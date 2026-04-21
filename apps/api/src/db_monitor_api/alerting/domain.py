from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from db_monitor_api.control_plane.domain import DatabaseEngine


class AlertEventType(StrEnum):
    ACKNOWLEDGED = "acknowledged"
    NOTIFICATION_FAILED = "notification_failed"
    NOTIFICATION_SUPPRESSED = "notification_suppressed"
    NOTIFIED = "notified"
    NOTE_ADDED = "note_added"
    OPENED = "opened"
    OWNER_ASSIGNED = "owner_assigned"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertStatus(StrEnum):
    ACKNOWLEDGED = "acknowledged"
    OPEN = "open"
    RESOLVED = "resolved"


class RuleOperator(StrEnum):
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"


class RuleSeverity(StrEnum):
    CRITICAL = "critical"
    WARNING = "warning"


def format_alert_engine(engine: DatabaseEngine) -> str:
    return "Oracle" if engine is DatabaseEngine.ORACLE else "MySQL"


@dataclass(frozen=True)
class AlertRule:
    created_at: datetime
    enabled: bool
    engine: DatabaseEngine
    instance_ids: tuple[str, ...]
    metric_name: str
    name: str
    organization_id: str
    operator: RuleOperator
    rule_id: str
    severity: RuleSeverity
    threshold: float


@dataclass(frozen=True)
class AlertRecord:
    alert_id: str
    acknowledged_at: datetime | None
    acknowledged_by_user_id: str | None
    current_value: float
    engine: DatabaseEngine
    instance_id: str
    last_evaluated_at: datetime
    metric_name: str
    opened_at: datetime
    owner_assigned_at: datetime | None
    owner_user_id: str | None
    organization_id: str
    resolved_at: datetime | None
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    status: AlertStatus
    threshold: float


@dataclass(frozen=True)
class AlertHistoryEvent:
    alert_id: str
    detail: str
    event_type: AlertEventType
    organization_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class AlertDetail:
    history: tuple[AlertHistoryEvent, ...]
    record: AlertRecord


@dataclass(frozen=True)
class EvaluationSummary:
    notified_alerts: int
    opened_alerts: int
    resolved_alerts: int


@dataclass(frozen=True)
class NotificationRequest:
    alert_id: str
    engine: DatabaseEngine
    instance_id: str
    message: str
    rule_name: str
    severity: RuleSeverity
