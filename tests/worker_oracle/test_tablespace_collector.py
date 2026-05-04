"""Unit tests for Oracle tablespace collector/worker (child #4)."""

import pytest

from db_monitor_api.control_plane.domain import InstanceConnectionConfig
from db_monitor_pipeline.sink import InMemoryMetricSink
from db_monitor_pipeline.tablespace import (
    PyOracleTablespaceCollector,
    TablespaceWorker,
    snapshot_to_clickhouse_rows,
)

from tests.worker_oracle._tablespace_fixtures import (
    StaticCollector,
    oracle_instance,
    tablespace_entry,
)


def test_worker_writes_tablespace_snapshot_to_sink() -> None:
    sink = InMemoryMetricSink()
    worker = TablespaceWorker(
        collector=StaticCollector(
            (tablespace_entry(), tablespace_entry(name="USERS", used_rate_percent=97.0))
        ),
        sink=sink,
    )

    snapshot = worker.collect_once(oracle_instance())

    assert len(sink.tablespace_snapshots) == 1
    assert len(snapshot.entries) == 2
    assert snapshot.entries[1].tablespace_name == "USERS"
    assert snapshot.instance_id == "inst-oracle"
    assert snapshot.organization_id == "org-internal"


def test_collect_with_driver_normalizes_blocks_to_bytes() -> None:
    class FakeCursor:
        def __init__(self) -> None:
            self._rows: list[tuple[object, ...]] = []
            self.queries: list[str] = []

        def execute(self, query: str) -> None:
            self.queries.append(query)
            if "dba_tablespace_usage_metrics" in query:
                self._rows = [
                    ("SYSAUX", 10, 40, 25.0, "ONLINE", 8192),
                    ("USERS", 3, 4, 75.0, "OFFLINE", 8192),
                ]
            elif "dba_data_files" in query:
                self._rows = [("SYSAUX", 1), ("USERS", 0)]
            else:
                raise AssertionError(f"Unexpected query: {query}")

        def fetchall(self) -> list[tuple[object, ...]]:
            return list(self._rows)

        def close(self) -> None:
            return None

    class FakeConnection:
        def __init__(self) -> None:
            self.closed = False

        def cursor(self) -> FakeCursor:
            return FakeCursor()

        def close(self) -> None:
            self.closed = True

    from types import ModuleType

    driver = ModuleType("oracledb")
    driver.connect = lambda **kwargs: FakeConnection()  # type: ignore[attr-defined]

    from db_monitor_pipeline import tablespace as tablespace_module

    entries = tablespace_module._collect_with_driver(
        connection=InstanceConnectionConfig(
            database="XE",
            host="127.0.0.1",
            password="pw",
            port=1521,
            username="system",
        ),
        driver=driver,
        timeout_seconds=5,
    )

    assert len(entries) == 2
    sysaux = entries[0]
    assert sysaux.used_bytes == 10 * 8192
    assert sysaux.total_bytes == 40 * 8192
    assert sysaux.autoextensible is True
    users = entries[1]
    assert users.autoextensible is False
    assert users.status == "OFFLINE"


def test_snapshot_rows_serialize_expected_columns() -> None:
    worker = TablespaceWorker(
        collector=StaticCollector((tablespace_entry(),)),
        sink=InMemoryMetricSink(),
    )
    snapshot = worker.collect_once(oracle_instance())

    rows = snapshot_to_clickhouse_rows(snapshot)

    assert len(rows) == 1
    row = rows[0]
    assert row["organization_id"] == "org-internal"
    assert row["instance_id"] == "inst-oracle"
    assert row["tablespace_name"] == "SYSAUX"
    assert row["autoextensible"] == 1
    assert row["used_bytes"] == 1024
    assert "collected_at" in row


def test_pyoracle_collector_raises_when_driver_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "db_monitor_pipeline.tablespace._load_oracle_driver",
        lambda: None,
    )
    with pytest.raises(RuntimeError, match="python-oracledb"):
        PyOracleTablespaceCollector().collect(
            InstanceConnectionConfig(
                database="XE",
                host="127.0.0.1",
                password="pw",
                port=1521,
                username="system",
            )
        )
