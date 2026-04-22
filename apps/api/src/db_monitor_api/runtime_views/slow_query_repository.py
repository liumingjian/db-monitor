"""Slow query ClickHouse read paths (ADR-0007)."""

from collections.abc import Iterable
from datetime import UTC, datetime
import json
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from db_monitor_api.runtime_views.slow_query_domain import (
    DEFAULT_SLOW_QUERY_LIMIT,
    MAX_SLOW_QUERY_LIMIT,
    SlowQueryEntryRow,
    SlowQueryQuery,
    SlowQuerySnapshotView,
    SlowQueryWindow,
)
from db_monitor_pipeline.sink import CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE


class SlowQueryRepository(Protocol):
    def fetch_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: SlowQueryQuery,
        window: SlowQueryWindow,
    ) -> SlowQuerySnapshotView:
        ...


class InMemorySlowQueryRepository:
    def __init__(
        self,
        *,
        entries: Iterable[tuple[str, str, SlowQueryEntryRow]] = (),
    ) -> None:
        self._entries: list[tuple[str, str, SlowQueryEntryRow]] = list(entries)

    def add(
        self,
        *,
        instance_id: str,
        organization_id: str,
        entry: SlowQueryEntryRow,
    ) -> None:
        self._entries.append((organization_id, instance_id, entry))

    def fetch_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: SlowQueryQuery,
        window: SlowQueryWindow,
    ) -> SlowQuerySnapshotView:
        matched = tuple(
            entry
            for entry_org, entry_instance, entry in self._entries
            if entry_org == organization_id
            and entry_instance == instance_id
            and _within_window(entry, query=query, window=window)
        )
        sorted_entries = sorted(matched, key=lambda item: item.timer_wait_ms, reverse=True)
        limit = _clamp_limit(query.limit)
        return SlowQuerySnapshotView(
            window=window,
            entries=tuple(sorted_entries[:limit]),
        )


class ClickHouseSlowQueryRepository:
    def __init__(
        self,
        *,
        database: str,
        endpoint: str,
        password: str,
        username: str,
    ) -> None:
        self._database = database
        self._endpoint = endpoint.rstrip("/")
        self._password = password
        self._username = username

    def fetch_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: SlowQueryQuery,
        window: SlowQueryWindow,
    ) -> SlowQuerySnapshotView:
        sql = _build_select_sql(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
            window=window,
        )
        rows = self._run_query(sql)
        entries = tuple(_row_to_entry(row) for row in rows)
        return SlowQuerySnapshotView(window=window, entries=entries)

    def _run_query(self, sql: str) -> list[dict[str, object]]:
        request = Request(
            url=(
                f"{self._endpoint}/?"
                f"{urlencode({'database': self._database, 'query': sql})}"
            ),
            data=b"",
            headers={
                "X-ClickHouse-User": self._username,
                "X-ClickHouse-Key": self._password,
            },
            method="POST",
        )
        with urlopen(request) as response:
            body = response.read().decode("utf-8")
        return [json.loads(line) for line in body.splitlines() if line]


def _build_select_sql(
    *,
    instance_id: str,
    organization_id: str,
    query: SlowQueryQuery,
    window: SlowQueryWindow,
) -> str:
    filters = [
        f"organization_id = {_quote(organization_id)}",
        f"instance_id = {_quote(instance_id)}",
        f"started_at >= '{_format_datetime(window.from_at)}'",
        f"started_at <= '{_format_datetime(window.to_at)}'",
    ]
    if query.min_duration_ms is not None:
        filters.append(f"timer_wait_ms >= {float(query.min_duration_ms)}")
    if query.user is not None:
        filters.append(f"user = {_quote(query.user)}")
    if query.schema_name is not None:
        filters.append(f"schema_name = {_quote(query.schema_name)}")
    if query.digest_prefix is not None:
        filters.append(
            f"startsWith(digest, {_quote(query.digest_prefix)})"
        )
    if query.started_after is not None:
        filters.append(f"started_at >= '{_format_datetime(query.started_after)}'")
    if query.started_before is not None:
        filters.append(f"started_at <= '{_format_datetime(query.started_before)}'")
    limit = _clamp_limit(query.limit)
    return (
        "SELECT event_id, started_at, user, schema_name, sql_text, digest, "
        "timer_wait_ms, rows_examined, rows_sent, rows_affected, errors "
        f"FROM {CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE} "
        f"WHERE {' AND '.join(filters)} "
        f"ORDER BY timer_wait_ms DESC, event_id ASC "
        f"LIMIT {limit} FORMAT JSONEachRow"
    )


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return DEFAULT_SLOW_QUERY_LIMIT
    return min(limit, MAX_SLOW_QUERY_LIMIT)


def _within_window(
    entry: SlowQueryEntryRow,
    *,
    query: SlowQueryQuery,
    window: SlowQueryWindow,
) -> bool:
    if entry.started_at < window.from_at or entry.started_at > window.to_at:
        return False
    if query.min_duration_ms is not None and entry.timer_wait_ms < query.min_duration_ms:
        return False
    if query.user is not None and entry.user != query.user:
        return False
    if query.schema_name is not None and entry.schema_name != query.schema_name:
        return False
    if query.digest_prefix is not None and not entry.digest.startswith(query.digest_prefix):
        return False
    if query.started_after is not None and entry.started_at < query.started_after:
        return False
    if query.started_before is not None and entry.started_at > query.started_before:
        return False
    return True


def _row_to_entry(row: dict[str, object]) -> SlowQueryEntryRow:
    return SlowQueryEntryRow(
        event_id=int(str(row["event_id"])),
        started_at=_parse_datetime(str(row["started_at"])),
        user=str(row.get("user", "")),
        schema_name=str(row.get("schema_name", "")),
        sql_text=str(row.get("sql_text", "")),
        digest=str(row.get("digest", "")),
        timer_wait_ms=float(str(row.get("timer_wait_ms", 0))),
        rows_examined=int(str(row.get("rows_examined", 0))),
        rows_sent=int(str(row.get("rows_sent", 0))),
        rows_affected=int(str(row.get("rows_affected", 0))),
        errors=int(str(row.get("errors", 0))),
    )


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def _format_datetime(value: datetime) -> str:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
