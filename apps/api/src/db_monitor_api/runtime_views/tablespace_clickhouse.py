"""ClickHouse-backed implementation of TablespaceRepository."""

from datetime import UTC, datetime
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from db_monitor_api.runtime_views.tablespace_domain import (
    HISTORY_HOURLY_DOWNSAMPLE_THRESHOLD_DAYS,
    TablespaceEntryRow,
    TablespaceHistoryPoint,
    TablespaceHistoryQuery,
    TablespaceHistoryView,
    TablespaceSnapshotQuery,
    TablespaceSnapshotView,
)
from db_monitor_pipeline.sink import CLICKHOUSE_ORACLE_TABLESPACES_TABLE


class ClickHouseTablespaceRepository:
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
        query: TablespaceSnapshotQuery,
    ) -> TablespaceSnapshotView | None:
        snapshot_at = self._fetch_snapshot_at(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
        )
        if snapshot_at is None:
            return None
        rows = self._fetch_snapshot_rows(
            instance_id=instance_id,
            organization_id=organization_id,
            snapshot_at=snapshot_at,
        )
        entries = tuple(_row_to_entry(row) for row in rows)
        return TablespaceSnapshotView(collected_at=snapshot_at, entries=entries)

    def fetch_history(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceHistoryQuery,
    ) -> TablespaceHistoryView:
        rows = self._fetch_history_rows(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
        )
        points = tuple(_row_to_history_point(row) for row in rows)
        return TablespaceHistoryView(entries=points)

    def _fetch_snapshot_at(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceSnapshotQuery,
    ) -> datetime | None:
        filters = _base_filters(instance_id=instance_id, organization_id=organization_id)
        if query.collected_after is not None:
            filters.append(f"collected_at >= '{_format_datetime(query.collected_after)}'")
        if query.collected_before is not None:
            filters.append(f"collected_at <= '{_format_datetime(query.collected_before)}'")
        sql = (
            "SELECT max(collected_at) AS snapshot_at "
            f"FROM {CLICKHOUSE_ORACLE_TABLESPACES_TABLE} "
            f"WHERE {' AND '.join(filters)} FORMAT JSONEachRow"
        )
        rows = self._run_query(sql)
        if not rows:
            return None
        raw = rows[0].get("snapshot_at")
        if raw is None or raw == "" or raw == "1970-01-01 00:00:00.000":
            return None
        return _parse_datetime(str(raw))

    def _fetch_snapshot_rows(
        self,
        *,
        instance_id: str,
        organization_id: str,
        snapshot_at: datetime,
    ) -> list[dict[str, object]]:
        filters = _base_filters(instance_id=instance_id, organization_id=organization_id)
        filters.append(f"collected_at = '{_format_datetime(snapshot_at)}'")
        sql = (
            "SELECT tablespace_name, status, used_bytes, total_bytes, "
            "used_rate_percent, autoextensible "
            f"FROM {CLICKHOUSE_ORACLE_TABLESPACES_TABLE} "
            f"WHERE {' AND '.join(filters)} "
            "ORDER BY used_rate_percent DESC, tablespace_name ASC "
            "FORMAT JSONEachRow"
        )
        return self._run_query(sql)

    def _fetch_history_rows(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceHistoryQuery,
    ) -> list[dict[str, object]]:
        filters = _base_filters(instance_id=instance_id, organization_id=organization_id)
        filters.append(f"tablespace_name = {_quote(query.tablespace_name)}")
        filters.append(f"collected_at >= '{_format_datetime(query.from_timestamp)}'")
        filters.append(f"collected_at <= '{_format_datetime(query.to_timestamp)}'")
        span_days = (query.to_timestamp - query.from_timestamp).total_seconds() / 86400
        sql = (
            _hourly_downsample_sql(filters)
            if span_days > HISTORY_HOURLY_DOWNSAMPLE_THRESHOLD_DAYS
            else _raw_history_sql(filters)
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


def _base_filters(*, instance_id: str, organization_id: str) -> list[str]:
    return [
        f"organization_id = {_quote(organization_id)}",
        f"instance_id = {_quote(instance_id)}",
    ]


def _raw_history_sql(filters: list[str]) -> str:
    return (
        "SELECT collected_at, used_bytes, total_bytes, used_rate_percent "
        f"FROM {CLICKHOUSE_ORACLE_TABLESPACES_TABLE} "
        f"WHERE {' AND '.join(filters)} "
        "ORDER BY collected_at ASC FORMAT JSONEachRow"
    )


def _hourly_downsample_sql(filters: list[str]) -> str:
    return (
        "SELECT toStartOfHour(collected_at) AS collected_at, "
        "toUInt64(avg(used_bytes)) AS used_bytes, "
        "toUInt64(avg(total_bytes)) AS total_bytes, "
        "avg(used_rate_percent) AS used_rate_percent "
        f"FROM {CLICKHOUSE_ORACLE_TABLESPACES_TABLE} "
        f"WHERE {' AND '.join(filters)} "
        "GROUP BY collected_at "
        "ORDER BY collected_at ASC FORMAT JSONEachRow"
    )


def _row_to_entry(row: dict[str, object]) -> TablespaceEntryRow:
    return TablespaceEntryRow(
        tablespace_name=str(row["tablespace_name"]),
        status=str(row.get("status", "")),
        used_bytes=int(str(row.get("used_bytes", 0))),
        total_bytes=int(str(row.get("total_bytes", 0))),
        used_rate_percent=float(str(row.get("used_rate_percent", 0))),
        autoextensible=int(str(row.get("autoextensible", 0))) == 1,
    )


def _row_to_history_point(row: dict[str, object]) -> TablespaceHistoryPoint:
    return TablespaceHistoryPoint(
        collected_at=_parse_datetime(str(row["collected_at"])),
        used_bytes=int(str(row.get("used_bytes", 0))),
        total_bytes=int(str(row.get("total_bytes", 0))),
        used_rate_percent=float(str(row.get("used_rate_percent", 0))),
    )


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def _format_datetime(value: datetime) -> str:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
