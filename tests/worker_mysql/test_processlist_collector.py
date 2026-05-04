from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any, Literal
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request

import json
import pytest

from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    InstanceConnectionConfig,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.instance_parameters import (
    InMemoryInstanceParameterRepository,
)
from db_monitor_pipeline.processlist import (
    DEFAULT_PROCESSLIST_INTERVAL_SECONDS,
    MIN_PROCESSLIST_INTERVAL_SECONDS,
    PROCESSLIST_INTERVAL_PARAMETER_KEY,
    ProcesslistCollector,
    ProcesslistEntry,
    ProcesslistSnapshot,
    ProcesslistWorker,
    resolve_processlist_interval_seconds,
    snapshot_to_clickhouse_rows,
)
from db_monitor_pipeline.sink import (
    CLICKHOUSE_MYSQL_PROCESSLIST_TABLE,
    ClickHouseMetricSink,
    InMemoryMetricSink,
)


class StaticProcesslistCollector(ProcesslistCollector):
    def __init__(self, entries: tuple[ProcesslistEntry, ...]) -> None:
        self._entries = entries

    def collect(self, connection: InstanceConnectionConfig) -> tuple[ProcesslistEntry, ...]:
        del connection
        return self._entries


class FailingProcesslistCollector(ProcesslistCollector):
    def collect(self, connection: InstanceConnectionConfig) -> tuple[ProcesslistEntry, ...]:
        del connection
        raise RuntimeError("processlist probe failed: Lost connection to MySQL server")


class FakeResponse:
    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> Literal[False]:
        del exc_type, exc, traceback
        return False

    def read(self) -> bytes:
        return b""


def _instance() -> MonitoredInstance:
    anchor = datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc)
    return MonitoredInstance(
        connection=InstanceConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=anchor,
        engine=DatabaseEngine.MYSQL,
        environment="prod",
        instance_id="inst-processlist",
        labels=("primary",),
        name="prod-primary",
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=anchor,
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )


def _entries() -> tuple[ProcesslistEntry, ...]:
    trx_started_at = datetime(2026, 4, 22, 9, 59, 45, tzinfo=timezone.utc)
    return (
        ProcesslistEntry(
            process_id=101,
            user="app",
            host="10.0.0.2:31000",
            db="ordering",
            command="Query",
            time_seconds=3,
            state="Sending data",
            info="SELECT * FROM orders WHERE id = ?",
            trx_started_at=trx_started_at,
        ),
        ProcesslistEntry(
            process_id=202,
            user="replica",
            host="10.0.0.3:31002",
            db="",
            command="Sleep",
            time_seconds=900,
            state="",
            info="",
            trx_started_at=None,
        ),
    )


def test_worker_collects_snapshot_and_writes_to_sink() -> None:
    sink = InMemoryMetricSink()
    worker = ProcesslistWorker(
        collector=StaticProcesslistCollector(_entries()),
        sink=sink,
    )

    snapshot = worker.collect_once(_instance())

    assert snapshot.instance_id == "inst-processlist"
    assert snapshot.organization_id == "org-internal"
    assert len(snapshot.entries) == 2
    commands = tuple(entry.command for entry in snapshot.entries)
    assert "Sleep" in commands, "ADR-0005 requires full-coverage capture incl. Sleep"
    assert sink.processlist_snapshots == [snapshot]


def test_worker_exposes_collector_failure_without_silent_fallback() -> None:
    sink = InMemoryMetricSink()
    worker = ProcesslistWorker(
        collector=FailingProcesslistCollector(),
        sink=sink,
    )

    with pytest.raises(RuntimeError, match="Lost connection to MySQL server"):
        worker.collect_once(_instance())
    assert sink.processlist_snapshots == []


def test_snapshot_to_clickhouse_rows_preserves_adr_0005_columns() -> None:
    snapshot = ProcesslistSnapshot(
        collected_at=datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc),
        entries=_entries(),
        instance_id="inst-processlist",
        organization_id="org-internal",
    )

    rows = snapshot_to_clickhouse_rows(snapshot)

    assert len(rows) == 2
    first, second = rows
    assert first["process_id"] == 101
    assert first["command"] == "Query"
    assert first["collected_at"] == "2026-04-22 10:00:00.000"
    assert first["trx_started_at"] == "2026-04-22 09:59:45.000"
    assert second["command"] == "Sleep"
    assert second["trx_started_at"] is None
    assert set(first.keys()) == {
        "organization_id",
        "instance_id",
        "collected_at",
        "process_id",
        "user",
        "host",
        "db",
        "command",
        "time_seconds",
        "state",
        "info",
        "trx_started_at",
    }


def test_clickhouse_sink_batch_inserts_into_mysql_processlist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request: Request) -> FakeResponse:
        captured["query"] = parse_qs(urlsplit(request.get_full_url()).query)["query"][0]
        captured["body"] = request.data
        return FakeResponse()

    monkeypatch.setattr("db_monitor_pipeline.sink.urlopen", fake_urlopen)

    sink = ClickHouseMetricSink(
        database="db_monitor",
        endpoint="http://127.0.0.1:8123",
        password="db_monitor",
        username="db_monitor",
    )

    sink.write_processlist(
        ProcesslistSnapshot(
            collected_at=datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc),
            entries=_entries(),
            instance_id="inst-processlist",
            organization_id="org-internal",
        )
    )

    assert captured["query"] == (
        f"INSERT INTO {CLICKHOUSE_MYSQL_PROCESSLIST_TABLE} FORMAT JSONEachRow"
    )
    body = captured["body"]
    assert isinstance(body, bytes)
    lines = body.decode("utf-8").splitlines()
    assert len(lines) == 2, "ADR-0005: batch insert of all processlist entries in one request"
    first_row = json.loads(lines[0])
    assert first_row["command"] == "Query"
    assert first_row["organization_id"] == "org-internal"


def test_resolve_processlist_interval_uses_default_when_key_missing() -> None:
    reader = InMemoryInstanceParameterRepository(
        parameters_by_instance={"inst-a": {"other_key": "value"}},
    )

    assert (
        resolve_processlist_interval_seconds(instance_id="inst-a", reader=reader)
        == DEFAULT_PROCESSLIST_INTERVAL_SECONDS
    )


def test_resolve_processlist_interval_uses_default_when_instance_absent() -> None:
    reader = InMemoryInstanceParameterRepository()

    assert (
        resolve_processlist_interval_seconds(instance_id="inst-b", reader=reader)
        == DEFAULT_PROCESSLIST_INTERVAL_SECONDS
    )


def test_resolve_processlist_interval_honors_override_value() -> None:
    reader = InMemoryInstanceParameterRepository(
        parameters_by_instance={
            "inst-c": {PROCESSLIST_INTERVAL_PARAMETER_KEY: 60},
        },
    )

    assert resolve_processlist_interval_seconds(instance_id="inst-c", reader=reader) == 60


def test_resolve_processlist_interval_rejects_below_minimum() -> None:
    reader = InMemoryInstanceParameterRepository(
        parameters_by_instance={
            "inst-d": {PROCESSLIST_INTERVAL_PARAMETER_KEY: 5},
        },
    )

    with pytest.raises(RuntimeError, match=str(MIN_PROCESSLIST_INTERVAL_SECONDS)):
        resolve_processlist_interval_seconds(instance_id="inst-d", reader=reader)


def test_pymysql_collector_maps_show_processlist_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from db_monitor_pipeline.processlist import PyMySQLProcesslistCollector

    class FakeCursor:
        def __init__(self, rows: Sequence[Mapping[str, Any]]) -> None:
            self._rows = rows
            self.executed: list[str] = []

        def __enter__(self) -> "FakeCursor":
            return self

        def __exit__(self, *args: object) -> Literal[False]:
            del args
            return False

        def execute(self, query: str) -> None:
            self.executed.append(query)

        def fetchall(self) -> Sequence[Mapping[str, Any]]:
            return self._rows

    class FakeConnection:
        def __init__(self, cursor: FakeCursor) -> None:
            self._cursor = cursor

        def __enter__(self) -> "FakeConnection":
            return self

        def __exit__(self, *args: object) -> Literal[False]:
            del args
            return False

        def cursor(self) -> FakeCursor:
            return self._cursor

    rows = [
        {
            "Id": 7,
            "User": "app",
            "Host": "10.0.0.2:31000",
            "db": "ordering",
            "Command": "Query",
            "Time": "3",
            "State": "Sending data",
            "Info": "SELECT 1",
            "Trx_started": datetime(2026, 4, 22, 9, 59, 45, tzinfo=timezone.utc),
        },
        {
            "Id": 9,
            "User": "idle",
            "Host": "10.0.0.2:31001",
            "db": None,
            "Command": "Sleep",
            "Time": 1234,
            "State": None,
            "Info": None,
            "Trx_started": None,
        },
    ]
    cursor = FakeCursor(rows)

    def fake_connect(**_: object) -> FakeConnection:
        return FakeConnection(cursor)

    monkeypatch.setattr(
        "db_monitor_pipeline.processlist.pymysql.connect",
        fake_connect,
    )

    entries = PyMySQLProcesslistCollector().collect(
        InstanceConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        )
    )

    assert len(entries) == 2
    assert entries[0].process_id == 7
    assert entries[0].time_seconds == 3
    assert entries[0].trx_started_at == datetime(
        2026, 4, 22, 9, 59, 45, tzinfo=timezone.utc
    )
    assert entries[1].command == "Sleep"
    assert entries[1].db == ""
    assert entries[1].info == ""
    assert entries[1].trx_started_at is None
    assert cursor.executed == ["SHOW FULL PROCESSLIST"]
