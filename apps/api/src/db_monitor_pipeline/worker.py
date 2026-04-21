from dataclasses import dataclass, field
from datetime import datetime, timedelta

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.collector import MySQLMetricsCollector, OracleMetricsCollector
from db_monitor_pipeline.domain import CollectionJob
from db_monitor_pipeline.normalization import normalize_metrics
from db_monitor_pipeline.queue import CollectionTaskQueue
from db_monitor_pipeline.sink import MetricSink

DEFAULT_RETRY_BACKOFF_SECONDS = 30
DEFAULT_RETRY_MAX_ATTEMPTS = 3
NON_IDEMPOTENT_SINK_ERROR_PREFIX = "non-idempotent sink failure"


@dataclass(frozen=True)
class RetryPolicy:
    backoff_seconds: int = DEFAULT_RETRY_BACKOFF_SECONDS
    max_attempts: int = DEFAULT_RETRY_MAX_ATTEMPTS


@dataclass(frozen=True)
class WorkerRunResult:
    error: str | None
    next_retry_at: datetime | None
    processed_metrics: int
    retry_attempt: int | None
    status: str


@dataclass(frozen=True)
class MySQLMetricsWorker:
    collector: MySQLMetricsCollector
    queue: CollectionTaskQueue
    sink: MetricSink
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)

    def process_next(self) -> WorkerRunResult:
        job = self.queue.dequeue()
        return _idle_worker_run_result() if job is None else self.process_job(job)

    def process_job(self, job: CollectionJob) -> WorkerRunResult:
        return _process_job(
            collector=self.collector,
            expected_engine=DatabaseEngine.MYSQL,
            job=job,
            queue=self.queue,
            retry_policy=self.retry_policy,
            sink=self.sink,
        )


@dataclass(frozen=True)
class OracleMetricsWorker:
    collector: OracleMetricsCollector
    queue: CollectionTaskQueue
    sink: MetricSink
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)

    def process_next(self) -> WorkerRunResult:
        job = self.queue.dequeue()
        return _idle_worker_run_result() if job is None else self.process_job(job)

    def process_job(self, job: CollectionJob) -> WorkerRunResult:
        return _process_job(
            collector=self.collector,
            expected_engine=DatabaseEngine.ORACLE,
            job=job,
            queue=self.queue,
            retry_policy=self.retry_policy,
            sink=self.sink,
        )


@dataclass(frozen=True)
class EngineAwareMetricsWorker:
    mysql_worker: MySQLMetricsWorker
    oracle_worker: OracleMetricsWorker
    queue: CollectionTaskQueue

    def process_next(self) -> WorkerRunResult:
        job = self.queue.dequeue()
        if job is None:
            return _idle_worker_run_result()
        if job.engine is DatabaseEngine.MYSQL:
            return self.mysql_worker.process_job(job)
        if job.engine is DatabaseEngine.ORACLE:
            return self.oracle_worker.process_job(job)
        return WorkerRunResult(
            error=f"Unsupported database engine: {job.engine.value}",
            next_retry_at=None,
            processed_metrics=0,
            retry_attempt=job.attempt,
            status="failed",
        )


def _idle_worker_run_result() -> WorkerRunResult:
    return WorkerRunResult(
        error=None,
        next_retry_at=None,
        processed_metrics=0,
        retry_attempt=None,
        status="idle",
    )


def _process_job(
    *,
    collector: MySQLMetricsCollector | OracleMetricsCollector,
    expected_engine: DatabaseEngine,
    job: CollectionJob,
    queue: CollectionTaskQueue,
    retry_policy: RetryPolicy,
    sink: MetricSink,
) -> WorkerRunResult:
    if job.engine is not expected_engine:
        return WorkerRunResult(
            error=(
                f"Worker for engine {expected_engine.value} received "
                f"{job.engine.value} job."
            ),
            next_retry_at=None,
            processed_metrics=0,
            retry_attempt=job.attempt,
            status="failed",
        )
    try:
        raw_metrics = collector.collect(job.connection)
    except Exception as error:
        return _schedule_retry(
            job=job,
            message=str(error),
            queue=queue,
            retry_policy=retry_policy,
        )
    samples = normalize_metrics(
        collected_at=utc_now(),
        job=job,
        raw_metrics=raw_metrics,
    )
    try:
        sink.write(samples)
    except Exception as error:
        return WorkerRunResult(
            error=f"{NON_IDEMPOTENT_SINK_ERROR_PREFIX}: {error}",
            next_retry_at=None,
            processed_metrics=0,
            retry_attempt=job.attempt,
            status="failed",
        )
    return WorkerRunResult(
        error=None,
        next_retry_at=None,
        processed_metrics=len(samples),
        retry_attempt=job.attempt,
        status="processed",
    )


def _schedule_retry(
    *,
    job: CollectionJob,
    message: str,
    queue: CollectionTaskQueue,
    retry_policy: RetryPolicy,
) -> WorkerRunResult:
    if job.attempt >= retry_policy.max_attempts:
        return WorkerRunResult(
            error=message,
            next_retry_at=None,
            processed_metrics=0,
            retry_attempt=job.attempt,
            status="failed",
        )
    next_retry_at = utc_now() + timedelta(seconds=retry_policy.backoff_seconds)
    queue.enqueue(job.schedule_retry(available_at=next_retry_at))
    return WorkerRunResult(
        error=message,
        next_retry_at=next_retry_at,
        processed_metrics=0,
        retry_attempt=job.attempt + 1,
        status="retry_scheduled",
    )
