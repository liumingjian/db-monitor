from collections.abc import Mapping
from datetime import datetime, timedelta
import os
import time
import uuid

import psycopg
import pytest
import redis

from db_monitor_api.alerting.domain import AlertEventType, NotificationRequest, RuleOperator, RuleSeverity
from db_monitor_api.alerting.notifier import Notifier
from db_monitor_api.alerting.postgres_repository import PostgresAlertingRepository
from db_monitor_api.alerting.service import (
    AlertingService,
    NotificationDeliveryError,
    NotificationRetryPolicy,
)
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    MySQLConnectionConfig,
    MySQLInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.collector import MySQLMetricsCollector
from db_monitor_pipeline.domain import MetricKind, MetricSample
from db_monitor_pipeline.queue import RedisCollectionTaskQueue
from db_monitor_pipeline.scheduler import MetricsDispatchService
from db_monitor_pipeline.sink import InMemoryMetricSink
from db_monitor_pipeline.worker import MySQLMetricsWorker, RetryPolicy
from db_monitor_schema.postgres import bootstrap_postgres_schema

POSTGRES_DSN_ENV = "DB_MONITOR_POSTGRES_DSN"
READY_TIMEOUT_SECONDS = 30
REDIS_URL_ENV = "DB_MONITOR_REDIS_URL"
RETRY_INTERVAL_SECONDS = 1


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


class FailingOnceNotifier(Notifier):
    def __init__(self) -> None:
        self.calls = 0

    def send(self, request: NotificationRequest) -> None:
        del request
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("smtp unavailable")


def test_live_recovery_paths_dedupe_pending_jobs_retry_safe_failures_and_resume_notifications() -> None:
    postgres_dsn = _required_env(POSTGRES_DSN_ENV)
    redis_url = _required_env(REDIS_URL_ENV)
    queue_name = f"db-monitor:recovery:{uuid.uuid4().hex}"

    _wait_for_postgres(postgres_dsn)
    _wait_for_redis(redis_url)
    _reset_postgres_state(postgres_dsn)
    bootstrap_postgres_schema(postgres_dsn=postgres_dsn)

    queue = RedisCollectionTaskQueue(queue_name=queue_name, redis_url=redis_url)
    control_plane_repository = InMemoryControlPlaneRepository()
    control_plane_repository.create_instance(_build_instance())
    dispatch_service = MetricsDispatchService(
        control_plane_repository=control_plane_repository,
        queue=queue,
    )
    sink = InMemoryMetricSink()
    worker = MySQLMetricsWorker(
        collector=FlakyCollector(),
        queue=queue,
        retry_policy=RetryPolicy(backoff_seconds=0, max_attempts=2),
        sink=sink,
    )

    first_dispatch = dispatch_service.dispatch_collection_jobs()
    second_dispatch = dispatch_service.dispatch_collection_jobs()
    first_result = worker.process_next()
    second_result = worker.process_next()

    notifier = FailingOnceNotifier()
    alert_repository = PostgresAlertingRepository(postgres_dsn=postgres_dsn)
    alert_service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        notification_retry_policy=NotificationRetryPolicy(backoff_seconds=0),
        repository=alert_repository,
    )
    alert_service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-recovery-live",),
        metric_name="mysql_replication_lag_seconds",
        name="Replication Lag High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.CRITICAL,
        threshold=5.0,
    )
    with pytest.raises(NotificationDeliveryError, match="smtp unavailable"):
        alert_service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=sample_anchor(),
                    instance_id="inst-recovery-live",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=9.0,
                    minutes_ago=1,
                ),
            )
        )
    recovery_summary = alert_service.evaluate_samples(
        samples=(
            build_sample(
                anchor=sample_anchor() + timedelta(minutes=1),
                instance_id="inst-recovery-live",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=0,
            ),
        )
    )
    alert = alert_service.list_alerts()[0]
    detail = alert_service.get_alert(alert_id=alert.alert_id)

    suppression_notifier = FailingOnceNotifier()
    suppression_service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=suppression_notifier,
        notification_retry_policy=NotificationRetryPolicy(backoff_seconds=0),
        repository=alert_repository,
    )
    suppression_service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-recovery-live-ack",),
        metric_name="mysql_replication_lag_seconds",
        name="Replication Lag High Acked",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.CRITICAL,
        threshold=5.0,
    )
    with pytest.raises(NotificationDeliveryError, match="smtp unavailable"):
        suppression_service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=sample_anchor(),
                    instance_id="inst-recovery-live-ack",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=9.0,
                    minutes_ago=1,
                ),
            )
        )
    suppressed_alert_id = next(
        alert_record.alert_id
        for alert_record in suppression_service.list_alerts()
        if alert_record.instance_id == "inst-recovery-live-ack"
    )
    suppression_service.acknowledge_alert(
        actor_user_id="user-ops",
        alert_id=suppressed_alert_id,
    )
    suppressed_summary = suppression_service.evaluate_samples(
        samples=(
            build_sample(
                anchor=sample_anchor() + timedelta(minutes=1),
                instance_id="inst-recovery-live-ack",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=0,
            ),
        )
    )
    suppressed_detail = suppression_service.get_alert(alert_id=suppressed_alert_id)

    assert first_dispatch == 1
    assert second_dispatch == 0
    assert first_result.status == "retry_scheduled"
    assert second_result.status == "processed"
    assert len(sink.samples) == second_result.processed_metrics
    assert recovery_summary.notified_alerts == 1
    assert [event.event_type for event in detail.history] == [
        AlertEventType.OPENED,
        AlertEventType.NOTIFICATION_FAILED,
        AlertEventType.NOTIFIED,
    ]
    assert suppressed_summary.notified_alerts == 0
    assert suppression_notifier.calls == 1
    assert suppressed_detail.history[-1].event_type is AlertEventType.NOTIFICATION_SUPPRESSED


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
        instance_id="inst-recovery-live",
        labels=("primary", "live-gate"),
        name="prod-primary-live",
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=utc_now(),
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _reset_postgres_state(postgres_dsn: str) -> None:
    with psycopg.connect(postgres_dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS schema_version")
            cursor.execute("DROP TABLE IF EXISTS alert_history")
            cursor.execute("DROP TABLE IF EXISTS alert_records")
            cursor.execute("DROP TABLE IF EXISTS alert_rules")


def _wait_for_postgres(postgres_dsn: str) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(postgres_dsn) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            return
        except psycopg.Error as error:
            last_error = error
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("PostgreSQL did not become ready for the recovery live gate.") from last_error


def _wait_for_redis(redis_url: str) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            client.ping()
            return
        except redis.RedisError as error:
            last_error = error
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("Redis did not become ready for the recovery live gate.") from last_error


def build_sample(
    *,
    anchor: datetime,
    instance_id: str,
    metric_kind: MetricKind,
    metric_name: str,
    metric_value: float,
    minutes_ago: int,
) -> MetricSample:
    return MetricSample(
        collected_at=anchor - timedelta(minutes=minutes_ago),
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        metric_kind=metric_kind,
        metric_name=metric_name,
        metric_value=metric_value,
    )


def sample_anchor() -> datetime:
    return utc_now()
