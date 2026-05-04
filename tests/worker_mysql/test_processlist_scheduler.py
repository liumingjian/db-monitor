"""ADR-0011 D3 + EPIC 15 Control Contract: processlist scheduler.

Verifies that `ProcesslistScheduler`:
- Reads per-instance cadence from `InstanceParameterRepository`
- Falls back to 30s when the key is absent
- Surfaces collector failures as WorkerRunResult(status="failed") with a
  non-empty `error`, without silent retry/swallow.
- Honours the `MIN_PROCESSLIST_INTERVAL_SECONDS=10` floor (raises a
  RuntimeError when the reader returns below-floor value, per the
  resolver's contract).
- Skips instances with `validation_status != PASSED` and non-MySQL
  engines.
"""

from datetime import datetime, timedelta, timezone

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
from db_monitor_pipeline.processlist import (
    PROCESSLIST_INTERVAL_PARAMETER_KEY,
    ProcesslistCollector,
    ProcesslistEntry,
    ProcesslistWorker,
)
from db_monitor_pipeline.processlist_scheduler import (
    ProcesslistScheduler,
    reduce_cycle_to_run_result,
)
from db_monitor_pipeline.sink import InMemoryMetricSink


ANCHOR = datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc)


class StaticCollector(ProcesslistCollector):
    def __init__(self, entries: tuple[ProcesslistEntry, ...]) -> None:
        self._entries = entries

    def collect(
        self, connection: InstanceConnectionConfig
    ) -> tuple[ProcesslistEntry, ...]:
        del connection
        return self._entries


class FailingCollector(ProcesslistCollector):
    def collect(
        self, connection: InstanceConnectionConfig
    ) -> tuple[ProcesslistEntry, ...]:
        del connection
        raise RuntimeError("Lost connection to MySQL server during query")


def _instance(
    *,
    instance_id: str = "inst-a",
    status: ValidationStatus = ValidationStatus.PASSED,
    engine: DatabaseEngine = DatabaseEngine.MYSQL,
) -> MonitoredInstance:
    return MonitoredInstance(
        connection=InstanceConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=ANCHOR,
        engine=engine,
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        name=instance_id,
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=ANCHOR,
            detail="ok",
            server_version="8.4.0",
            status=status,
        ),
    )


def _entry() -> ProcesslistEntry:
    return ProcesslistEntry(
        process_id=101,
        user="app",
        host="10.0.0.2:31000",
        db="ordering",
        command="Query",
        time_seconds=3,
        state="Sending data",
        info="SELECT 1",
        trx_started_at=None,
    )


def _build_scheduler(
    *,
    instances: tuple[MonitoredInstance, ...],
    collector: ProcesslistCollector,
    parameters: dict[str, dict[str, int]] | None = None,
    clock_times: list[datetime] | None = None,
) -> ProcesslistScheduler:
    repo = InMemoryControlPlaneRepository()
    for instance in instances:
        repo.create_instance(instance)
    parameter_reader = InMemoryInstanceParameterRepository(
        parameters_by_instance=parameters or {},
    )
    worker = ProcesslistWorker(collector=collector, sink=InMemoryMetricSink())
    times = clock_times or [ANCHOR]
    clock_iter = iter(times)

    def clock() -> datetime:
        try:
            return next(clock_iter)
        except StopIteration:
            return times[-1]

    return ProcesslistScheduler(
        control_plane_repository=repo,
        parameter_reader=parameter_reader,
        worker=worker,
        clock=clock,
    )


def test_default_interval_is_applied_when_parameter_row_absent() -> None:
    scheduler = _build_scheduler(
        instances=(_instance(),),
        collector=StaticCollector((_entry(),)),
    )

    cycle = scheduler.run_cycle()

    assert cycle.scheduled_instances == 1
    assert cycle.results[0].status == "processed"
    assert cycle.results[0].processed_metrics == 1


def test_scheduler_honours_configured_interval_between_cycles() -> None:
    first = ANCHOR
    second = ANCHOR + timedelta(seconds=60)  # > 60s cadence
    third = ANCHOR + timedelta(seconds=30)  # < 60s cadence: should not run
    scheduler = _build_scheduler(
        instances=(_instance(),),
        collector=StaticCollector((_entry(),)),
        parameters={"inst-a": {PROCESSLIST_INTERVAL_PARAMETER_KEY: 60}},
        clock_times=[first, third, second],
    )

    scheduler.run_cycle()  # first run schedules
    midway_cycle = scheduler.run_cycle()  # too early
    due_cycle = scheduler.run_cycle()  # now due

    assert midway_cycle.scheduled_instances == 0
    assert due_cycle.scheduled_instances == 1


def test_collector_failure_is_surfaced_without_silent_swallow() -> None:
    scheduler = _build_scheduler(
        instances=(_instance(),),
        collector=FailingCollector(),
    )

    cycle = scheduler.run_cycle()

    assert cycle.scheduled_instances == 1
    result = cycle.results[0]
    assert result.status == "failed"
    assert result.error is not None
    assert "Lost connection to MySQL server" in result.error
    assert "inst-a" in result.error, "Error message must carry the instance_id root cause."


def test_scheduler_rejects_below_minimum_interval() -> None:
    scheduler = _build_scheduler(
        instances=(_instance(),),
        collector=StaticCollector((_entry(),)),
        parameters={"inst-a": {PROCESSLIST_INTERVAL_PARAMETER_KEY: 5}},
    )

    with pytest.raises(RuntimeError, match="10"):
        scheduler.run_cycle()


def test_non_passed_instances_are_skipped() -> None:
    failed = _instance(instance_id="inst-failed", status=ValidationStatus.FAILED)
    passed = _instance(instance_id="inst-passed", status=ValidationStatus.PASSED)
    scheduler = _build_scheduler(
        instances=(failed, passed),
        collector=StaticCollector((_entry(),)),
    )

    cycle = scheduler.run_cycle()

    assert cycle.scanned_instances == 1
    assert cycle.scheduled_instances == 1


def test_non_mysql_engine_instances_are_skipped() -> None:
    oracle = _instance(instance_id="inst-oracle", engine=DatabaseEngine.ORACLE)
    scheduler = _build_scheduler(
        instances=(oracle,),
        collector=StaticCollector((_entry(),)),
    )

    cycle = scheduler.run_cycle()

    assert cycle.scanned_instances == 0
    assert cycle.scheduled_instances == 0


def test_reduce_cycle_failure_precedence() -> None:
    scheduler = _build_scheduler(
        instances=(_instance(),),
        collector=FailingCollector(),
    )

    cycle = scheduler.run_cycle()
    aggregated = reduce_cycle_to_run_result(cycle)

    assert aggregated.status == "failed"
    assert aggregated.error is not None
    assert "Lost connection" in aggregated.error


def test_reduce_cycle_idle_when_nothing_due() -> None:
    scheduler = _build_scheduler(
        instances=(),
        collector=StaticCollector((_entry(),)),
    )

    aggregated = reduce_cycle_to_run_result(scheduler.run_cycle())

    assert aggregated.status == "idle"
    assert aggregated.error is None
