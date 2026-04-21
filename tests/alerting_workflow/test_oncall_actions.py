import pytest

from db_monitor_api.alerting.domain import RuleOperator, RuleSeverity
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertWorkflowValidationError, AlertingService
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_sample, sample_anchor


def test_oncall_actions_are_retry_safe_for_same_acknowledger_and_owner() -> None:
    service = _build_service()
    alert_id = _open_alert(service=service, instance_id="inst-oncall-retry")

    first_ack = service.acknowledge_alert(actor_user_id="user-ops", alert_id=alert_id)
    second_ack = service.acknowledge_alert(actor_user_id="user-ops", alert_id=alert_id)
    first_owner = service.assign_alert_owner(
        actor_user_id="user-admin",
        alert_id=alert_id,
        owner_user_id="user-ops",
    )
    second_owner = service.assign_alert_owner(
        actor_user_id="user-admin",
        alert_id=alert_id,
        owner_user_id="user-ops",
    )

    assert len(first_ack.history) == len(second_ack.history)
    assert len(first_owner.history) == len(second_owner.history)
    assert second_owner.record.owner_user_id == "user-ops"


def test_oncall_actions_reject_acknowledging_resolved_alerts() -> None:
    service = _build_service()
    alert_id = _open_alert(service=service, instance_id="inst-oncall-resolved")

    service.evaluate_samples(
        samples=(
            build_sample(
                anchor=sample_anchor(),
                instance_id="inst-oncall-resolved",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=1.0,
                minutes_ago=0,
            ),
        )
    )

    with pytest.raises(
        AlertWorkflowValidationError,
        match="Resolved alerts cannot be acknowledged.",
    ):
        service.acknowledge_alert(actor_user_id="user-ops", alert_id=alert_id)


def test_oncall_actions_preserve_oracle_alert_context() -> None:
    service = _build_service()
    alert_id = _open_alert(
        service=service,
        engine=DatabaseEngine.ORACLE,
        instance_id="inst-oncall-oracle",
        metric_name="oracle_sessions_active",
        name="Oracle Sessions Active High",
        threshold=6.0,
    )

    acknowledged = service.acknowledge_alert(
        actor_user_id="user-dba",
        alert_id=alert_id,
    )
    owned = service.assign_alert_owner(
        actor_user_id="user-admin",
        alert_id=alert_id,
        owner_user_id="user-dba",
    )

    assert acknowledged.record.engine is DatabaseEngine.ORACLE
    assert acknowledged.history[0].detail == (
        "Oracle rule 'Oracle Sessions Active High' triggered on inst-oncall-oracle: "
        "oracle_sessions_active=8.0 threshold=6.0."
    )
    assert owned.record.engine is DatabaseEngine.ORACLE
    assert owned.record.owner_user_id == "user-dba"


def _build_service() -> AlertingService:
    return AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=InMemoryNotifier(),
        repository=InMemoryAlertingRepository(),
    )


def _open_alert(
    *,
    service: AlertingService,
    engine: DatabaseEngine = DatabaseEngine.MYSQL,
    instance_id: str,
    metric_name: str = "mysql_replication_lag_seconds",
    name: str = "Replication Lag High",
    threshold: float = 5.0,
) -> str:
    anchor = sample_anchor()
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=engine,
        instance_ids=(instance_id,),
        metric_name=metric_name,
        name=name,
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.CRITICAL,
        threshold=threshold,
    )
    service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name=metric_name,
                metric_value=8.0,
                minutes_ago=1,
            ),
        )
    )
    return service.list_alerts()[0].alert_id
