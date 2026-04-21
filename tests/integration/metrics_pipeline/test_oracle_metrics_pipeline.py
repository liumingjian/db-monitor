from collections.abc import Mapping

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    InstanceConnectionConfig,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.collector import OracleMetricsCollector
from db_monitor_pipeline.queue import InMemoryCollectionTaskQueue
from db_monitor_pipeline.scheduler import MetricsDispatchService
from db_monitor_pipeline.sink import InMemoryMetricSink
from db_monitor_pipeline.worker import OracleMetricsWorker


class StaticOracleCollector(OracleMetricsCollector):
    def collect(self, connection: InstanceConnectionConfig) -> Mapping[str, str]:
        del connection
        return {
            "SessionsActive": "4",
            "SessionsTotal": "11",
            "SessionWaits": "1",
            "PhysicalReads": "24",
            "UptimeSeconds": "5400",
            "UserCalls": "96",
        }


def test_scheduler_to_oracle_worker_pipeline_writes_normalized_metrics() -> None:
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(_build_oracle_instance())
    queue = InMemoryCollectionTaskQueue()
    sink = InMemoryMetricSink()

    dispatched = MetricsDispatchService(
        control_plane_repository=repository,
        queue=queue,
    ).dispatch_collection_jobs()
    result = OracleMetricsWorker(
        collector=StaticOracleCollector(),
        queue=queue,
        sink=sink,
    ).process_next()

    assert dispatched == 1
    assert result.status == "processed"
    assert result.processed_metrics == len(sink.samples)
    assert {sample.metric_name for sample in sink.samples} >= {
        "oracle_server_available",
        "oracle_sessions_total",
        "oracle_user_calls_total",
    }


def _build_oracle_instance() -> MonitoredInstance:
    return MonitoredInstance(
        connection=InstanceConnectionConfig(
            database="XE",
            host="127.0.0.1",
            password="oracle",
            port=15211,
            username="system",
        ),
        created_at=utc_now(),
        engine=DatabaseEngine.ORACLE,
        environment="prod",
        instance_id="inst-oracle-1",
        labels=("oracle", "primary"),
        name="prod-oracle-primary",
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=utc_now(),
            detail="ok",
            server_version="11.2.0.2.0",
            status=ValidationStatus.PASSED,
        ),
    )
