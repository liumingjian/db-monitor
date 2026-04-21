from datetime import timedelta

import pytest

from db_monitor_api.alerting.domain import (
    AlertEventType,
    NotificationRequest,
    RuleOperator,
    RuleSeverity,
)
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


def test_delivery_policy_suppresses_retry_after_acknowledge() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = FailingOnceNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        notification_retry_policy=NotificationRetryPolicy(backoff_seconds=0),
        repository=repository,
    )
    _create_rule(service=service, instance_id="inst-delivery-ack")

    with pytest.raises(NotificationDeliveryError, match="smtp unavailable"):
        service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    instance_id="inst-delivery-ack",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=9.0,
                    minutes_ago=1,
                ),
            )
        )

    alert = service.list_alerts()[0]
    service.acknowledge_alert(actor_user_id="user-ops", alert_id=alert.alert_id)
    retry_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor + timedelta(minutes=1),
                instance_id="inst-delivery-ack",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=0,
            ),
        )
    )
    detail = service.get_alert(alert_id=alert.alert_id)

    assert retry_summary.notified_alerts == 0
    assert notifier.calls == 1
    assert [event.event_type for event in detail.history] == [
        AlertEventType.OPENED,
        AlertEventType.NOTIFICATION_FAILED,
        AlertEventType.ACKNOWLEDGED,
        AlertEventType.NOTIFICATION_SUPPRESSED,
    ]
    assert detail.history[-1].detail == (
        "MySQL notification retry suppressed because alert is acknowledged by user-ops."
    )


def test_delivery_policy_suppresses_retry_after_owner_assignment() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = FailingOnceNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        notification_retry_policy=NotificationRetryPolicy(backoff_seconds=0),
        repository=repository,
    )
    _create_rule(service=service, instance_id="inst-delivery-owner")

    with pytest.raises(NotificationDeliveryError, match="smtp unavailable"):
        service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    instance_id="inst-delivery-owner",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=9.0,
                    minutes_ago=1,
                ),
            )
        )

    alert = service.list_alerts()[0]
    service.assign_alert_owner(
        actor_user_id="user-admin",
        alert_id=alert.alert_id,
        owner_user_id="user-ops",
    )
    retry_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor + timedelta(minutes=1),
                instance_id="inst-delivery-owner",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=0,
            ),
        )
    )
    detail = service.get_alert(alert_id=alert.alert_id)

    assert retry_summary.notified_alerts == 0
    assert notifier.calls == 1
    assert detail.history[-1].event_type is AlertEventType.NOTIFICATION_SUPPRESSED
    assert detail.history[-1].detail == (
        "MySQL notification retry suppressed because alert is owned by user-ops."
    )


def test_delivery_policy_suppresses_oracle_retry_after_owner_assignment() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = FailingOnceNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        notification_retry_policy=NotificationRetryPolicy(backoff_seconds=0),
        repository=repository,
    )
    _create_rule(
        service=service,
        engine=DatabaseEngine.ORACLE,
        instance_id="inst-delivery-oracle-owner",
        metric_name="oracle_sessions_active",
        name="Oracle Sessions Active High",
        severity=RuleSeverity.WARNING,
        threshold=6.0,
    )

    with pytest.raises(NotificationDeliveryError, match="smtp unavailable"):
        service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    engine=DatabaseEngine.ORACLE,
                    instance_id="inst-delivery-oracle-owner",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="oracle_sessions_active",
                    metric_value=9.0,
                    minutes_ago=1,
                ),
            )
        )

    alert = service.list_alerts()[0]
    service.assign_alert_owner(
        actor_user_id="user-admin",
        alert_id=alert.alert_id,
        owner_user_id="user-ops",
    )
    retry_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor + timedelta(minutes=1),
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-delivery-oracle-owner",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=8.0,
                minutes_ago=0,
            ),
        )
    )
    detail = service.get_alert(alert_id=alert.alert_id)

    assert retry_summary.notified_alerts == 0
    assert notifier.calls == 1
    assert detail.history[-1].event_type is AlertEventType.NOTIFICATION_SUPPRESSED
    assert detail.history[-1].detail == (
        "Oracle notification retry suppressed because alert is owned by user-ops."
    )


def _create_rule(
    *,
    service: AlertingService,
    engine: DatabaseEngine = DatabaseEngine.MYSQL,
    instance_id: str,
    metric_name: str = "mysql_replication_lag_seconds",
    name: str = "Replication Lag High",
    severity: RuleSeverity = RuleSeverity.CRITICAL,
    threshold: float = 5.0,
) -> None:
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=engine,
        instance_ids=(instance_id,),
        metric_name=metric_name,
        name=name,
        operator=RuleOperator.GREATER_THAN,
        severity=severity,
        threshold=threshold,
    )
