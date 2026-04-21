from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import FastAPI

from db_monitor_api.alerting.domain import (
    AlertEventType,
    AlertHistoryEvent,
    AlertRecord,
    AlertRule,
    AlertStatus,
    RuleOperator,
    RuleSeverity,
)
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.analytics.repository import InMemoryAnalyticsRepository
from db_monitor_api.app import create_app
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    MySQLConnectionConfig,
    MySQLInstance,
    SystemSetting,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.domain import MetricKind, MetricSample

INSTANCE_ID = "inst-prod-primary"


class SmokeMySQLConnectionValidator:
    def validate(self, config: MySQLConnectionConfig) -> ConnectionValidation:
        return ConnectionValidation(
            checked_at=utc_now(),
            detail=f"Smoke validation passed for {config.host}:{config.port}.",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        )


def build_smoke_app() -> FastAPI:
    anchor = utc_now()
    control_plane_repository = InMemoryControlPlaneRepository()
    analytics_repository = InMemoryAnalyticsRepository(samples=_build_metric_samples(anchor))
    alerting_repository = InMemoryAlertingRepository()
    control_plane_repository.create_instance(_build_instance(anchor))
    control_plane_repository.upsert_setting(
        SystemSetting(
            key="notification.channel",
            organization_id="org-internal",
            updated_at=anchor,
            value="email",
        )
    )
    _seed_alerting(alerting_repository=alerting_repository, anchor=anchor)
    return create_app(
        runtime=build_local_runtime(
            analytics_repository=analytics_repository,
            alerting_repository=alerting_repository,
            control_plane_repository=control_plane_repository,
            mysql_validator=SmokeMySQLConnectionValidator(),
        )
    )


def _build_instance(anchor: datetime) -> MySQLInstance:
    return MySQLInstance(
        connection=MySQLConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=anchor - timedelta(minutes=15),
        environment="prod",
        instance_id=INSTANCE_ID,
        labels=("primary", "critical"),
        name="prod-primary",
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=anchor - timedelta(minutes=15),
            detail="Smoke instance is ready.",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )


def _build_metric_samples(anchor: datetime) -> tuple[MetricSample, ...]:
    samples: list[MetricSample] = []
    for minutes_ago, values in (
        (
            15,
            {
                "mysql_server_available": (MetricKind.GAUGE, 1),
                "mysql_threads_connected": (MetricKind.GAUGE, 16),
                "mysql_threads_running": (MetricKind.GAUGE, 3),
                "mysql_queries_total": (MetricKind.COUNTER, 120),
                "mysql_bytes_received_total": (MetricKind.COUNTER, 1000),
                "mysql_bytes_sent_total": (MetricKind.COUNTER, 1800),
                "mysql_innodb_buffer_pool_reads_total": (MetricKind.COUNTER, 40),
                "mysql_replication_lag_seconds": (MetricKind.GAUGE, 3),
                "mysql_uptime_seconds": (MetricKind.GAUGE, 1200),
            },
        ),
        (
            10,
            {
                "mysql_server_available": (MetricKind.GAUGE, 1),
                "mysql_threads_connected": (MetricKind.GAUGE, 18),
                "mysql_threads_running": (MetricKind.GAUGE, 4),
                "mysql_queries_total": (MetricKind.COUNTER, 180),
                "mysql_bytes_received_total": (MetricKind.COUNTER, 1400),
                "mysql_bytes_sent_total": (MetricKind.COUNTER, 2400),
                "mysql_innodb_buffer_pool_reads_total": (MetricKind.COUNTER, 70),
                "mysql_replication_lag_seconds": (MetricKind.GAUGE, 4),
                "mysql_uptime_seconds": (MetricKind.GAUGE, 1500),
            },
        ),
        (
            5,
            {
                "mysql_server_available": (MetricKind.GAUGE, 1),
                "mysql_threads_connected": (MetricKind.GAUGE, 20),
                "mysql_threads_running": (MetricKind.GAUGE, 4),
                "mysql_queries_total": (MetricKind.COUNTER, 240),
                "mysql_bytes_received_total": (MetricKind.COUNTER, 1950),
                "mysql_bytes_sent_total": (MetricKind.COUNTER, 3200),
                "mysql_innodb_buffer_pool_reads_total": (MetricKind.COUNTER, 115),
                "mysql_replication_lag_seconds": (MetricKind.GAUGE, 5),
                "mysql_uptime_seconds": (MetricKind.GAUGE, 1800),
            },
        ),
    ):
        for metric_name, (metric_kind, metric_value) in values.items():
            samples.append(
                MetricSample(
                    collected_at=anchor - timedelta(minutes=minutes_ago),
                    environment="prod",
                    instance_id=INSTANCE_ID,
                    labels=("primary", "critical"),
                    metric_kind=metric_kind,
                    metric_name=metric_name,
                    metric_value=metric_value,
                )
            )
    return tuple(samples)


def _seed_alerting(
    *,
    alerting_repository: InMemoryAlertingRepository,
    anchor: datetime,
) -> None:
    alerting_repository.create_rule(
        AlertRule(
            created_at=anchor - timedelta(minutes=6),
            enabled=True,
            engine=DatabaseEngine.MYSQL,
            instance_ids=(INSTANCE_ID,),
            metric_name="mysql_replication_lag_seconds",
            name="Replication Lag High",
            organization_id="org-internal",
            operator=RuleOperator.GREATER_THAN,
            rule_id="rule-lag",
            severity=RuleSeverity.CRITICAL,
            threshold=5,
        )
    )
    alerting_repository.upsert_alert(
        AlertRecord(
            alert_id="alert-lag",
            acknowledged_at=None,
            acknowledged_by_user_id=None,
            current_value=8.0,
            engine=DatabaseEngine.MYSQL,
            instance_id=INSTANCE_ID,
            last_evaluated_at=anchor,
            metric_name="mysql_replication_lag_seconds",
            opened_at=anchor - timedelta(minutes=5),
            owner_assigned_at=None,
            owner_user_id=None,
            organization_id="org-internal",
            resolved_at=None,
            rule_id="rule-lag",
            rule_name="Replication Lag High",
            severity=RuleSeverity.CRITICAL,
            status=AlertStatus.OPEN,
            threshold=5.0,
        )
    )
    alerting_repository.append_history(
        AlertHistoryEvent(
            alert_id="alert-lag",
            detail=(
                "MySQL rule 'Replication Lag High' triggered on inst-prod-primary: "
                "mysql_replication_lag_seconds=8.0 threshold=5.0."
            ),
            event_type=AlertEventType.OPENED,
            organization_id="org-internal",
            occurred_at=anchor - timedelta(minutes=5),
        )
    )
    alerting_repository.append_history(
        AlertHistoryEvent(
            alert_id="alert-lag",
            detail="Notifier sent critical MySQL alert.",
            event_type=AlertEventType.NOTIFIED,
            organization_id="org-internal",
            occurred_at=anchor - timedelta(minutes=5),
        )
    )


app = build_smoke_app()
