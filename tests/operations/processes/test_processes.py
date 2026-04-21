from db_monitor_pipeline.process_settings import (
    ProcessMode,
    load_scheduler_process_settings,
    load_worker_process_settings,
)
from db_monitor_pipeline.processes import SchedulerCycleResult, SchedulerProcess, WorkerProcess
from db_monitor_pipeline.worker import WorkerRunResult


class StaticDispatchService:
    def __init__(self, counts: tuple[int, ...]) -> None:
        self._counts = list(counts)

    def dispatch_collection_jobs(self) -> int:
        return self._counts.pop(0)


class StaticProcessWorker:
    def __init__(self, results: tuple[WorkerRunResult, ...]) -> None:
        self._results = list(results)

    def process_next(self) -> WorkerRunResult:
        return self._results.pop(0)


def test_scheduler_process_contract_loads_settings_and_reports_dispatch_state() -> None:
    settings = load_scheduler_process_settings(
        {
            "DB_MONITOR_POSTGRES_DSN": "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor",
            "DB_MONITOR_REDIS_URL": "redis://127.0.0.1:6379/0",
            "DB_MONITOR_SCHEDULER_MAX_CYCLES": "2",
            "DB_MONITOR_SCHEDULER_MODE": "loop",
            "DB_MONITOR_SCHEDULER_POLL_SECONDS": "1.5",
        }
    )
    process = SchedulerProcess(
        dispatch_service=StaticDispatchService((2,)),
        poll_seconds=settings.poll_seconds,
    )

    result = process.run_once()

    assert settings.mode is ProcessMode.LOOP
    assert settings.max_cycles == 2
    assert settings.poll_seconds == 1.5
    assert result == SchedulerCycleResult(dispatched_jobs=2, status="dispatched")


def test_scheduler_process_loop_sleeps_between_cycles() -> None:
    sleep_calls: list[float] = []
    process = SchedulerProcess(
        dispatch_service=StaticDispatchService((0, 1)),
        poll_seconds=0.25,
        sleep=sleep_calls.append,
    )

    result = process.run_loop(max_cycles=2)

    assert result == SchedulerCycleResult(dispatched_jobs=1, status="dispatched")
    assert sleep_calls == [0.25]


def test_worker_process_contract_loads_settings_and_reports_idle_state() -> None:
    settings = load_worker_process_settings(
        {
            "DB_MONITOR_CLICKHOUSE_DATABASE": "db_monitor",
            "DB_MONITOR_CLICKHOUSE_ENDPOINT": "http://127.0.0.1:8123",
            "DB_MONITOR_CLICKHOUSE_PASSWORD": "db_monitor",
            "DB_MONITOR_CLICKHOUSE_USERNAME": "db_monitor",
            "DB_MONITOR_REDIS_URL": "redis://127.0.0.1:6379/0",
            "DB_MONITOR_WORKER_MYSQL_MAX_CYCLES": "3",
            "DB_MONITOR_WORKER_MYSQL_MODE": "loop",
            "DB_MONITOR_WORKER_MYSQL_POLL_SECONDS": "2.0",
            "DB_MONITOR_WORKER_MYSQL_TIMEOUT_SECONDS": "7",
        }
    )
    process = WorkerProcess(
        poll_seconds=settings.poll_seconds,
        process_worker=StaticProcessWorker(
            (
                WorkerRunResult(
                    error=None,
                    next_retry_at=None,
                    processed_metrics=0,
                    retry_attempt=None,
                    status="idle",
                ),
            )
        ),
    )

    result = process.run_once()

    assert settings.mode is ProcessMode.LOOP
    assert settings.max_cycles == 3
    assert settings.mysql_timeout_seconds == 7
    assert result.status == "idle"
    assert result.processed_metrics == 0


def test_worker_process_loop_surfaces_failed_cycle() -> None:
    sleep_calls: list[float] = []
    process = WorkerProcess(
        poll_seconds=2.0,
        process_worker=StaticProcessWorker(
            (
                WorkerRunResult(
                    error=None,
                    next_retry_at=None,
                    processed_metrics=9,
                    retry_attempt=1,
                    status="processed",
                ),
                WorkerRunResult(
                    error="access denied for metrics user",
                    next_retry_at=None,
                    processed_metrics=0,
                    retry_attempt=2,
                    status="failed",
                ),
            )
        ),
        sleep=sleep_calls.append,
    )

    result = process.run_loop(max_cycles=2)

    assert result.status == "failed"
    assert result.error == "access denied for metrics user"
    assert sleep_calls == [2.0]
