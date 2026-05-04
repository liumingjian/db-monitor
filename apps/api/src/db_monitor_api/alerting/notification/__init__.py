"""Notifier abstraction (Epic 16).

Channel-agnostic notification dispatch used by the alerting rule engine.
Concrete channels (feishu, smtp) live under ``channels/``.
"""

from db_monitor_api.alerting.notification.bindings import InMemoryBindingRepository
from db_monitor_api.alerting.notification.coordinator import (
    CoordinatorState,
    DispatchCoordinator,
    NullRuleHitSink,
    RuleHitSink,
)
from db_monitor_api.alerting.notification.fallback import dispatch_with_fallback
from db_monitor_api.alerting.notification.protocol import (
    Notifier,
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)
from db_monitor_api.alerting.notification.registry import (
    ChannelAlreadyRegisteredError,
    ChannelRegistry,
    UnknownChannelError,
)
from db_monitor_api.alerting.notification.query_service import NotifyHistoryService
from db_monitor_api.alerting.notification.repository import (
    InMemoryNotifyHistoryRepository,
    NotifyHistoryEntry,
    NotifyHistoryRepository,
)
from db_monitor_api.alerting.notification.service import (
    BindingRepository,
    ChannelBinding,
    NotifyHistoryWriter,
    RuleHitEvent,
    dispatch,
)

__all__ = [
    "BindingRepository",
    "ChannelAlreadyRegisteredError",
    "ChannelBinding",
    "ChannelRegistry",
    "CoordinatorState",
    "DispatchCoordinator",
    "InMemoryBindingRepository",
    "InMemoryNotifyHistoryRepository",
    "Notifier",
    "NotifyHistoryEntry",
    "NotifyHistoryRepository",
    "NotifyHistoryService",
    "NotifyHistoryWriter",
    "NotifyPayload",
    "NotifyResult",
    "NotifyStatus",
    "NullRuleHitSink",
    "RuleHitEvent",
    "RuleHitSink",
    "UnknownChannelError",
    "dispatch",
    "dispatch_with_fallback",
]
