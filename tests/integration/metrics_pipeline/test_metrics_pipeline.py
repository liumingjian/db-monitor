from collections.abc import Mapping
from datetime import UTC, datetime
import json

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    MySQLConnectionConfig,
    MySQLInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.domain import MetricKind, MetricSample
from db_monitor_pipeline.collector import MySQLMetricsCollector
from db_monitor_pipeline.queue import InMemoryCollectionTaskQueue
from db_monitor_pipeline.scheduler import MetricsDispatchService
from db_monitor_pipeline.sink import InMemoryMetricSink
from db_monitor_pipeline.sink import _sample_to_json
from db_monitor_pipeline.worker import MySQLMetricsWorker


class StaticCollector(MySQLMetricsCollector):
    def collect(self, connection: MySQLConnectionConfig) -> Mapping[str, str]:
        del connection
        return {
            "Bytes_received": "128",
            "Bytes_sent": "256",
            "Com_commit": "20",
            "Com_rollback": "1",
            "Innodb_buffer_pool_reads": "2",
            "Questions": "42",
            "Seconds_Behind_Source": "0",
            "Threads_connected": "10",
            "Threads_running": "3",
            "Uptime": "3600",
        }


def test_scheduler_to_worker_pipeline_writes_normalized_metrics() -> None:
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(_build_instance())
    queue = InMemoryCollectionTaskQueue()
    sink = InMemoryMetricSink()

    dispatched = MetricsDispatchService(
        control_plane_repository=repository,
        queue=queue,
    ).dispatch_collection_jobs()
    result = MySQLMetricsWorker(
        collector=StaticCollector(),
        queue=queue,
        sink=sink,
    ).process_next()

    assert dispatched == 1
    assert result.status == "processed"
    assert result.processed_metrics == len(sink.samples)
    assert {sample.metric_name for sample in sink.samples} >= {
        "mysql_server_available",
        "mysql_transactions_total",
        "mysql_threads_connected",
        "mysql_queries_total",
    }


def test_clickhouse_write_payload_uses_clickhouse_datetime_format() -> None:
    payload = json.loads(
        _sample_to_json(
            MetricSample(
                collected_at=datetime(2026, 4, 19, 0, 0, 0, 123000, tzinfo=UTC),
                environment="prod",
                instance_id="inst-1",
                labels=("primary",),
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_server_available",
                metric_value=1.0,
            )
        )
    )

    assert payload["collected_at"] == "2026-04-19 00:00:00.123"
    assert payload["engine"] == "mysql"


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
        instance_id="inst-1",
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
