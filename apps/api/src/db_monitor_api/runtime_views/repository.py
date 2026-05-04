"""Processlist ClickHouse read paths.

Reads from the `mysql_processlist` dedicated table created by
`bootstrap_clickhouse_schema()` (ADR-0005 / ADR-0008). Query shape:

1. Resolve the `snapshot_at` (`MAX(collected_at)`) matching the optional
   time window and instance. If no snapshot exists -> return `None`.
2. Fetch all rows for that snapshot, applying field filters and `limit`
   at the database layer so the API never ships > 500 rows.
"""

from collections.abc import Iterable
from datetime import UTC, datetime
import json
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from db_monitor_api.runtime_views.domain import (
    DEFAULT_PROCESSLIST_LIMIT,
    MAX_PROCESSLIST_LIMIT,
    ProcesslistEntryRow,
    ProcesslistQuery,
    ProcesslistSnapshotView,
)
from db_monitor_pipeline.sink import CLICKHOUSE_MYSQL_PROCESSLIST_TABLE


class ProcesslistRepository(Protocol):
    def fetch_latest_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: ProcesslistQuery,
    ) -> ProcesslistSnapshotView | None:
        ...


class InMemoryProcesslistRepository:
    def __init__(
        self,
        *,
        snapshots: Iterable[tuple[str, str, ProcesslistSnapshotView]] = (),
    ) -> None:
        self._snapshots: list[tuple[str, str, ProcesslistSnapshotView]] = list(snapshots)

    def add_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        snapshot: ProcesslistSnapshotView,
    ) -> None:
        self._snapshots.append((organization_id, instance_id, snapshot))

    def fetch_latest_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: ProcesslistQuery,
    ) -> ProcesslistSnapshotView | None:
        matched = tuple(
            snapshot
            for snapshot_org, snapshot_instance, snapshot in self._snapshots
            if snapshot_org == organization_id
            and snapshot_instance == instance_id
            and _within_window(snapshot.collected_at, query)
        )
        if not matched:
            return None
        snapshot = max(matched, key=lambda item: item.collected_at)
        filtered = tuple(
            entry
            for entry in snapshot.entries
            if _entry_matches(entry, query)
        )
        limit = _clamp_limit(query.limit)
        return ProcesslistSnapshotView(
            collected_at=snapshot.collected_at,
            entries=filtered[:limit],
        )


class ClickHouseProcesslistRepository:
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

    def fetch_latest_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: ProcesslistQuery,
    ) -> ProcesslistSnapshotView | None:
        snapshot_at = self._fetch_snapshot_at(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
        )
        if snapshot_at is None:
            return None
        rows = self._fetch_rows(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
            snapshot_at=snapshot_at,
        )
        return ProcesslistSnapshotView(
            collected_at=snapshot_at,
            entries=tuple(_row_to_entry(row) for row in rows),
        )

    def _fetch_snapshot_at(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: ProcesslistQuery,
    ) -> datetime | None:
        filters = [
            f"organization_id = {_quote(organization_id)}",
            f"instance_id = {_quote(instance_id)}",
        ]
        if query.collected_after is not None:
            filters.append(f"collected_at >= '{_format_datetime(query.collected_after)}'")
        if query.collected_before is not None:
            filters.append(f"collected_at <= '{_format_datetime(query.collected_before)}'")
        sql = (
            "SELECT max(collected_at) AS snapshot_at "
            f"FROM {CLICKHOUSE_MYSQL_PROCESSLIST_TABLE} "
            f"WHERE {' AND '.join(filters)} FORMAT JSONEachRow"
        )
        rows = self._run_query(sql)
        if not rows:
            return None
        raw = rows[0].get("snapshot_at")
        if raw is None or raw == "" or raw == "1970-01-01 00:00:00.000":
            return None
        return _parse_datetime(str(raw))

    def _fetch_rows(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: ProcesslistQuery,
        snapshot_at: datetime,
    ) -> list[dict[str, object]]:
        filters = [
            f"organization_id = {_quote(organization_id)}",
            f"instance_id = {_quote(instance_id)}",
            f"collected_at = '{_format_datetime(snapshot_at)}'",
        ]
        if query.user is not None:
            filters.append(f"user = {_quote(query.user)}")
        if query.host is not None:
            filters.append(f"host = {_quote(query.host)}")
        if query.command is not None:
            filters.append(f"command = {_quote(query.command)}")
        if query.min_time_seconds is not None:
            filters.append(f"time_seconds >= {int(query.min_time_seconds)}")
        limit = _clamp_limit(query.limit)
        sql = (
            "SELECT process_id, user, host, db, command, time_seconds, state, info, trx_started_at "
            f"FROM {CLICKHOUSE_MYSQL_PROCESSLIST_TABLE} "
            f"WHERE {' AND '.join(filters)} "
            f"ORDER BY time_seconds DESC, process_id ASC "
            f"LIMIT {limit} FORMAT JSONEachRow"
        )
        return self._run_query(sql)

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


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return DEFAULT_PROCESSLIST_LIMIT
    return min(limit, MAX_PROCESSLIST_LIMIT)


def _within_window(when: datetime, query: ProcesslistQuery) -> bool:
    if query.collected_after is not None and when < query.collected_after:
        return False
    if query.collected_before is not None and when > query.collected_before:
        return False
    return True


def _entry_matches(entry: ProcesslistEntryRow, query: ProcesslistQuery) -> bool:
    if query.user is not None and entry.user != query.user:
        return False
    if query.host is not None and entry.host != query.host:
        return False
    if query.command is not None and entry.command != query.command:
        return False
    if (
        query.min_time_seconds is not None
        and entry.time_seconds < query.min_time_seconds
    ):
        return False
    return True


def _row_to_entry(row: dict[str, object]) -> ProcesslistEntryRow:
    raw_trx = row.get("trx_started_at")
    return ProcesslistEntryRow(
        process_id=int(str(row["process_id"])),
        user=str(row.get("user", "")),
        host=str(row.get("host", "")),
        db=str(row.get("db", "")),
        command=str(row.get("command", "")),
        time_seconds=int(str(row.get("time_seconds", 0))),
        state=str(row.get("state", "")),
        info=str(row.get("info", "")),
        trx_started_at=_parse_optional_datetime(raw_trx),
    )


def _parse_optional_datetime(value: object) -> datetime | None:
    if value is None or value == "":
        return None
    return _parse_datetime(str(value))


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def _format_datetime(value: datetime) -> str:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
