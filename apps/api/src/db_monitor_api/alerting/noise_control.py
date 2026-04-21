from dataclasses import dataclass
from datetime import timedelta

from db_monitor_api.alerting.domain import (
    AlertEventType,
    AlertHistoryEvent,
    AlertRecord,
    format_alert_engine,
)
from db_monitor_pipeline.domain import MetricSample

DEFAULT_SUPPRESSION_WINDOW_SECONDS = 300


@dataclass(frozen=True)
class AlertNoiseControlPolicy:
    suppression_window_seconds: int = DEFAULT_SUPPRESSION_WINDOW_SECONDS


def build_noise_group_key(*, alert: AlertRecord) -> str:
    return f"{alert.rule_id}:{alert.instance_id}"


def build_suppressed_event(
    *,
    alert: AlertRecord,
    group_key: str,
    sample: MetricSample,
) -> AlertHistoryEvent:
    return AlertHistoryEvent(
        alert_id=alert.alert_id,
        detail=(
            f"Suppressed repeated {format_alert_engine(alert.engine)} trigger for group {group_key} "
            f"at value {sample.metric_value}."
        ),
        event_type=AlertEventType.SUPPRESSED,
        organization_id=alert.organization_id,
        occurred_at=sample.collected_at,
    )


def should_record_suppressed_event(
    *,
    history: tuple[AlertHistoryEvent, ...],
    policy: AlertNoiseControlPolicy,
    sample: MetricSample,
) -> bool:
    if not history:
        return True
    last_event_at = history[-1].occurred_at
    return sample.collected_at >= last_event_at + timedelta(
        seconds=policy.suppression_window_seconds
    )
