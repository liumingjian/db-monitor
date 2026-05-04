from dataclasses import dataclass, replace
from datetime import datetime, timedelta
import json
import logging
import secrets
import time

from db_monitor_api.alerting.domain import (
    AlertEventType,
    AlertHistoryEvent,
    AlertRecord,
    AlertRule,
    AlertStatus,
    EvaluationSummary,
    NotificationRequest,
    RuleInstanceOverride,
    RuleOperator,
    format_alert_engine,
)
from db_monitor_api.alerting.delivery_policy import (
    build_notification_suppressed_event,
    notification_suppression_reason,
    should_record_notification_suppressed_event,
)
from db_monitor_api.alerting.noise_control import (
    AlertNoiseControlPolicy,
    build_noise_group_key,
    build_suppressed_event,
    should_record_suppressed_event,
)
from db_monitor_api.alerting.notification import NullRuleHitSink, RuleHitEvent, RuleHitSink
from db_monitor_api.alerting.notifier import Notifier
from db_monitor_api.alerting.repository import AlertingRepository
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricSample

DEFAULT_NOTIFICATION_RETRY_BACKOFF_SECONDS = 60
_EVALUATION_LOGGER = logging.getLogger("db_monitor_api.alerting.evaluation")
_MILLISECONDS_PER_SECOND = 1000


class NotificationDeliveryError(Exception):
    pass


@dataclass(frozen=True)
class NotificationRetryPolicy:
    backoff_seconds: int = DEFAULT_NOTIFICATION_RETRY_BACKOFF_SECONDS


def evaluate_samples(
    *,
    notifier: Notifier,
    noise_control_policy: AlertNoiseControlPolicy,
    organization_id: str | None,
    notification_retry_policy: NotificationRetryPolicy,
    repository: AlertingRepository,
    samples: tuple[MetricSample, ...],
    rule_hit_sink: RuleHitSink | None = None,
) -> EvaluationSummary:
    started_at = time.perf_counter()
    effective_sink: RuleHitSink = rule_hit_sink if rule_hit_sink is not None else NullRuleHitSink()
    rules = repository.list_rules(organization_id=organization_id)
    notified = 0
    opened = 0
    resolved = 0
    for rule in rules:
        if not rule.enabled:
            continue
        override_index = _index_overrides(rule.overrides)
        for sample in _matching_samples(rule=rule, samples=samples):
            counts = _evaluate_sample(
                notifier=notifier,
                noise_control_policy=noise_control_policy,
                notification_retry_policy=notification_retry_policy,
                override=override_index.get(sample.instance_id),
                repository=repository,
                rule=rule,
                rule_hit_sink=effective_sink,
                sample=sample,
            )
            notified += counts.notified_alerts
            opened += counts.opened_alerts
            resolved += counts.resolved_alerts
    duration_ms = (time.perf_counter() - started_at) * _MILLISECONDS_PER_SECOND
    _log_evaluation_completed(
        duration_ms=duration_ms,
        rule_count=len(rules),
        sample_count=len(samples),
    )
    return EvaluationSummary(
        notified_alerts=notified,
        opened_alerts=opened,
        resolved_alerts=resolved,
    )


def _index_overrides(
    overrides: tuple[RuleInstanceOverride, ...],
) -> dict[str, RuleInstanceOverride]:
    return {override.instance_id: override for override in overrides}


def _log_evaluation_completed(
    *,
    duration_ms: float,
    rule_count: int,
    sample_count: int,
) -> None:
    _EVALUATION_LOGGER.info(
        json.dumps(
            {
                "event": "rule.evaluation.completed",
                "duration_ms": round(duration_ms, 3),
                "rule_count": rule_count,
                "sample_count": sample_count,
            },
            sort_keys=True,
        )
    )


def _matching_samples(
    *,
    rule: AlertRule,
    samples: tuple[MetricSample, ...],
) -> tuple[MetricSample, ...]:
    return tuple(
        sorted(
            (
                sample
                for sample in samples
                if sample.engine is rule.engine
                and sample.metric_name == rule.metric_name
                and (not rule.instance_ids or sample.instance_id in rule.instance_ids)
            ),
            key=lambda sample: sample.collected_at,
        )
    )


def _matches(*, operator: RuleOperator, threshold: float, value: float) -> bool:
    if operator is RuleOperator.GREATER_THAN:
        return value > threshold
    if operator is RuleOperator.GREATER_THAN_OR_EQUAL:
        return value >= threshold
    if operator is RuleOperator.LESS_THAN:
        return value < threshold
    return value <= threshold


def _effective_threshold(
    *,
    override: RuleInstanceOverride | None,
    rule: AlertRule,
) -> float:
    if override is not None and override.threshold is not None:
        return override.threshold
    return rule.threshold


def _effective_enabled(
    *,
    override: RuleInstanceOverride | None,
    rule: AlertRule,
) -> bool:
    if override is not None and override.enabled is not None:
        return override.enabled
    return rule.enabled


def _evaluate_sample(
    *,
    notifier: Notifier,
    noise_control_policy: AlertNoiseControlPolicy,
    notification_retry_policy: NotificationRetryPolicy,
    override: RuleInstanceOverride | None,
    repository: AlertingRepository,
    rule: AlertRule,
    rule_hit_sink: RuleHitSink,
    sample: MetricSample,
) -> EvaluationSummary:
    if not _effective_enabled(override=override, rule=rule):
        return EvaluationSummary(notified_alerts=0, opened_alerts=0, resolved_alerts=0)
    effective_threshold = _effective_threshold(override=override, rule=rule)
    active_alert = repository.find_active_alert(
        instance_id=sample.instance_id,
        organization_id=rule.organization_id,
        rule_id=rule.rule_id,
    )
    if _matches(
        operator=rule.operator,
        threshold=effective_threshold,
        value=sample.metric_value,
    ):
        return _handle_matching_sample(
            active_alert=active_alert,
            effective_threshold=effective_threshold,
            notifier=notifier,
            noise_control_policy=noise_control_policy,
            notification_retry_policy=notification_retry_policy,
            repository=repository,
            rule=rule,
            rule_hit_sink=rule_hit_sink,
            sample=sample,
        )
    if active_alert is None:
        return EvaluationSummary(notified_alerts=0, opened_alerts=0, resolved_alerts=0)
    repository.upsert_alert(_resolve_alert(alert=active_alert, sample=sample))
    repository.append_history(
        AlertHistoryEvent(
            alert_id=active_alert.alert_id,
            detail=_recovery_message(alert=active_alert, value=sample.metric_value),
            event_type=AlertEventType.RESOLVED,
            organization_id=active_alert.organization_id,
            occurred_at=sample.collected_at,
        )
    )
    return EvaluationSummary(notified_alerts=0, opened_alerts=0, resolved_alerts=1)


def _handle_matching_sample(
    *,
    active_alert: AlertRecord | None,
    effective_threshold: float,
    notifier: Notifier,
    noise_control_policy: AlertNoiseControlPolicy,
    notification_retry_policy: NotificationRetryPolicy,
    repository: AlertingRepository,
    rule: AlertRule,
    rule_hit_sink: RuleHitSink,
    sample: MetricSample,
) -> EvaluationSummary:
    if active_alert is None:
        _open_alert(
            effective_threshold=effective_threshold,
            notifier=notifier,
            repository=repository,
            rule=rule,
            rule_hit_sink=rule_hit_sink,
            sample=sample,
        )
        return EvaluationSummary(notified_alerts=1, opened_alerts=1, resolved_alerts=0)
    refreshed_alert = _refresh_alert(alert=active_alert, sample=sample)
    repository.upsert_alert(refreshed_alert)
    history = repository.list_history(
        alert_id=refreshed_alert.alert_id,
        organization_id=refreshed_alert.organization_id,
    )
    if _should_retry_notification(
        history=history,
        retry_policy=notification_retry_policy,
        sample=sample,
    ):
        suppression_reason = notification_suppression_reason(alert=refreshed_alert)
        if suppression_reason is not None:
            _record_notification_suppressed_if_due(
                alert=refreshed_alert,
                history=history,
                repository=repository,
                sample=sample,
                suppression_reason=suppression_reason,
            )
            return EvaluationSummary(notified_alerts=0, opened_alerts=0, resolved_alerts=0)
        _deliver_notification(
            alert=refreshed_alert,
            notifier=notifier,
            occurred_at=sample.collected_at,
            repository=repository,
        )
        rule_hit_sink.submit(_build_rule_hit_event(alert=refreshed_alert, sample=sample))
        return EvaluationSummary(notified_alerts=1, opened_alerts=0, resolved_alerts=0)
    _record_suppressed_match_if_due(
        alert=refreshed_alert,
        history=history,
        noise_control_policy=noise_control_policy,
        repository=repository,
        sample=sample,
    )
    return EvaluationSummary(notified_alerts=0, opened_alerts=0, resolved_alerts=0)


def _open_alert(
    *,
    effective_threshold: float,
    notifier: Notifier,
    repository: AlertingRepository,
    rule: AlertRule,
    rule_hit_sink: RuleHitSink,
    sample: MetricSample,
) -> None:
    alert = AlertRecord(
        alert_id=f"alert-{secrets.token_hex(6)}",
        acknowledged_at=None,
        acknowledged_by_user_id=None,
        current_value=sample.metric_value,
        engine=rule.engine,
        instance_id=sample.instance_id,
        last_evaluated_at=sample.collected_at,
        metric_name=rule.metric_name,
        opened_at=sample.collected_at,
        owner_assigned_at=None,
        owner_user_id=None,
        organization_id=rule.organization_id,
        resolved_at=None,
        rule_id=rule.rule_id,
        rule_name=rule.name,
        severity=rule.severity,
        status=AlertStatus.OPEN,
        threshold=effective_threshold,
    )
    repository.upsert_alert(alert)
    repository.append_history(
        AlertHistoryEvent(
            alert_id=alert.alert_id,
            detail=_alert_message(alert=alert),
            event_type=AlertEventType.OPENED,
            organization_id=alert.organization_id,
            occurred_at=sample.collected_at,
        )
    )
    _deliver_notification(
        alert=alert,
        notifier=notifier,
        occurred_at=sample.collected_at,
        repository=repository,
    )
    rule_hit_sink.submit(_build_rule_hit_event(alert=alert, sample=sample))


def _build_rule_hit_event(*, alert: AlertRecord, sample: MetricSample) -> RuleHitEvent:
    engine_value = (
        alert.engine.value if isinstance(alert.engine, DatabaseEngine) else str(alert.engine)
    )
    severity_value = (
        alert.severity.value
        if hasattr(alert.severity, "value")
        else str(alert.severity)
    )
    return RuleHitEvent(
        rule_id=alert.rule_id,
        rule_name=alert.rule_name,
        organization_id=alert.organization_id,
        instance_id=alert.instance_id,
        engine=engine_value,
        metric_name=alert.metric_name,
        metric_value=sample.metric_value,
        threshold=alert.threshold,
        severity=severity_value,
        occurred_at=sample.collected_at,
        web_link=None,
    )


def _deliver_notification(
    *,
    alert: AlertRecord,
    notifier: Notifier,
    occurred_at: datetime,
    repository: AlertingRepository,
) -> None:
    request = NotificationRequest(
        alert_id=alert.alert_id,
        engine=alert.engine,
        instance_id=alert.instance_id,
        message=_alert_message(alert=alert),
        rule_name=alert.rule_name,
        severity=alert.severity,
    )
    try:
        notifier.send(request)
    except Exception as error:
        repository.append_history(
            AlertHistoryEvent(
                alert_id=alert.alert_id,
                detail=str(error),
                event_type=AlertEventType.NOTIFICATION_FAILED,
                organization_id=alert.organization_id,
                occurred_at=occurred_at,
            )
        )
        raise NotificationDeliveryError(str(error)) from error
    repository.append_history(
        AlertHistoryEvent(
            alert_id=alert.alert_id,
            detail=f"Notifier sent {alert.severity.value} {format_alert_engine(alert.engine)} alert.",
            event_type=AlertEventType.NOTIFIED,
            organization_id=alert.organization_id,
            occurred_at=occurred_at,
        )
    )


def _should_retry_notification(
    *,
    history: tuple[AlertHistoryEvent, ...],
    retry_policy: NotificationRetryPolicy,
    sample: MetricSample,
) -> bool:
    if any(event.event_type is AlertEventType.NOTIFIED for event in history):
        return False
    failed_events = tuple(
        event for event in history if event.event_type is AlertEventType.NOTIFICATION_FAILED
    )
    if not failed_events:
        return False
    return sample.collected_at >= failed_events[-1].occurred_at + timedelta(
        seconds=retry_policy.backoff_seconds
    )


def _refresh_alert(*, alert: AlertRecord, sample: MetricSample) -> AlertRecord:
    return replace(
        alert,
        current_value=sample.metric_value,
        last_evaluated_at=sample.collected_at,
    )


def _resolve_alert(*, alert: AlertRecord, sample: MetricSample) -> AlertRecord:
    return replace(
        alert,
        current_value=sample.metric_value,
        last_evaluated_at=sample.collected_at,
        resolved_at=sample.collected_at,
        status=AlertStatus.RESOLVED,
    )


def _alert_message(*, alert: AlertRecord) -> str:
    return (
        f"{format_alert_engine(alert.engine)} rule '{alert.rule_name}' triggered on {alert.instance_id}: "
        f"{alert.metric_name}={alert.current_value} threshold={alert.threshold}."
    )


def _recovery_message(*, alert: AlertRecord, value: float) -> str:
    return (
        f"{format_alert_engine(alert.engine)} alert recovered on {alert.instance_id}: "
        f"{alert.metric_name}={value} threshold={alert.threshold}."
    )


def _record_suppressed_match_if_due(
    *,
    alert: AlertRecord,
    history: tuple[AlertHistoryEvent, ...],
    noise_control_policy: AlertNoiseControlPolicy,
    repository: AlertingRepository,
    sample: MetricSample,
) -> None:
    if not should_record_suppressed_event(
        history=history,
        policy=noise_control_policy,
        sample=sample,
    ):
        return
    repository.append_history(
        build_suppressed_event(
            alert=alert,
            group_key=build_noise_group_key(alert=alert),
            sample=sample,
        )
    )


def _record_notification_suppressed_if_due(
    *,
    alert: AlertRecord,
    history: tuple[AlertHistoryEvent, ...],
    repository: AlertingRepository,
    sample: MetricSample,
    suppression_reason: str,
) -> None:
    if not should_record_notification_suppressed_event(alert=alert, history=history):
        return
    repository.append_history(
        build_notification_suppressed_event(
            alert=alert,
            reason=suppression_reason,
            sample=sample,
        )
    )
