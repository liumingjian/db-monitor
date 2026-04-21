from db_monitor_api.alerting.domain import AlertEventType, AlertStatus, RuleOperator, RuleSeverity
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertingService
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_sample, sample_anchor


def test_rule_engine_evaluate_opens_then_resolves_without_duplicate_notifications() -> None:
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
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-rule-evaluate",),
        metric_name="mysql_threads_running",
        name="Threads Running High",
        operator=RuleOperator.GREATER_THAN_OR_EQUAL,
        severity=RuleSeverity.WARNING,
        threshold=4.0,
    )

    open_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-rule-evaluate",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=5.0,
                minutes_ago=2,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-rule-evaluate",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=6.0,
                minutes_ago=1,
            ),
        )
    )
    resolve_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-rule-evaluate",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=2.0,
                minutes_ago=0,
            ),
        )
    )

    alert = service.list_alerts()[0]

    assert open_summary.opened_alerts == 1
    assert open_summary.notified_alerts == 1
    assert resolve_summary.resolved_alerts == 1
    assert alert.status is AlertStatus.RESOLVED
    assert len(notifier.requests) == 1


def test_rule_engine_evaluate_oracle_metric_opens_then_resolves_without_duplicate_notifications() -> (
    None
):
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
        instance_ids=("inst-rule-oracle",),
        metric_name="oracle_sessions_active",
        name="Oracle Sessions Active High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=6.0,
    )

    open_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-rule-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=8.0,
                minutes_ago=2,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-rule-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=9.0,
                minutes_ago=1,
            ),
        )
    )
    resolve_summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-rule-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=4.0,
                minutes_ago=0,
            ),
        )
    )

    alert = service.list_alerts()[0]
    detail = service.get_alert(alert_id=alert.alert_id)

    assert open_summary.opened_alerts == 1
    assert open_summary.notified_alerts == 1
    assert resolve_summary.resolved_alerts == 1
    assert alert.engine is DatabaseEngine.ORACLE
    assert alert.status is AlertStatus.RESOLVED
    assert len(notifier.requests) == 1
    assert detail.history[-1].event_type is AlertEventType.RESOLVED
    assert detail.history[-1].detail == (
        "Oracle alert recovered on inst-rule-oracle: oracle_sessions_active=4.0 threshold=6.0."
    )
