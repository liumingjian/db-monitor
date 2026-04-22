"""Unit tests for MySQL slow query collector + scheduler (ADR-0007)."""

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
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
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.sink import (
    CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE,
    ClickHouseMetricSink,
    InMemoryMetricSink,
)
from db_monitor_pipeline.slow_query import (
    DEFAULT_SLOW_THRESHOLD_SECONDS,
    InMemorySlowQueryCursorStore,
    MIN_SLOW_THRESHOLD_SECONDS,
    SLOW_QUERY_COLLECT_INTERVAL_SECONDS,
    SLOW_QUERY_THRESHOLD_PARAMETER_KEY,
    SlowQueryCollector,
    SlowQueryEvent,
    SlowQuerySnapshot,
    SlowQueryWorker,
    resolve_slow_threshold_seconds,
    slow_query_snapshot_to_clickhouse_rows,
)
from db_monitor_pipeline.slow_query_scheduler import (
    SlowQueryScheduler,
    reduce_slow_query_cycle_to_run_result,
)


ANCHOR = datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc)


def _instance(instance_id: str = "inst-slowq") -> MonitoredInstance:
    return MonitoredInstance(
        connection=InstanceConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=ANCHOR,
        engine=DatabaseEngine.MYSQL,
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        name="prod-primary",
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=ANCHOR,
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )


class StaticSlowQueryCollector(SlowQueryCollector):
    def __init__(
        self,
        *,
        events: tuple[SlowQueryEvent, ...] = (),
        max_event_id: int = 0,
    ) -> None:
        self._events = events
        self._max_event_id = max_event_id
        self.observed_cursor: int | None = None
        self.observed_threshold: float | None = None
        self.probe_calls = 0

    def collect(
        self,
        *,
        connection: InstanceConnectionConfig,
        last_event_id: int,
        slow_threshold_seconds: float,
    ) -> tuple[SlowQueryEvent, ...]:
        del connection
        self.observed_cursor = last_event_id
        self.observed_threshold = slow_threshold_seconds
        return tuple(
            event for event in self._events if event.event_id > last_event_id
        )

    def probe_max_event_id(self, connection: InstanceConnectionConfig) -> int:
        del connection
        self.probe_calls += 1
        return self._max_event_id


class FailingSlowQueryCollector(SlowQueryCollector):
    def collect(
        self,
        *,
        connection: InstanceConnectionConfig,
        last_event_id: int,
        slow_threshold_seconds: float,
    ) -> tuple[SlowQueryEvent, ...]:
        del connection, last_event_id, slow_threshold_seconds
        raise RuntimeError("slow query probe failed: Lost connection")

    def probe_max_event_id(self, connection: InstanceConnectionConfig) -> int:
        del connection
        return 0


class FakeResponse:
    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> Literal[False]:
        del exc_type, exc, traceback
        return False

    def read(self) -> bytes:
        return b""


def _event(event_id: int, *, timer_wait_ms: float = 1500.0) -> SlowQueryEvent:
    return SlowQueryEvent(
        event_id=event_id,
        thread_id=event_id * 10,
        user="app",
        host="10.0.0.2",
        schema_name="ordering",
        digest=f"digest-{event_id}",
        digest_text=f"SELECT {event_id}",
        sql_text=f"SELECT {event_id} FROM orders",
        timer_wait_ms=timer_wait_ms,
        rows_examined=100,
        rows_sent=10,
        rows_affected=0,
        errors=0,
        started_at=ANCHOR - timedelta(seconds=event_id),
    )


def test_worker_aligns_cursor_to_max_event_id_on_first_run() -> None:
    collector = StaticSlowQueryCollector(events=(), max_event_id=777)
    cursor_store = InMemorySlowQueryCursorStore()
    sink = InMemoryMetricSink()
    worker = SlowQueryWorker(
        collector=collector,
        cursor_store=cursor_store,
        sink=sink,
    )

    snapshot = worker.collect_once(
        instance=_instance(),
        slow_threshold_seconds=1.0,
    )

    assert collector.probe_calls == 1
    assert cursor_store.get("inst-slowq") == 777
    assert collector.observed_cursor == 777
    assert snapshot.events == ()
    assert sink.slow_query_snapshots == [snapshot]


def test_worker_advances_cursor_after_successful_write() -> None:
    collector = StaticSlowQueryCollector(
        events=(_event(10), _event(20), _event(30)),
        max_event_id=0,
    )
    cursor_store = InMemorySlowQueryCursorStore(cursors={"inst-slowq": 5})
    sink = InMemoryMetricSink()
    worker = SlowQueryWorker(
        collector=collector,
        cursor_store=cursor_store,
        sink=sink,
    )

    snapshot = worker.collect_once(
        instance=_instance(),
        slow_threshold_seconds=1.0,
    )

    assert collector.probe_calls == 0, "existing cursor must not trigger probe"
    assert collector.observed_cursor == 5
    assert snapshot.last_event_id == 30
    assert cursor_store.get("inst-slowq") == 30
    assert [event.event_id for event in snapshot.events] == [10, 20, 30]


def test_worker_does_not_advance_cursor_when_no_rows_returned() -> None:
    collector = StaticSlowQueryCollector(events=(), max_event_id=0)
    cursor_store = InMemorySlowQueryCursorStore(cursors={"inst-slowq": 42})
    worker = SlowQueryWorker(
        collector=collector,
        cursor_store=cursor_store,
        sink=InMemoryMetricSink(),
    )

    snapshot = worker.collect_once(
        instance=_instance(),
        slow_threshold_seconds=1.0,
    )

    assert snapshot.last_event_id == 42
    assert cursor_store.get("inst-slowq") == 42


def test_worker_surfaces_collector_failure_without_fallback() -> None:
    worker = SlowQueryWorker(
        collector=FailingSlowQueryCollector(),
        cursor_store=InMemorySlowQueryCursorStore(cursors={"inst-slowq": 10}),
        sink=InMemoryMetricSink(),
    )

    with pytest.raises(RuntimeError, match="Lost connection"):
        worker.collect_once(instance=_instance(), slow_threshold_seconds=1.0)


def test_resolve_slow_threshold_uses_default_when_absent() -> None:
    reader = InMemoryInstanceParameterRepository()
    assert (
        resolve_slow_threshold_seconds(instance_id="inst-a", reader=reader)
        == DEFAULT_SLOW_THRESHOLD_SECONDS
    )


def test_resolve_slow_threshold_honors_override() -> None:
    reader = InMemoryInstanceParameterRepository(
        parameters_by_instance={
            "inst-a": {SLOW_QUERY_THRESHOLD_PARAMETER_KEY: 0.5},
        },
    )
    assert resolve_slow_threshold_seconds(instance_id="inst-a", reader=reader) == 0.5


def test_resolve_slow_threshold_rejects_below_minimum() -> None:
    reader = InMemoryInstanceParameterRepository(
        parameters_by_instance={
            "inst-a": {SLOW_QUERY_THRESHOLD_PARAMETER_KEY: 0.01},
        },
    )
    with pytest.raises(RuntimeError, match=str(MIN_SLOW_THRESHOLD_SECONDS)):
        resolve_slow_threshold_seconds(instance_id="inst-a", reader=reader)


def test_snapshot_to_clickhouse_rows_contains_all_columns() -> None:
    snapshot = SlowQuerySnapshot(
        collected_at=ANCHOR,
        events=(_event(11),),
        instance_id="inst-slowq",
        organization_id="org-internal",
        last_event_id=11,
    )

    rows = slow_query_snapshot_to_clickhouse_rows(snapshot)

    assert len(rows) == 1
    row = rows[0]
    assert row["event_id"] == 11
    assert row["user"] == "app"
    assert row["digest"] == "digest-11"
    assert row["sql_text"] == "SELECT 11 FROM orders"
    assert row["timer_wait_ms"] == 1500.0
    assert row["collected_at"] == "2026-04-22 10:00:00.000"
    assert row["started_at"] == "2026-04-22 09:59:49.000"
    assert set(row.keys()) == {
        "organization_id",
        "instance_id",
        "collected_at",
        "event_id",
        "thread_id",
        "user",
        "host",
        "schema_name",
        "digest",
        "digest_text",
        "sql_text",
        "timer_wait_ms",
        "rows_examined",
        "rows_sent",
        "rows_affected",
        "errors",
        "started_at",
    }


def test_clickhouse_sink_batches_slow_query_inserts(
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

    sink.write_slow_queries(
        SlowQuerySnapshot(
            collected_at=ANCHOR,
            events=(_event(1), _event(2)),
            instance_id="inst-slowq",
            organization_id="org-internal",
            last_event_id=2,
        )
    )

    assert captured["query"] == (
        f"INSERT INTO {CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE} FORMAT JSONEachRow"
    )
    body = captured["body"]
    assert isinstance(body, bytes)
    lines = body.decode("utf-8").splitlines()
    assert len(lines) == 2
    payload_first = json.loads(lines[0])
    assert payload_first["event_id"] == 1
    assert payload_first["timer_wait_ms"] == 1500.0


def test_pymysql_collector_maps_performance_schema_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from db_monitor_pipeline.slow_query import PyMySQLSlowQueryCollector

    class FakeCursor:
        def __init__(self, rows: list[Mapping[str, Any]]) -> None:
            self._rows = rows
            self.executed: list[tuple[str, tuple[object, ...]]] = []

        def __enter__(self) -> "FakeCursor":
            return self

        def __exit__(self, *args: object) -> Literal[False]:
            del args
            return False

        def execute(self, query: str, params: tuple[object, ...] = ()) -> None:
            self.executed.append((query, params))

        def fetchall(self) -> list[Mapping[str, Any]]:
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
            "EVENT_ID": 100,
            "THREAD_ID": 7,
            "CURRENT_SCHEMA": "ordering",
            "DIGEST": "abc",
            "DIGEST_TEXT": "SELECT ?",
            "SQL_TEXT": "SELECT 1",
            "TIMER_WAIT": 2_500_000_000_000,
            "ROWS_EXAMINED": 500,
            "ROWS_SENT": 1,
            "ROWS_AFFECTED": 0,
            "ERRORS": 0,
            "USER": "app",
            "HOST": "10.0.0.2",
        },
    ]
    cursor = FakeCursor(rows)

    def fake_connect(**_: object) -> FakeConnection:
        return FakeConnection(cursor)

    monkeypatch.setattr(
        "db_monitor_pipeline.slow_query.pymysql.connect",
        fake_connect,
    )

    events = PyMySQLSlowQueryCollector().collect(
        connection=_instance().connection,
        last_event_id=50,
        slow_threshold_seconds=1.0,
    )

    assert len(events) == 1
    event = events[0]
    assert event.event_id == 100
    assert event.user == "app"
    assert event.host == "10.0.0.2"
    assert event.schema_name == "ordering"
    assert event.timer_wait_ms == 2_500.0
    assert cursor.executed[0][1][0] == 50
    assert cursor.executed[0][1][1] == 1_000_000_000_000


def test_scheduler_dispatches_only_passed_mysql_instances_with_cooldown() -> None:
    primary = _instance("inst-primary")
    failed = _instance("inst-failed")
    failed = MonitoredInstance(
        connection=failed.connection,
        created_at=failed.created_at,
        engine=failed.engine,
        environment=failed.environment,
        instance_id=failed.instance_id,
        labels=failed.labels,
        name=failed.name,
        organization_id=failed.organization_id,
        validation=ConnectionValidation(
            checked_at=ANCHOR,
            detail="failed",
            server_version=None,
            status=ValidationStatus.FAILED,
        ),
    )
    repo = InMemoryControlPlaneRepository()
    repo.create_instance(primary)
    repo.create_instance(failed)
    reader = InMemoryInstanceParameterRepository()
    collector = StaticSlowQueryCollector(events=(_event(10),), max_event_id=0)
    worker = SlowQueryWorker(
        collector=collector,
        cursor_store=InMemorySlowQueryCursorStore(cursors={"inst-primary": 0}),
        sink=InMemoryMetricSink(),
    )
    times = iter(
        [
            ANCHOR,
            ANCHOR + timedelta(seconds=10),
            ANCHOR + timedelta(seconds=SLOW_QUERY_COLLECT_INTERVAL_SECONDS + 1),
        ]
    )
    scheduler = SlowQueryScheduler(
        control_plane_repository=repo,
        parameter_reader=reader,
        worker=worker,
        clock=lambda: next(times),
    )

    first_cycle = scheduler.run_cycle()
    assert first_cycle.scanned_instances == 1
    assert first_cycle.scheduled_instances == 1
    assert first_cycle.results[0].status == "processed"

    second_cycle = scheduler.run_cycle()
    assert second_cycle.scheduled_instances == 0, "within cooldown should be skipped"

    third_cycle = scheduler.run_cycle()
    assert third_cycle.scheduled_instances == 1, "past cooldown should run again"


def test_reduce_cycle_reports_failure_when_any_instance_fails() -> None:
    repo = InMemoryControlPlaneRepository()
    repo.create_instance(_instance())
    scheduler = SlowQueryScheduler(
        control_plane_repository=repo,
        parameter_reader=InMemoryInstanceParameterRepository(),
        worker=SlowQueryWorker(
            collector=FailingSlowQueryCollector(),
            cursor_store=InMemorySlowQueryCursorStore(cursors={"inst-slowq": 0}),
            sink=InMemoryMetricSink(),
        ),
        clock=lambda: ANCHOR,
    )

    cycle = scheduler.run_cycle()
    result = reduce_slow_query_cycle_to_run_result(cycle)

    assert result.status == "failed"
    assert "Lost connection" in (result.error or "")
