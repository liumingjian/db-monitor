from collections.abc import Callable
from dataclasses import dataclass
import time
from typing import Protocol, TypeVar

from db_monitor_api.control_plane.postgres_repository import PostgresControlPlaneRepository
from db_monitor_pipeline.collector import PyMySQLMetricsCollector, PythonOracleMetricsCollector
from db_monitor_pipeline.process_settings import SchedulerProcessSettings, WorkerProcessSettings
from db_monitor_pipeline.queue import RedisCollectionTaskQueue
from db_monitor_pipeline.scheduler import MetricsDispatchService
from db_monitor_pipeline.sink import ClickHouseMetricSink
from db_monitor_pipeline.worker import (
    EngineAwareMetricsWorker,
    MySQLMetricsWorker,
    OracleMetricsWorker,
    RetryPolicy,
    WorkerRunResult,
)
from db_monitor_schema.runtime import (
    verify_scheduler_process_schema,
    verify_worker_process_schema,
)

SleepFn = Callable[[float], None]
CycleResultT = TypeVar("CycleResultT")


class DispatchService(Protocol):
    def dispatch_collection_jobs(self) -> int:
        ...


class ProcessWorker(Protocol):
    def process_next(self) -> WorkerRunResult:
        ...


@dataclass(frozen=True)
class SchedulerCycleResult:
    dispatched_jobs: int
    status: str


@dataclass(frozen=True)
class SchedulerProcess:
    dispatch_service: DispatchService
    poll_seconds: float
    sleep: SleepFn = time.sleep

    def run_once(self) -> SchedulerCycleResult:
        dispatched_jobs = self.dispatch_service.dispatch_collection_jobs()
        return SchedulerCycleResult(
            dispatched_jobs=dispatched_jobs,
            status="dispatched" if dispatched_jobs else "idle",
        )

    def run_loop(self, *, max_cycles: int | None) -> SchedulerCycleResult:
        return _run_loop(
            max_cycles=max_cycles,
            poll_seconds=self.poll_seconds,
            run_cycle=self.run_once,
            sleep=self.sleep,
        )


@dataclass(frozen=True)
class WorkerProcess:
    poll_seconds: float
    process_worker: ProcessWorker
    sleep: SleepFn = time.sleep

    def run_once(self) -> WorkerRunResult:
        return self.process_worker.process_next()

    def run_loop(self, *, max_cycles: int | None) -> WorkerRunResult:
        return _run_loop(
            max_cycles=max_cycles,
            poll_seconds=self.poll_seconds,
            run_cycle=self.run_once,
            sleep=self.sleep,
        )


def build_scheduler_process(settings: SchedulerProcessSettings) -> SchedulerProcess:
    verify_scheduler_process_schema(settings)
    queue = RedisCollectionTaskQueue(redis_url=settings.redis_url)
    return SchedulerProcess(
        dispatch_service=MetricsDispatchService(
            control_plane_repository=PostgresControlPlaneRepository(
                postgres_dsn=settings.postgres_dsn
            ),
            queue=queue,
        ),
        poll_seconds=settings.poll_seconds,
    )


def build_worker_process(settings: WorkerProcessSettings) -> WorkerProcess:
    verify_worker_process_schema(settings)
    queue = RedisCollectionTaskQueue(redis_url=settings.redis_url)
    sink = ClickHouseMetricSink(
        database=settings.clickhouse.database,
        endpoint=settings.clickhouse.endpoint,
        password=settings.clickhouse.password,
        username=settings.clickhouse.username,
    )
    return WorkerProcess(
        poll_seconds=settings.poll_seconds,
        process_worker=EngineAwareMetricsWorker(
            mysql_worker=MySQLMetricsWorker(
                collector=PyMySQLMetricsCollector(timeout_seconds=settings.mysql_timeout_seconds),
                queue=queue,
                retry_policy=RetryPolicy(
                    backoff_seconds=settings.retry_backoff_seconds,
                    max_attempts=settings.retry_max_attempts,
                ),
                sink=sink,
            ),
            oracle_worker=OracleMetricsWorker(
                collector=PythonOracleMetricsCollector(),
                queue=queue,
                retry_policy=RetryPolicy(
                    backoff_seconds=settings.retry_backoff_seconds,
                    max_attempts=settings.retry_max_attempts,
                ),
                sink=sink,
            ),
            queue=queue,
        ),
    )


def _run_loop(
    *,
    max_cycles: int | None,
    poll_seconds: float,
    run_cycle: Callable[[], CycleResultT],
    sleep: SleepFn,
) -> CycleResultT:
    cycle_count = 1
    last_result = run_cycle()
    while max_cycles is None or cycle_count < max_cycles:
        sleep(poll_seconds)
        last_result = run_cycle()
        cycle_count += 1
    return last_result
