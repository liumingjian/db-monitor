from collections.abc import Mapping

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    MySQLConnectionConfig,
    MySQLInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.collector import MySQLMetricsCollector
from db_monitor_pipeline.queue import InMemoryCollectionTaskQueue
from db_monitor_pipeline.scheduler import MetricsDispatchService
from db_monitor_pipeline.sink import InMemoryMetricSink, MetricSink
from db_monitor_pipeline.worker import MySQLMetricsWorker, RetryPolicy


class FlakyCollector(MySQLMetricsCollector):
    def __init__(self) -> None:
        self.calls = 0

    def collect(self, connection: MySQLConnectionConfig) -> Mapping[str, str]:
        del connection
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("mysql timeout")
        return {
            "Bytes_received": "128",
            "Bytes_sent": "256",
            "Innodb_buffer_pool_reads": "2",
            "Questions": "42",
            "Seconds_Behind_Source": "0",
            "Threads_connected": "10",
            "Threads_running": "3",
            "Uptime": "3600",
        }


class StaticCollector(MySQLMetricsCollector):
    def collect(self, connection: MySQLConnectionConfig) -> Mapping[str, str]:
        del connection
        return {
            "Bytes_received": "128",
            "Bytes_sent": "256",
            "Innodb_buffer_pool_reads": "2",
            "Questions": "42",
            "Seconds_Behind_Source": "0",
            "Threads_connected": "10",
            "Threads_running": "3",
            "Uptime": "3600",
        }


class FailingSink(MetricSink):
    def write(self, samples: tuple[object, ...]) -> None:
        del samples
        raise RuntimeError("clickhouse timeout after write boundary")


def test_pipeline_recovery_contract_dedupes_pending_jobs_and_schedules_retry() -> None:
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(_build_instance())
    queue = InMemoryCollectionTaskQueue()
    sink = InMemoryMetricSink()
    dispatch_service = MetricsDispatchService(
        control_plane_repository=repository,
        queue=queue,
    )
    worker = MySQLMetricsWorker(
        collector=FlakyCollector(),
        queue=queue,
        retry_policy=RetryPolicy(backoff_seconds=1, max_attempts=2),
        sink=sink,
    )

    first_dispatch = dispatch_service.dispatch_collection_jobs()
    second_dispatch = dispatch_service.dispatch_collection_jobs()
    first_result = worker.process_next()
    second_result = worker.process_next()

    assert first_dispatch == 1
    assert second_dispatch == 0
    assert first_result.status == "retry_scheduled"
    assert first_result.retry_attempt == 2
    assert first_result.next_retry_at is not None
    assert second_result.status == "idle"


def test_pipeline_recovery_behavior_does_not_retry_non_idempotent_sink_failures() -> None:
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(_build_instance())
    queue = InMemoryCollectionTaskQueue()
    MetricsDispatchService(control_plane_repository=repository, queue=queue).dispatch_collection_jobs()

    result = MySQLMetricsWorker(
        collector=StaticCollector(),
        queue=queue,
        retry_policy=RetryPolicy(backoff_seconds=1, max_attempts=2),
        sink=FailingSink(),
    ).process_next()

    assert result.status == "failed"
    assert result.error is not None
    assert "non-idempotent sink failure" in result.error
    assert queue.size() == 0


def _build_instance() -> MySQLInstance:
    return MySQLInstance(
        connection=MySQLConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=utc_now(),
        environment="prod",
        instance_id="inst-recovery",
        labels=("primary",),
        name="prod-primary",
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=utc_now(),
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )
