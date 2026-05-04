"""MySQL processlist collection domain, snapshot sink, and worker.

Implements the data-plane side of ADR-0005 (展示走采集，命令走实时):
`SHOW PROCESSLIST` is snapshotted on a per-instance cadence, the full
result set (including `COMMAND='Sleep'`) is persisted to ClickHouse
`mysql_processlist`, and the HTTP API reads from ClickHouse.

Per-instance cadence comes from `instance_parameters.parameters->>
'processlist_interval_seconds'` (ADR-0011 D3); the caller is responsible
for throttling. This module only exposes atomic `collect_once`
semantics so failures surface explicitly (no silent retries / fake
success) per Debug-First Policy.
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

PROCESSLIST_QUERY = "SHOW FULL PROCESSLIST"
DEFAULT_PROCESSLIST_INTERVAL_SECONDS = 30
MIN_PROCESSLIST_INTERVAL_SECONDS = 10
PROCESSLIST_INTERVAL_PARAMETER_KEY = "processlist_interval_seconds"
MYSQL_PROCESSLIST_TIMEOUT_SECONDS = 5


@dataclass(frozen=True)
class ProcesslistEntry:
    process_id: int
    user: str
    host: str
    db: str
    command: str
    time_seconds: int
    state: str
    info: str
    trx_started_at: datetime | None


@dataclass(frozen=True)
class ProcesslistSnapshot:
    collected_at: datetime
    entries: tuple[ProcesslistEntry, ...]
    instance_id: str
    organization_id: str


class ProcesslistCollector(Protocol):
    def collect(self, connection: InstanceConnectionConfig) -> tuple[ProcesslistEntry, ...]:
        ...


class ProcesslistSink(Protocol):
    def write_processlist(self, snapshot: ProcesslistSnapshot) -> None:
        ...


class InstanceParameterReader(Protocol):
    def get_parameters(self, instance_id: str) -> Mapping[str, Any]:
        ...


class PyMySQLProcesslistCollector:
    def __init__(self, *, timeout_seconds: int = MYSQL_PROCESSLIST_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def collect(self, connection: InstanceConnectionConfig) -> tuple[ProcesslistEntry, ...]:
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
                cursor.execute(PROCESSLIST_QUERY)
                rows = cursor.fetchall()
        return tuple(_row_to_entry(row) for row in rows)


@dataclass(frozen=True)
class ProcesslistWorker:
    """Atomic collect-and-write unit; raises on failure (no silent swallow)."""

    collector: ProcesslistCollector
    sink: ProcesslistSink

    def collect_once(self, instance: MonitoredInstance) -> ProcesslistSnapshot:
        entries = self.collector.collect(instance.connection)
        snapshot = ProcesslistSnapshot(
            collected_at=utc_now(),
            entries=entries,
            instance_id=instance.instance_id,
            organization_id=instance.organization_id,
        )
        self.sink.write_processlist(snapshot)
        return snapshot


def resolve_processlist_interval_seconds(
    *,
    instance_id: str,
    reader: InstanceParameterReader,
) -> int:
    parameters = reader.get_parameters(instance_id)
    raw_value = parameters.get(PROCESSLIST_INTERVAL_PARAMETER_KEY)
    if raw_value is None:
        return DEFAULT_PROCESSLIST_INTERVAL_SECONDS
    parsed = int(raw_value)
    if parsed < MIN_PROCESSLIST_INTERVAL_SECONDS:
        raise RuntimeError(
            f"processlist_interval_seconds={parsed} violates minimum "
            f"{MIN_PROCESSLIST_INTERVAL_SECONDS}s (ADR-0005)."
        )
    return parsed


def _row_to_entry(row: Mapping[str, object]) -> ProcesslistEntry:
    return ProcesslistEntry(
        process_id=int(_as_str(_require(row, "Id"))),
        user=_as_str(row.get("User")),
        host=_as_str(row.get("Host")),
        db=_as_str(row.get("db")),
        command=_as_str(row.get("Command")),
        time_seconds=int(_as_str(row.get("Time")) or 0),
        state=_as_str(row.get("State")),
        info=_as_str(row.get("Info")),
        trx_started_at=_as_datetime(row.get("Trx_started")),
    )


def _require(row: Mapping[str, object], key: str) -> object:
    if key not in row:
        raise RuntimeError(f"SHOW PROCESSLIST row missing required column: {key}")
    return row[key]


def _as_str(value: object) -> str:
    return "" if value is None else str(value)


def _as_datetime(value: object) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def snapshot_to_clickhouse_rows(
    snapshot: ProcesslistSnapshot,
) -> Sequence[Mapping[str, object]]:
    return tuple(_entry_to_row(snapshot, entry) for entry in snapshot.entries)


def _entry_to_row(
    snapshot: ProcesslistSnapshot,
    entry: ProcesslistEntry,
) -> Mapping[str, object]:
    return {
        "organization_id": snapshot.organization_id,
        "instance_id": snapshot.instance_id,
        "collected_at": _format_clickhouse_datetime(snapshot.collected_at),
        "process_id": entry.process_id,
        "user": entry.user,
        "host": entry.host,
        "db": entry.db,
        "command": entry.command,
        "time_seconds": entry.time_seconds,
        "state": entry.state,
        "info": entry.info,
        "trx_started_at": (
            None
            if entry.trx_started_at is None
            else _format_clickhouse_datetime(entry.trx_started_at)
        ),
    }


def _format_clickhouse_datetime(value: datetime) -> str:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
