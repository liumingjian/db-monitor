from db_monitor_api.alerting.domain import AlertEventType, AlertStatus, RuleOperator, RuleSeverity
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertingService
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_sample, sample_anchor


def test_rule_engine_contract_tracks_alert_state_and_notifier_boundary() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    notifier = InMemoryNotifier()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier,
        repository=repository,
    )

    rule = service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-rule-contract",),
        metric_name="mysql_replication_lag_seconds",
        name="Replication Lag High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.CRITICAL,
        threshold=5.0,
    )
    summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-rule-contract",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=12.0,
                minutes_ago=1,
            ),
        )
    )

    alert = service.list_alerts()[0]
    detail = service.get_alert(alert_id=alert.alert_id)

    assert rule.operator is RuleOperator.GREATER_THAN
    assert rule.engine is DatabaseEngine.MYSQL
    assert summary.opened_alerts == 1
    assert detail.record.engine is DatabaseEngine.MYSQL
    assert detail.record.status is AlertStatus.OPEN
    assert [event.event_type for event in detail.history] == [
        AlertEventType.OPENED,
        AlertEventType.NOTIFIED,
    ]
    assert notifier.requests[0].rule_name == "Replication Lag High"
