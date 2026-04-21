from db_monitor_api.alerting.domain import (
    AlertEventType,
    AlertHistoryEvent,
    AlertRecord,
    AlertStatus,
    format_alert_engine,
)
from db_monitor_pipeline.domain import MetricSample


def notification_suppression_reason(*, alert: AlertRecord) -> str | None:
    engine_label = format_alert_engine(alert.engine)
    if alert.status is AlertStatus.ACKNOWLEDGED and alert.acknowledged_by_user_id is not None:
        return (
            f"{engine_label} notification retry suppressed because alert is acknowledged by "
            f"{alert.acknowledged_by_user_id}."
        )
    if alert.owner_user_id is not None:
        return f"{engine_label} notification retry suppressed because alert is owned by {alert.owner_user_id}."
    return None


def should_record_notification_suppressed_event(
    *,
    alert: AlertRecord,
    history: tuple[AlertHistoryEvent, ...],
) -> bool:
    control_edge = max(
        timestamp
        for timestamp in (alert.acknowledged_at, alert.owner_assigned_at)
        if timestamp is not None
    )
    return not any(
        event.event_type is AlertEventType.NOTIFICATION_SUPPRESSED
        and event.occurred_at >= control_edge
        for event in history
    )


def build_notification_suppressed_event(
    *,
    alert: AlertRecord,
    reason: str,
    sample: MetricSample,
) -> AlertHistoryEvent:
    return AlertHistoryEvent(
        alert_id=alert.alert_id,
        detail=reason,
        event_type=AlertEventType.NOTIFICATION_SUPPRESSED,
        organization_id=alert.organization_id,
        occurred_at=sample.collected_at,
    )
