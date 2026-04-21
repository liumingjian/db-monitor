from dataclasses import replace
from datetime import datetime

from db_monitor_api.alerting.domain import AlertEventType, AlertHistoryEvent, AlertRecord, AlertStatus


class AlertWorkflowValidationError(Exception):
    pass


def acknowledge_alert(
    *,
    actor_user_id: str,
    alert: AlertRecord,
    occurred_at: datetime,
) -> tuple[AlertRecord, AlertHistoryEvent] | None:
    if alert.status is AlertStatus.RESOLVED:
        raise AlertWorkflowValidationError("Resolved alerts cannot be acknowledged.")
    if alert.status is AlertStatus.ACKNOWLEDGED:
        if alert.acknowledged_by_user_id == actor_user_id:
            return None
        raise AlertWorkflowValidationError(
            f"Alert is already acknowledged by {alert.acknowledged_by_user_id}."
        )
    updated_alert = replace(
        alert,
        acknowledged_at=occurred_at,
        acknowledged_by_user_id=actor_user_id,
        status=AlertStatus.ACKNOWLEDGED,
    )
    return updated_alert, AlertHistoryEvent(
        alert_id=alert.alert_id,
        detail=f"Acknowledged by {actor_user_id}.",
        event_type=AlertEventType.ACKNOWLEDGED,
        organization_id=alert.organization_id,
        occurred_at=occurred_at,
    )


def assign_alert_owner(
    *,
    actor_user_id: str,
    alert: AlertRecord,
    occurred_at: datetime,
    owner_user_id: str,
) -> tuple[AlertRecord, AlertHistoryEvent] | None:
    if alert.status is AlertStatus.RESOLVED:
        raise AlertWorkflowValidationError("Resolved alerts cannot be reassigned.")
    if alert.owner_user_id == owner_user_id:
        return None
    updated_alert = replace(
        alert,
        owner_assigned_at=occurred_at,
        owner_user_id=owner_user_id,
    )
    return updated_alert, AlertHistoryEvent(
        alert_id=alert.alert_id,
        detail=f"Owner assigned to {owner_user_id} by {actor_user_id}.",
        event_type=AlertEventType.OWNER_ASSIGNED,
        organization_id=alert.organization_id,
        occurred_at=occurred_at,
    )


def add_alert_note(
    *,
    actor_user_id: str,
    alert: AlertRecord,
    note: str,
    occurred_at: datetime,
) -> AlertHistoryEvent:
    stripped_note = note.strip()
    if not stripped_note:
        raise AlertWorkflowValidationError("Alert notes cannot be empty.")
    return AlertHistoryEvent(
        alert_id=alert.alert_id,
        detail=f"{actor_user_id}: {stripped_note}",
        event_type=AlertEventType.NOTE_ADDED,
        organization_id=alert.organization_id,
        occurred_at=occurred_at,
    )
