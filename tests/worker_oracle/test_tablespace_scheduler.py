"""Unit tests for Oracle tablespace scheduler (child #4)."""

from datetime import datetime, timedelta

import pytest

from db_monitor_api.control_plane.domain import (
    DatabaseEngine,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.instance_parameters import (
    InMemoryInstanceParameterRepository,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.sink import InMemoryMetricSink
from db_monitor_pipeline.tablespace import (
    TABLESPACE_INTERVAL_PARAMETER_KEY,
    TablespaceCollector,
    TablespaceWorker,
)
from db_monitor_pipeline.tablespace_scheduler import (
    TablespaceScheduler,
    reduce_cycle_to_run_result,
)

from tests.worker_oracle._tablespace_fixtures import (
    ANCHOR,
    FailingCollector,
    StaticCollector,
    oracle_instance,
    tablespace_entry,
)


def _build_scheduler(
    *,
    instances: tuple[MonitoredInstance, ...],
    collector: TablespaceCollector,
    parameters: dict[str, dict[str, int]] | None = None,
    clock_times: list[datetime] | None = None,
) -> TablespaceScheduler:
    repo = InMemoryControlPlaneRepository()
    for instance in instances:
        repo.create_instance(instance)
    parameter_reader = InMemoryInstanceParameterRepository(
        parameters_by_instance=parameters or {},
    )
    worker = TablespaceWorker(collector=collector, sink=InMemoryMetricSink())
    times = clock_times or [ANCHOR]
    clock_iter = iter(times)

    def clock() -> datetime:
        try:
            return next(clock_iter)
        except StopIteration:
            return times[-1]

    return TablespaceScheduler(
        control_plane_repository=repo,
        parameter_reader=parameter_reader,
        worker=worker,
        clock=clock,
    )


def test_scheduler_runs_oracle_instances_only() -> None:
    mysql = oracle_instance(instance_id="inst-mysql", engine=DatabaseEngine.MYSQL)
    oracle = oracle_instance()
    scheduler = _build_scheduler(
        instances=(mysql, oracle),
        collector=StaticCollector((tablespace_entry(),)),
    )

    cycle = scheduler.run_cycle()

    assert cycle.scanned_instances == 1
    assert cycle.scheduled_instances == 1
    assert cycle.results[0].status == "processed"


def test_scheduler_default_interval_is_300_seconds() -> None:
    first = ANCHOR
    too_early = ANCHOR + timedelta(seconds=60)
    due = ANCHOR + timedelta(seconds=301)
    scheduler = _build_scheduler(
        instances=(oracle_instance(),),
        collector=StaticCollector((tablespace_entry(),)),
        clock_times=[first, too_early, due],
    )

    scheduler.run_cycle()
    midway = scheduler.run_cycle()
    later = scheduler.run_cycle()

    assert midway.scheduled_instances == 0
    assert later.scheduled_instances == 1


def test_scheduler_rejects_below_minimum_interval() -> None:
    scheduler = _build_scheduler(
        instances=(oracle_instance(),),
        collector=StaticCollector((tablespace_entry(),)),
        parameters={"inst-oracle": {TABLESPACE_INTERVAL_PARAMETER_KEY: 30}},
    )

    with pytest.raises(RuntimeError, match="60"):
        scheduler.run_cycle()


def test_scheduler_surfaces_collector_failure() -> None:
    scheduler = _build_scheduler(
        instances=(oracle_instance(),),
        collector=FailingCollector(),
    )

    cycle = scheduler.run_cycle()
    aggregated = reduce_cycle_to_run_result(cycle)

    assert cycle.scheduled_instances == 1
    result = cycle.results[0]
    assert result.status == "failed"
    assert result.error is not None
    assert "ORA-01034" in result.error
    assert "inst-oracle" in result.error
    assert aggregated.status == "failed"


def test_non_passed_oracle_instances_are_skipped() -> None:
    failed = oracle_instance(instance_id="inst-failed", status=ValidationStatus.FAILED)
    passed = oracle_instance()
    scheduler = _build_scheduler(
        instances=(failed, passed),
        collector=StaticCollector((tablespace_entry(),)),
    )

    cycle = scheduler.run_cycle()

    assert cycle.scanned_instances == 1
    assert cycle.scheduled_instances == 1
