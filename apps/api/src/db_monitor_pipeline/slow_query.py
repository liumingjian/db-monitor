"""MySQL slow query collection domain, cursor store, sink wiring, worker.

Implements ADR-0007: worker increments `last_event_id` per instance and
incrementally pulls rows from
`performance_schema.events_statements_history_long` that exceed the
per-instance `slow_threshold_seconds` (ADR-0011 D3). Results are
persisted to ClickHouse `mysql_slow_query_events` (7 day TTL).

Debug-First Policy: collection failures surface explicitly; there is no
silent swallow, no mock success, no cursor roll-back on failure other
than not-advancing so the next cycle retries the same window.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

import pymysql

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    InstanceConnectionConfig,
    MonitoredInstance,
)

SLOW_QUERY_COLLECT_INTERVAL_SECONDS = 60
SLOW_QUERY_THRESHOLD_PARAMETER_KEY = "slow_threshold_seconds"
DEFAULT_SLOW_THRESHOLD_SECONDS = 1.0
MIN_SLOW_THRESHOLD_SECONDS = 0.1
MYSQL_SLOW_QUERY_TIMEOUT_SECONDS = 5
MYSQL_SLOW_QUERY_FETCH_LIMIT = 1000
PICOSECONDS_PER_SECOND = 1_000_000_000_000.0
PICOSECONDS_PER_MILLISECOND = 1_000_000_000.0
REDIS_CURSOR_KEY_PREFIX = "mysql:slowq:last_event_id"

_SLOW_QUERY_SELECT_SQL = (
    "SELECT e.EVENT_ID, e.THREAD_ID, e.CURRENT_SCHEMA, e.DIGEST, "
    "e.DIGEST_TEXT, e.SQL_TEXT, e.TIMER_WAIT, e.ROWS_EXAMINED, e.ROWS_SENT, "
    "e.ROWS_AFFECTED, e.ERRORS, t.PROCESSLIST_USER AS USER, "
    "t.PROCESSLIST_HOST AS HOST "
    "FROM performance_schema.events_statements_history_long AS e "
    "LEFT JOIN performance_schema.threads AS t ON t.THREAD_ID = e.THREAD_ID "
    "WHERE e.EVENT_ID > %s AND e.TIMER_WAIT >= %s "
    "ORDER BY e.EVENT_ID ASC LIMIT %s"
)
_SLOW_QUERY_MAX_EVENT_ID_SQL = (
    "SELECT COALESCE(MAX(EVENT_ID), 0) AS max_event_id "
    "FROM performance_schema.events_statements_history_long"
)


@dataclass(frozen=True)
class SlowQueryEvent:
    event_id: int
    thread_id: int
    user: str
    host: str
    schema_name: str
    digest: str
    digest_text: str
    sql_text: str
    timer_wait_ms: float
    rows_examined: int
    rows_sent: int
    rows_affected: int
    errors: int
    started_at: datetime


@dataclass(frozen=True)
class SlowQuerySnapshot:
    collected_at: datetime
    events: tuple[SlowQueryEvent, ...]
    instance_id: str
    organization_id: str
    last_event_id: int


class SlowQueryCollector(Protocol):
    def collect(
        self,
        *,
        connection: InstanceConnectionConfig,
        last_event_id: int,
        slow_threshold_seconds: float,
    ) -> tuple[SlowQueryEvent, ...]:
        ...

    def probe_max_event_id(self, connection: InstanceConnectionConfig) -> int:
        ...


class SlowQuerySink(Protocol):
    def write_slow_queries(self, snapshot: SlowQuerySnapshot) -> None:
        ...


class SlowQueryCursorStore(Protocol):
    def get(self, instance_id: str) -> int | None:
        ...

    def set(self, instance_id: str, last_event_id: int) -> None:
        ...


class InMemorySlowQueryCursorStore:
    def __init__(self, *, cursors: Mapping[str, int] | None = None) -> None:
        self._cursors: dict[str, int] = dict(cursors or {})

    def get(self, instance_id: str) -> int | None:
        return self._cursors.get(instance_id)

    def set(self, instance_id: str, last_event_id: int) -> None:
        self._cursors[instance_id] = last_event_id


class RedisSlowQueryCursorStore:
    """Redis-backed cursor store keyed by instance (ADR-0007)."""

    def __init__(self, *, redis_url: str) -> None:
        import redis

        self._client = redis.Redis.from_url(redis_url, decode_responses=True)

    def get(self, instance_id: str) -> int | None:
        raw_value = self._client.get(_cursor_key(instance_id))
        if raw_value is None:
            return None
        return int(str(raw_value))

    def set(self, instance_id: str, last_event_id: int) -> None:
        self._client.set(_cursor_key(instance_id), str(last_event_id))


def _cursor_key(instance_id: str) -> str:
    return f"{REDIS_CURSOR_KEY_PREFIX}:{instance_id}"


class PyMySQLSlowQueryCollector:
    def __init__(
        self,
        *,
        fetch_limit: int = MYSQL_SLOW_QUERY_FETCH_LIMIT,
        timeout_seconds: int = MYSQL_SLOW_QUERY_TIMEOUT_SECONDS,
    ) -> None:
        self._fetch_limit = fetch_limit
        self._timeout_seconds = timeout_seconds

    def collect(
        self,
        *,
        connection: InstanceConnectionConfig,
        last_event_id: int,
        slow_threshold_seconds: float,
    ) -> tuple[SlowQueryEvent, ...]:
        threshold_picoseconds = int(slow_threshold_seconds * PICOSECONDS_PER_SECOND)
        rows = self._run_query(
            connection=connection,
            params=(last_event_id, threshold_picoseconds, self._fetch_limit),
            sql=_SLOW_QUERY_SELECT_SQL,
        )
        return tuple(_row_to_event(row) for row in rows)

    def probe_max_event_id(self, connection: InstanceConnectionConfig) -> int:
        rows = self._run_query(
            connection=connection,
            params=(),
            sql=_SLOW_QUERY_MAX_EVENT_ID_SQL,
        )
        if not rows:
            return 0
        return int(rows[0].get("max_event_id") or 0)

    def _run_query(
        self,
        *,
        connection: InstanceConnectionConfig,
        params: tuple[object, ...],
        sql: str,
    ) -> list[Mapping[str, Any]]:
        with pymysql.connect(
            host=connection.host,
            port=connection.port,
            user=connection.username,
            password=connection.password,
            database=connection.database,
            connect_timeout=self._timeout_seconds,
            read_timeout=self._timeout_seconds,
            write_timeout=self._timeout_seconds,
            cursorclass=pymysql.cursors.DictCursor,
        ) as mysql_connection:
            with mysql_connection.cursor() as cursor:
                cursor.execute(sql, params)
                return list(cursor.fetchall())


@dataclass(frozen=True)
class SlowQueryWorker:
    """Atomic collect-and-write unit for one instance.

    Responsibilities:
    - Resolve the cursor (first run -> align to `probe_max_event_id`, no backfill).
    - Pull events from performance_schema via the collector.
    - Persist them to the sink.
    - Advance the cursor only after a successful write.
    """

    collector: SlowQueryCollector
    cursor_store: SlowQueryCursorStore
    sink: SlowQuerySink

    def collect_once(
        self,
        *,
        instance: MonitoredInstance,
        slow_threshold_seconds: float,
    ) -> SlowQuerySnapshot:
        cursor = self._resolve_cursor(instance)
        events = self.collector.collect(
            connection=instance.connection,
            last_event_id=cursor,
            slow_threshold_seconds=slow_threshold_seconds,
        )
        next_cursor = events[-1].event_id if events else cursor
        snapshot = SlowQuerySnapshot(
            collected_at=utc_now(),
            events=events,
            instance_id=instance.instance_id,
            organization_id=instance.organization_id,
            last_event_id=next_cursor,
        )
        self.sink.write_slow_queries(snapshot)
        if events:
            self.cursor_store.set(instance.instance_id, next_cursor)
        return snapshot

    def _resolve_cursor(self, instance: MonitoredInstance) -> int:
        existing = self.cursor_store.get(instance.instance_id)
        if existing is not None:
            return existing
        aligned = self.collector.probe_max_event_id(instance.connection)
        self.cursor_store.set(instance.instance_id, aligned)
        return aligned


class InstanceParameterReader(Protocol):
    def get_parameters(self, instance_id: str) -> Mapping[str, Any]:
        ...


def resolve_slow_threshold_seconds(
    *,
    instance_id: str,
    reader: InstanceParameterReader,
) -> float:
    parameters = reader.get_parameters(instance_id)
    raw_value = parameters.get(SLOW_QUERY_THRESHOLD_PARAMETER_KEY)
    if raw_value is None:
        return DEFAULT_SLOW_THRESHOLD_SECONDS
    parsed = float(raw_value)
    if parsed < MIN_SLOW_THRESHOLD_SECONDS:
        raise RuntimeError(
            f"slow_threshold_seconds={parsed} violates minimum "
            f"{MIN_SLOW_THRESHOLD_SECONDS}s (ADR-0007)."
        )
    return parsed


def _row_to_event(row: Mapping[str, Any]) -> SlowQueryEvent:
    timer_wait_picoseconds = int(row.get("TIMER_WAIT") or 0)
    started_at = _resolve_started_at(row)
    return SlowQueryEvent(
        event_id=int(_as_str(_require(row, "EVENT_ID"))),
        thread_id=int(row.get("THREAD_ID") or 0),
        user=_as_str(row.get("USER")),
        host=_as_str(row.get("HOST")),
        schema_name=_as_str(row.get("CURRENT_SCHEMA")),
        digest=_as_str(row.get("DIGEST")),
        digest_text=_as_str(row.get("DIGEST_TEXT")),
        sql_text=_as_str(row.get("SQL_TEXT")),
        timer_wait_ms=timer_wait_picoseconds / PICOSECONDS_PER_MILLISECOND,
        rows_examined=int(row.get("ROWS_EXAMINED") or 0),
        rows_sent=int(row.get("ROWS_SENT") or 0),
        rows_affected=int(row.get("ROWS_AFFECTED") or 0),
        errors=int(row.get("ERRORS") or 0),
        started_at=started_at,
    )


def _resolve_started_at(row: Mapping[str, Any]) -> datetime:
    raw = row.get("STARTED_AT") or row.get("started_at")
    if isinstance(raw, datetime):
        return raw if raw.tzinfo is not None else raw.replace(tzinfo=UTC)
    if isinstance(raw, str) and raw:
        parsed = datetime.fromisoformat(raw)
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
    # performance_schema does not expose a direct SQL timestamp for the
    # event; approximating via collected_at keeps the timeline monotonic
    # on UI. We align to utc_now() at row conversion time.
    return utc_now()


def _require(row: Mapping[str, Any], key: str) -> object:
    if key not in row:
        raise RuntimeError(f"slow query row missing required column: {key}")
    return row[key]


def _as_str(value: object) -> str:
    return "" if value is None else str(value)


def slow_query_snapshot_to_clickhouse_rows(
    snapshot: SlowQuerySnapshot,
) -> Sequence[Mapping[str, object]]:
    return tuple(_event_to_row(snapshot, event) for event in snapshot.events)


def _event_to_row(
    snapshot: SlowQuerySnapshot,
    event: SlowQueryEvent,
) -> Mapping[str, object]:
    return {
        "organization_id": snapshot.organization_id,
        "instance_id": snapshot.instance_id,
        "collected_at": _format_clickhouse_datetime(snapshot.collected_at),
        "event_id": event.event_id,
        "thread_id": event.thread_id,
        "user": event.user,
        "host": event.host,
        "schema_name": event.schema_name,
        "digest": event.digest,
        "digest_text": event.digest_text,
        "sql_text": event.sql_text,
        "timer_wait_ms": event.timer_wait_ms,
        "rows_examined": event.rows_examined,
        "rows_sent": event.rows_sent,
        "rows_affected": event.rows_affected,
        "errors": event.errors,
        "started_at": _format_clickhouse_datetime(event.started_at),
    }


def _format_clickhouse_datetime(value: datetime) -> str:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
