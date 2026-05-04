"""Oracle tablespace collection domain, snapshot sink, and worker.

Implements the Epic 15 Slice 1 child #4 data-plane surface (ADR-0008 +
ADR-0011 D1 sub-route): `dba_tablespace_usage_metrics` joined with
`dba_tablespaces` is snapshotted on a per-instance 300s cadence and the
full row set (including OFFLINE tablespaces) is persisted to ClickHouse
`oracle_tablespaces`. The HTTP API reads from ClickHouse, never from
Oracle directly.

Debug-First Policy: collection/sink failures surface explicitly via
exceptions; there is no silent retry, no swallow, and no mock-success
path. The scheduler maps exceptions to `WorkerRunResult.status="failed"`
per instance so the worker entry point can exit non-zero.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from types import ModuleType
from typing import Protocol

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    InstanceConnectionConfig,
    MonitoredInstance,
)
from db_monitor_api.control_plane.oracle_validation import (
    DEFAULT_ORACLE_TIMEOUT_SECONDS,
    _build_oracle_dsn,
    _load_oracle_driver,
)

DEFAULT_TABLESPACE_INTERVAL_SECONDS = 300
MIN_TABLESPACE_INTERVAL_SECONDS = 60
TABLESPACE_INTERVAL_PARAMETER_KEY = "tablespace_interval_seconds"
TABLESPACE_USAGE_QUERY = (
    "SELECT m.tablespace_name, m.used_space, m.tablespace_size, "
    "m.used_percent, t.status, t.block_size "
    "FROM dba_tablespace_usage_metrics m "
    "JOIN dba_tablespaces t ON t.tablespace_name = m.tablespace_name"
)
TABLESPACE_AUTOEXTEND_QUERY = (
    "SELECT tablespace_name, MAX(CASE WHEN autoextensible = 'YES' THEN 1 ELSE 0 END) "
    "FROM dba_data_files GROUP BY tablespace_name"
)


@dataclass(frozen=True)
class TablespaceEntry:
    tablespace_name: str
    status: str
    used_bytes: int
    total_bytes: int
    used_rate_percent: float
    autoextensible: bool


@dataclass(frozen=True)
class TablespaceSnapshot:
    collected_at: datetime
    entries: tuple[TablespaceEntry, ...]
    instance_id: str
    organization_id: str


class TablespaceCollector(Protocol):
    def collect(self, connection: InstanceConnectionConfig) -> tuple[TablespaceEntry, ...]:
        ...


class TablespaceSink(Protocol):
    def write_tablespaces(self, snapshot: TablespaceSnapshot) -> None:
        ...


class InstanceParameterReader(Protocol):
    def get_parameters(self, instance_id: str) -> Mapping[str, object]:
        ...


class PyOracleTablespaceCollector:
    """Oracle tablespace collector using python-oracledb / cx_Oracle.

    Debug-First: when the driver is unavailable we raise explicitly.
    There is no sqlplus fallback here — Oracle tablespace collection is
    production-only and only runs in environments where the driver is
    present (validated upstream by `OracleConnectionValidator`).
    """

    def __init__(self, *, timeout_seconds: int = DEFAULT_ORACLE_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def collect(self, connection: InstanceConnectionConfig) -> tuple[TablespaceEntry, ...]:
        driver = _load_oracle_driver()
        if driver is None:
            raise RuntimeError(
                "Oracle tablespace collection requires the python-oracledb or "
                "cx_Oracle package."
            )
        return _collect_with_driver(
            connection=connection,
            driver=driver,
            timeout_seconds=self._timeout_seconds,
        )


@dataclass(frozen=True)
class TablespaceWorker:
    """Atomic collect-and-write unit; raises on failure (no silent swallow)."""

    collector: TablespaceCollector
    sink: TablespaceSink

    def collect_once(self, instance: MonitoredInstance) -> TablespaceSnapshot:
        entries = self.collector.collect(instance.connection)
        snapshot = TablespaceSnapshot(
            collected_at=utc_now(),
            entries=entries,
            instance_id=instance.instance_id,
            organization_id=instance.organization_id,
        )
        self.sink.write_tablespaces(snapshot)
        return snapshot


def resolve_tablespace_interval_seconds(
    *,
    instance_id: str,
    reader: InstanceParameterReader,
) -> int:
    parameters = reader.get_parameters(instance_id)
    raw_value = parameters.get(TABLESPACE_INTERVAL_PARAMETER_KEY)
    if raw_value is None:
        return DEFAULT_TABLESPACE_INTERVAL_SECONDS
    parsed = int(str(raw_value))
    if parsed < MIN_TABLESPACE_INTERVAL_SECONDS:
        raise RuntimeError(
            f"tablespace_interval_seconds={parsed} violates minimum "
            f"{MIN_TABLESPACE_INTERVAL_SECONDS}s."
        )
    return parsed


def snapshot_to_clickhouse_rows(
    snapshot: TablespaceSnapshot,
) -> Sequence[Mapping[str, object]]:
    return tuple(_entry_to_row(snapshot, entry) for entry in snapshot.entries)


def _collect_with_driver(
    *,
    connection: InstanceConnectionConfig,
    driver: ModuleType,
    timeout_seconds: int,
) -> tuple[TablespaceEntry, ...]:
    connect_kwargs: dict[str, object] = {
        "user": connection.username,
        "password": connection.password,
        "dsn": _build_oracle_dsn(driver, connection),
    }
    if getattr(driver, "__name__", "") == "oracledb":
        connect_kwargs["tcp_connect_timeout"] = timeout_seconds
    db_connection = None
    cursor = None
    try:
        db_connection = driver.connect(**connect_kwargs)
        cursor = db_connection.cursor()
        usage_rows = _fetch_rows(cursor, TABLESPACE_USAGE_QUERY)
        autoextend_rows = _fetch_rows(cursor, TABLESPACE_AUTOEXTEND_QUERY)
    finally:
        if cursor is not None:
            cursor.close()
        if db_connection is not None:
            db_connection.close()
    return _rows_to_entries(usage_rows=usage_rows, autoextend_rows=autoextend_rows)


def _fetch_rows(cursor: object, query: str) -> tuple[tuple[object, ...], ...]:
    execute = getattr(cursor, "execute")
    fetchall = getattr(cursor, "fetchall")
    execute(query)
    return tuple(tuple(row) for row in fetchall())


def _rows_to_entries(
    *,
    usage_rows: tuple[tuple[object, ...], ...],
    autoextend_rows: tuple[tuple[object, ...], ...],
) -> tuple[TablespaceEntry, ...]:
    autoextend_by_name = {str(row[0]): int(str(row[1])) == 1 for row in autoextend_rows}
    entries = tuple(
        _build_entry(row=row, autoextend_by_name=autoextend_by_name) for row in usage_rows
    )
    return entries


def _build_entry(
    *,
    row: tuple[object, ...],
    autoextend_by_name: Mapping[str, bool],
) -> TablespaceEntry:
    name = str(row[0])
    used_blocks = int(str(row[1]))
    total_blocks = int(str(row[2]))
    used_percent = float(str(row[3]))
    status = str(row[4])
    block_size = int(str(row[5]))
    return TablespaceEntry(
        tablespace_name=name,
        status=status,
        used_bytes=used_blocks * block_size,
        total_bytes=total_blocks * block_size,
        used_rate_percent=used_percent,
        autoextensible=autoextend_by_name.get(name, False),
    )


def _entry_to_row(
    snapshot: TablespaceSnapshot,
    entry: TablespaceEntry,
) -> Mapping[str, object]:
    return {
        "organization_id": snapshot.organization_id,
        "instance_id": snapshot.instance_id,
        "collected_at": _format_clickhouse_datetime(snapshot.collected_at),
        "tablespace_name": entry.tablespace_name,
        "status": entry.status,
        "used_bytes": entry.used_bytes,
        "total_bytes": entry.total_bytes,
        "used_rate_percent": entry.used_rate_percent,
        "autoextensible": 1 if entry.autoextensible else 0,
    }


def _format_clickhouse_datetime(value: datetime) -> str:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
