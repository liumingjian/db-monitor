from datetime import timedelta

import pytest

from db_monitor_api.alerting.domain import AlertEventType, NotificationRequest, RuleOperator, RuleSeverity
from db_monitor_api.alerting.notifier import Notifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import (
    AlertingService,
    NotificationDeliveryError,
    NotificationRetryPolicy,
)
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_sample, sample_anchor


class FailingOnceNotifier(Notifier):
    def __init__(self) -> None:
        self.calls = 0

    def send(self, request: NotificationRequest) -> None:
        del request
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("smtp unavailable")


def test_alert_recovery_contract_retries_notification_only_after_backoff() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = FailingOnceNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        notification_retry_policy=NotificationRetryPolicy(backoff_seconds=90),
        repository=repository,
    )
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-alert-recovery",),
        metric_name="mysql_replication_lag_seconds",
        name="Replication Lag High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.CRITICAL,
        threshold=5.0,
    )

    with pytest.raises(NotificationDeliveryError, match="smtp unavailable"):
        service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    instance_id="inst-alert-recovery",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=9.0,
                    minutes_ago=2,
                ),
            )
        )

    early_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-alert-recovery",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=1,
            ),
        )
    )
    alert = service.list_alerts()[0]
    retry_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor + timedelta(minutes=1),
                instance_id="inst-alert-recovery",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=7.0,
                minutes_ago=0,
            ),
        )
    )
    detail = service.get_alert(alert_id=alert.alert_id)

    assert early_summary.notified_alerts == 0
    assert retry_summary.notified_alerts == 1
    assert notifier.calls == 2
    assert [event.event_type for event in detail.history] == [
        AlertEventType.OPENED,
        AlertEventType.NOTIFICATION_FAILED,
        AlertEventType.NOTIFIED,
    ]


def test_alert_recovery_contract_stops_retry_after_acknowledge() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = FailingOnceNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        notification_retry_policy=NotificationRetryPolicy(backoff_seconds=0),
        repository=repository,
    )
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-alert-ack-stop",),
        metric_name="mysql_replication_lag_seconds",
        name="Replication Lag High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.CRITICAL,
        threshold=5.0,
    )

    with pytest.raises(NotificationDeliveryError, match="smtp unavailable"):
        service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    instance_id="inst-alert-ack-stop",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=9.0,
                    minutes_ago=1,
                ),
            )
        )

    alert_id = service.list_alerts()[0].alert_id
    service.acknowledge_alert(actor_user_id="user-ops", alert_id=alert_id)
    retry_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor + timedelta(minutes=1),
                instance_id="inst-alert-ack-stop",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=0,
            ),
        )
    )
    detail = service.get_alert(alert_id=alert_id)

    assert retry_summary.notified_alerts == 0
    assert notifier.calls == 1
    assert detail.history[-1].event_type is AlertEventType.NOTIFICATION_SUPPRESSED


def test_alert_recovery_contract_retries_oracle_notification_only_after_backoff() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = FailingOnceNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        notification_retry_policy=NotificationRetryPolicy(backoff_seconds=90),
        repository=repository,
    )
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.ORACLE,
        instance_ids=("inst-alert-oracle-recovery",),
        metric_name="oracle_sessions_active",
        name="Oracle Sessions Active High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=6.0,
    )

    with pytest.raises(NotificationDeliveryError, match="smtp unavailable"):
        service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    engine=DatabaseEngine.ORACLE,
                    instance_id="inst-alert-oracle-recovery",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="oracle_sessions_active",
                    metric_value=8.0,
                    minutes_ago=2,
                ),
            )
        )

    early_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-alert-oracle-recovery",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=7.0,
                minutes_ago=1,
            ),
        )
    )
    alert = service.list_alerts()[0]
    retry_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor + timedelta(minutes=1),
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-alert-oracle-recovery",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=9.0,
                minutes_ago=0,
            ),
        )
    )
    detail = service.get_alert(alert_id=alert.alert_id)

    assert early_summary.notified_alerts == 0
    assert retry_summary.notified_alerts == 1
    assert alert.engine is DatabaseEngine.ORACLE
    assert notifier.calls == 2
    assert [event.event_type for event in detail.history] == [
        AlertEventType.OPENED,
        AlertEventType.NOTIFICATION_FAILED,
        AlertEventType.NOTIFIED,
    ]
