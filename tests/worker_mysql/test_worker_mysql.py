from collections.abc import Mapping

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import DatabaseEngine, MySQLConnectionConfig
from db_monitor_pipeline.collector import MySQLMetricsCollector
from db_monitor_pipeline.domain import CollectionJob, INITIAL_COLLECTION_ATTEMPT
from db_monitor_pipeline.queue import InMemoryCollectionTaskQueue
from db_monitor_pipeline.sink import InMemoryMetricSink
from db_monitor_pipeline.worker import MySQLMetricsWorker, RetryPolicy


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


class FailingCollector(MySQLMetricsCollector):
    def collect(self, connection: MySQLConnectionConfig) -> Mapping[str, str]:
        del connection
        raise RuntimeError("access denied for metrics user")


def test_worker_writes_normalized_metrics_to_sink() -> None:
    queue = InMemoryCollectionTaskQueue()
    queue.enqueue(_build_job())
    sink = InMemoryMetricSink()

    result = MySQLMetricsWorker(
        collector=StaticCollector(),
        queue=queue,
        sink=sink,
    ).process_next()

    assert result.status == "processed"
    assert result.processed_metrics == 9
    assert len(sink.samples) == 9
    assert sink.samples[0].metric_name == "mysql_server_available"


def test_worker_exposes_collection_failures_without_fake_success() -> None:
    queue = InMemoryCollectionTaskQueue()
    queue.enqueue(_build_job())
    sink = InMemoryMetricSink()

    result = MySQLMetricsWorker(
        collector=FailingCollector(),
        queue=queue,
        retry_policy=RetryPolicy(backoff_seconds=1, max_attempts=1),
        sink=sink,
    ).process_next()

    assert result.status == "failed"
    assert result.error == "access denied for metrics user"
    assert sink.samples == []


def _build_job() -> CollectionJob:
    queued_at = utc_now()
    return CollectionJob(
        attempt=INITIAL_COLLECTION_ATTEMPT,
        available_at=queued_at,
        connection=MySQLConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        engine=DatabaseEngine.MYSQL,
        environment="prod",
        instance_id="inst-123",
        labels=("primary",),
        name="prod-primary",
        queued_at=queued_at,
    )
