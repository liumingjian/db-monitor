import pytest

from db_monitor_api.alerting.domain import AlertEventType, RuleOperator, RuleSeverity
from db_monitor_api.alerting.domain import NotificationRequest
from db_monitor_api.alerting.notifier import InMemoryNotifier, Notifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertingService, NotificationDeliveryError
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_sample, sample_anchor


class FailingNotifier(Notifier):
    def __init__(self) -> None:
        self.requests: list[NotificationRequest] = []

    def send(self, request: NotificationRequest) -> None:
        self.requests.append(request)
        raise RuntimeError("smtp unavailable")


def test_notifier_lifecycle_exposes_delivery_failures_and_persists_history() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = FailingNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        repository=repository,
    )
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-notifier",),
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
                    instance_id="inst-notifier",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=9.0,
                    minutes_ago=1,
                ),
            )
        )

    alert = service.list_alerts()[0]
    detail = service.get_alert(alert_id=alert.alert_id)

    assert detail.history[-1].event_type is AlertEventType.NOTIFICATION_FAILED
    assert detail.history[-1].detail == "smtp unavailable"
    assert notifier.requests[0].engine is DatabaseEngine.MYSQL
    assert notifier.requests[0].message == (
        "MySQL rule 'Replication Lag High' triggered on inst-notifier: "
        "mysql_replication_lag_seconds=9.0 threshold=5.0."
    )


def test_notifier_lifecycle_carries_oracle_engine_context_in_request() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = InMemoryNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        repository=repository,
    )
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.ORACLE,
        instance_ids=("inst-notifier-oracle",),
        metric_name="oracle_sessions_active",
        name="Oracle Sessions Active High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=6.0,
    )

    summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-notifier-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=9.0,
                minutes_ago=1,
            ),
        )
    )

    alert = service.list_alerts()[0]
    detail = service.get_alert(alert_id=alert.alert_id)

    assert summary.notified_alerts == 1
    assert notifier.requests[0].engine is DatabaseEngine.ORACLE
    assert notifier.requests[0].message == (
        "Oracle rule 'Oracle Sessions Active High' triggered on inst-notifier-oracle: "
        "oracle_sessions_active=9.0 threshold=6.0."
    )
    assert detail.history[-1].event_type is AlertEventType.NOTIFIED
    assert detail.history[-1].detail == "Notifier sent warning Oracle alert."
