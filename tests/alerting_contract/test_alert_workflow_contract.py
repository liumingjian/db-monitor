from db_monitor_api.alerting.domain import AlertEventType, AlertStatus, RuleOperator, RuleSeverity
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertingService
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_sample, sample_anchor


def test_alert_workflow_contract_tracks_ack_owner_and_note_on_active_alert() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=InMemoryNotifier(),
        repository=repository,
    )
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-alert-contract",),
        metric_name="mysql_replication_lag_seconds",
        name="Replication Lag High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.CRITICAL,
        threshold=5.0,
    )

    service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-alert-contract",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=9.0,
                minutes_ago=2,
            ),
        )
    )
    alert = service.list_alerts()[0]

    service.acknowledge_alert(actor_user_id="user-ops", alert_id=alert.alert_id)
    service.assign_alert_owner(
        actor_user_id="user-admin",
        alert_id=alert.alert_id,
        owner_user_id="user-ops",
    )
    detail = service.add_alert_note(
        actor_user_id="user-ops",
        alert_id=alert.alert_id,
        note="Investigating replication lag.",
    )

    assert detail.record.status is AlertStatus.ACKNOWLEDGED
    assert detail.record.acknowledged_by_user_id == "user-ops"
    assert detail.record.owner_user_id == "user-ops"
    assert [event.event_type for event in detail.history[-3:]] == [
        AlertEventType.ACKNOWLEDGED,
        AlertEventType.OWNER_ASSIGNED,
        AlertEventType.NOTE_ADDED,
    ]


def test_alert_workflow_contract_reuses_acknowledged_alert_in_rule_evaluation() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    service = AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=InMemoryNotifier(),
        repository=repository,
    )
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-alert-active",),
        metric_name="mysql_threads_running",
        name="Threads Running High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=4.0,
    )

    service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-alert-active",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=6.0,
                minutes_ago=2,
            ),
        )
    )
    alert = service.list_alerts()[0]
    service.acknowledge_alert(actor_user_id="user-ops", alert_id=alert.alert_id)
    summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-alert-active",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=7.0,
                minutes_ago=1,
            ),
        )
    )

    alerts = service.list_alerts()

    assert summary.opened_alerts == 0
    assert len(alerts) == 1
    assert alerts[0].status is AlertStatus.ACKNOWLEDGED
