from dataclasses import dataclass, field, replace
from datetime import datetime
import secrets

from db_monitor_api.alerting.domain import (
    AlertDetail,
    AlertRecord,
    AlertRule,
    AlertStatus,
    EvaluationSummary,
    RuleInstanceOverride,
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
from db_monitor_api.alerting.notification import NullRuleHitSink, RuleHitSink
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
    "OverrideDraft",
    "RuleNotFoundError",
]

DEFAULT_ORGANIZATION_ID = "org-internal"


class AlertNotFoundError(Exception):
    pass


class RuleNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class OverrideDraft:
    instance_id: str
    enabled: bool | None = None
    threshold: float | None = None


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
    rule_hit_sink: RuleHitSink = field(default_factory=NullRuleHitSink)

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
        overrides: tuple[OverrideDraft, ...] = (),
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
            organization_id=organization_id,
            outcome="allowed",
            resource="alert-rule",
        )
        if overrides:
            self.replace_rule_overrides(
                actor_user_id=actor_user_id,
                organization_id=organization_id,
                overrides=overrides,
                rule_id=rule.rule_id,
            )
        return self.get_rule(rule_id=rule.rule_id, organization_id=organization_id)

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
            rule_hit_sink=self.rule_hit_sink,
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
        instance: str | None = None,
        opened_after: datetime | None = None,
        opened_before: datetime | None = None,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
        severity: RuleSeverity | None = None,
        status: AlertStatus | None = None,
    ) -> tuple[AlertRecord, ...]:
        alerts = self.repository.list_alerts(organization_id=organization_id)
        return tuple(
            alert
            for alert in alerts
            if _matches_alert_filters(
                alert=alert,
                instance=instance,
                opened_after=opened_after,
                opened_before=opened_before,
                severity=severity,
                status=status,
            )
        )

    def list_rules(
        self,
        *,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> tuple[AlertRule, ...]:
        return self.repository.list_rules(organization_id=organization_id)

    def get_rule(
        self,
        *,
        rule_id: str,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> AlertRule:
        rule = self.repository.get_rule(rule_id, organization_id=organization_id)
        if rule is None:
            raise RuleNotFoundError(f"Unknown rule: {rule_id}")
        return rule

    def update_rule(
        self,
        *,
        actor_user_id: str,
        enabled: bool,
        engine: DatabaseEngine,
        instance_ids: tuple[str, ...],
        metric_name: str,
        name: str,
        operator: RuleOperator,
        overrides: tuple[OverrideDraft, ...],
        rule_id: str,
        severity: RuleSeverity,
        threshold: float,
        organization_id: str = DEFAULT_ORGANIZATION_ID,
    ) -> AlertRule:
        existing = self.get_rule(rule_id=rule_id, organization_id=organization_id)
        self._validate_rule_metric(engine=engine, metric_name=metric_name)
        self._validate_rule_instances(
            engine=engine,
            instance_ids=instance_ids,
            organization_id=organization_id,
        )
        updated = replace(
            existing,
            enabled=enabled,
            engine=engine,
            instance_ids=instance_ids,
            metric_name=metric_name,
            name=name,
            operator=operator,
            severity=severity,
            threshold=threshold,
            overrides=(),
        )
        self.repository.update_rule(updated)
        self.audit_service.record(
            action="rules.update",
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            outcome="allowed",
            resource=f"alert-rule:{rule_id}",
        )
        self.replace_rule_overrides(
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            overrides=overrides,
            rule_id=rule_id,
        )
        return self.get_rule(rule_id=rule_id, organization_id=organization_id)

    def upsert_rule_override(
        self,
        *,
        actor_user_id: str,
        enabled: bool | None,
        instance_id: str,
        organization_id: str,
        rule_id: str,
        threshold: float | None,
    ) -> RuleInstanceOverride:
        rule = self.get_rule(rule_id=rule_id, organization_id=organization_id)
        self._validate_override_instance(
            engine=rule.engine,
            instance_id=instance_id,
            organization_id=organization_id,
        )
        override = RuleInstanceOverride(
            enabled=enabled,
            instance_id=instance_id,
            rule_id=rule.rule_id,
            threshold=threshold,
            updated_at=utc_now(),
        )
        self.repository.upsert_override(override)
        self.audit_service.record(
            action="rules.override.upsert",
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            outcome="allowed",
            resource=f"alert-rule:{rule.rule_id}:instance:{instance_id}",
        )
        return override

    def delete_rule_override(
        self,
        *,
        actor_user_id: str,
        instance_id: str,
        organization_id: str,
        rule_id: str,
    ) -> bool:
        rule = self.get_rule(rule_id=rule_id, organization_id=organization_id)
        deleted = self.repository.delete_override(
            instance_id=instance_id,
            rule_id=rule.rule_id,
        )
        if deleted:
            self.audit_service.record(
                action="rules.override.delete",
                actor_user_id=actor_user_id,
                organization_id=organization_id,
                outcome="allowed",
                resource=f"alert-rule:{rule.rule_id}:instance:{instance_id}",
            )
        return deleted

    def replace_rule_overrides(
        self,
        *,
        actor_user_id: str,
        organization_id: str,
        overrides: tuple[OverrideDraft, ...],
        rule_id: str,
    ) -> tuple[RuleInstanceOverride, ...]:
        rule = self.get_rule(rule_id=rule_id, organization_id=organization_id)
        existing = {override.instance_id for override in rule.overrides}
        desired = {draft.instance_id for draft in overrides}
        for instance_id in existing - desired:
            self.delete_rule_override(
                actor_user_id=actor_user_id,
                instance_id=instance_id,
                organization_id=organization_id,
                rule_id=rule.rule_id,
            )
        applied: list[RuleInstanceOverride] = []
        for draft in overrides:
            applied.append(
                self.upsert_rule_override(
                    actor_user_id=actor_user_id,
                    enabled=draft.enabled,
                    instance_id=draft.instance_id,
                    organization_id=organization_id,
                    rule_id=rule.rule_id,
                    threshold=draft.threshold,
                )
            )
        return tuple(applied)

    def _validate_override_instance(
        self,
        *,
        engine: DatabaseEngine,
        instance_id: str,
        organization_id: str,
    ) -> None:
        if self.control_plane_repository is None:
            return
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
                "Rule override instance engine mismatch: "
                f"{instance_id} is {instance.engine.value}, expected {engine.value}"
            )

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
        self._record_workflow_audit(
            action="alerts.acknowledge",
            actor_user_id=actor_user_id,
            organization_id=organization_id,
        )
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
        self._record_workflow_audit(
            action="alerts.assign_owner",
            actor_user_id=actor_user_id,
            organization_id=organization_id,
        )
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
        self._record_workflow_audit(
            action="alerts.add_note",
            actor_user_id=actor_user_id,
            organization_id=organization_id,
        )
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

    def _record_workflow_audit(
        self,
        *,
        action: str,
        actor_user_id: str,
        organization_id: str,
    ) -> None:
        self.audit_service.record(
            action=action,
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            outcome="allowed",
            resource="alert",
        )


def _matches_alert_filters(
    *,
    alert: AlertRecord,
    instance: str | None,
    opened_after: datetime | None,
    opened_before: datetime | None,
    severity: RuleSeverity | None,
    status: AlertStatus | None,
) -> bool:
    if status is not None and alert.status is not status:
        return False
    if severity is not None and alert.severity is not severity:
        return False
    if instance is not None and instance.strip():
        if instance.strip().casefold() not in alert.instance_id.casefold():
            return False
    if opened_after is not None and alert.opened_at < _normalize_filter_timestamp(opened_after):
        return False
    if opened_before is not None and alert.opened_at > _normalize_filter_timestamp(opened_before):
        return False
    return True


def _normalize_filter_timestamp(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value
    return value.astimezone()
