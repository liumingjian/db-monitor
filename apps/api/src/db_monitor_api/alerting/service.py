from dataclasses import dataclass, field
import secrets

from db_monitor_api.alerting.domain import (
    AlertDetail,
    AlertRecord,
    AlertRule,
    EvaluationSummary,
    RuleOperator,
    RuleSeverity,
)
from db_monitor_api.alerting.catalog import supports_alert_metric
from db_monitor_api.alerting.evaluation import (
    NotificationDeliveryError,
    NotificationRetryPolicy,
    evaluate_samples,
)
from db_monitor_api.alerting.noise_control import AlertNoiseControlPolicy
from db_monitor_api.alerting.notifier import Notifier
from db_monitor_api.alerting.repository import AlertingRepository
from db_monitor_api.alerting.workflow import (
    AlertWorkflowValidationError,
    acknowledge_alert,
    add_alert_note,
    assign_alert_owner,
)
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_api.control_plane.repository import ControlPlaneRepository
from db_monitor_pipeline.domain import MetricSample

__all__ = [
    "AlertingService",
    "AlertNotFoundError",
    "AlertWorkflowValidationError",
    "AlertNoiseControlPolicy",
    "NotificationDeliveryError",
    "NotificationRetryPolicy",
]

DEFAULT_ORGANIZATION_ID = "org-internal"


class AlertNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class AlertingService:
    audit_service: AuditService
    notifier: Notifier
    repository: AlertingRepository = field()
    control_plane_repository: ControlPlaneRepository | None = None
    noise_control_policy: AlertNoiseControlPolicy = field(
        default_factory=AlertNoiseControlPolicy
    )
    notification_retry_policy: NotificationRetryPolicy = field(
        default_factory=NotificationRetryPolicy
    )

    def create_rule(
        self,
        *,
        actor_user_id: str,
        enabled: bool,
        engine: DatabaseEngine,
        instance_ids: tuple[str, ...],
        metric_name: str,
        name: str,
        operator: RuleOperator,
        severity: RuleSeverity,
        threshold: float,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> AlertRule:
        self._validate_rule_metric(engine=engine, metric_name=metric_name)
        self._validate_rule_instances(
            engine=engine,
            instance_ids=instance_ids,
            organization_id=organization_id,
        )
        rule = AlertRule(
            created_at=utc_now(),
            enabled=enabled,
            engine=engine,
            instance_ids=instance_ids,
            metric_name=metric_name,
            name=name,
            organization_id=organization_id,
            operator=operator,
            rule_id=f"rule-{secrets.token_hex(6)}",
            severity=severity,
            threshold=threshold,
        )
        self.repository.create_rule(rule)
        self.audit_service.record(
            action="rules.create",
            actor_user_id=actor_user_id,
            outcome="allowed",
            resource="alert-rule",
        )
        return rule

    def evaluate_samples(
        self,
        *,
        organization_id: str | None = None,
        samples: tuple[MetricSample, ...],
    ) -> EvaluationSummary:
        return evaluate_samples(
            notifier=self.notifier,
            noise_control_policy=self.noise_control_policy,
            organization_id=organization_id,
            notification_retry_policy=self.notification_retry_policy,
            repository=self.repository,
            samples=samples,
        )

    def get_alert(
        self,
        *,
        alert_id: str,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> AlertDetail:
        alert = self.repository.get_alert(alert_id, organization_id=organization_id)
        if alert is None:
            raise AlertNotFoundError(f"Unknown alert: {alert_id}")
        return AlertDetail(
            history=self.repository.list_history(
                alert_id=alert_id,
                organization_id=organization_id,
            ),
            record=alert,
        )

    def list_alerts(
        self,
        *,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> tuple[AlertRecord, ...]:
        return self.repository.list_alerts(organization_id=organization_id)

    def list_rules(
        self,
        *,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> tuple[AlertRule, ...]:
        return self.repository.list_rules(organization_id=organization_id)

    def acknowledge_alert(
        self,
        *,
        actor_user_id: str,
        alert_id: str,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> AlertDetail:
        alert = self._require_alert(
            alert_id=alert_id,
            organization_id=organization_id,
        )
        workflow_result = acknowledge_alert(
            actor_user_id=actor_user_id,
            alert=alert,
            occurred_at=utc_now(),
        )
        if workflow_result is None:
            return self.get_alert(alert_id=alert_id, organization_id=organization_id)
        updated_alert, event = workflow_result
        self.repository.upsert_alert(updated_alert)
        self.repository.append_history(event)
        self._record_workflow_audit(action="alerts.acknowledge", actor_user_id=actor_user_id)
        return self.get_alert(alert_id=alert_id, organization_id=organization_id)

    def assign_alert_owner(
        self,
        *,
        actor_user_id: str,
        alert_id: str,
        owner_user_id: str,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> AlertDetail:
        alert = self._require_alert(
            alert_id=alert_id,
            organization_id=organization_id,
        )
        workflow_result = assign_alert_owner(
            actor_user_id=actor_user_id,
            alert=alert,
            occurred_at=utc_now(),
            owner_user_id=owner_user_id,
        )
        if workflow_result is None:
            return self.get_alert(alert_id=alert_id, organization_id=organization_id)
        updated_alert, event = workflow_result
        self.repository.upsert_alert(updated_alert)
        self.repository.append_history(event)
        self._record_workflow_audit(action="alerts.assign_owner", actor_user_id=actor_user_id)
        return self.get_alert(alert_id=alert_id, organization_id=organization_id)

    def add_alert_note(
        self,
        *,
        actor_user_id: str,
        alert_id: str,
        note: str,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> AlertDetail:
        alert = self._require_alert(
            alert_id=alert_id,
            organization_id=organization_id,
        )
        event = add_alert_note(
            actor_user_id=actor_user_id,
            alert=alert,
            note=note,
            occurred_at=utc_now(),
        )
        self.repository.append_history(event)
        self._record_workflow_audit(action="alerts.add_note", actor_user_id=actor_user_id)
        return self.get_alert(alert_id=alert_id, organization_id=organization_id)

    def _require_alert(
        self,
        *,
        alert_id: str,
        organization_id: str,
    ) -> AlertRecord:
        alert = self.repository.get_alert(
            alert_id,
            organization_id=organization_id,
        )
        if alert is None:
            raise AlertNotFoundError(f"Unknown alert: {alert_id}")
        return alert

    def _validate_rule_instances(
        self,
        *,
        engine: DatabaseEngine,
        instance_ids: tuple[str, ...],
        organization_id: str,
    ) -> None:
        if self.control_plane_repository is None:
            return
        for instance_id in instance_ids:
            instance = self.control_plane_repository.get_instance(
                instance_id,
                organization_id=organization_id,
            )
            if instance is None:
                raise AlertWorkflowValidationError(
                    f"Unknown instance in organization scope: {instance_id}"
                )
            if instance.engine is not engine:
                raise AlertWorkflowValidationError(
                    "Rule scope instance engine mismatch: "
                    f"{instance_id} is {instance.engine.value}, expected {engine.value}"
                )

    def _validate_rule_metric(
        self,
        *,
        engine: DatabaseEngine,
        metric_name: str,
    ) -> None:
        if supports_alert_metric(engine=engine, metric_name=metric_name):
            return
        raise AlertWorkflowValidationError(
            f"Unsupported alert metric for engine {engine.value}: {metric_name}"
        )

    def _record_workflow_audit(self, *, action: str, actor_user_id: str) -> None:
        self.audit_service.record(
            action=action,
            actor_user_id=actor_user_id,
            outcome="allowed",
            resource="alert",
        )
