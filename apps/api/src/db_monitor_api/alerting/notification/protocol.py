from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Protocol, runtime_checkable


class NotifyStatus(str, Enum):
    DELIVERED = "delivered"
    FAILED = "failed"
    SKIPPED = "skipped"


_EMPTY_CONFIG: Mapping[str, object] = MappingProxyType({})


@dataclass(frozen=True)
class NotifyPayload:
    rule_id: str
    rule_name: str
    organization_id: str
    instance_id: str | None
    engine: str
    metric_name: str
    metric_value: float
    threshold: float
    severity: str
    occurred_at: datetime
    web_link: str | None = None
    binding_config: Mapping[str, object] = _EMPTY_CONFIG


@dataclass(frozen=True)
class NotifyResult:
    channel: str
    status: NotifyStatus
    attempt: int
    delivered_at: datetime | None
    error: str | None


@runtime_checkable
class Notifier(Protocol):
    channel_name: str

    async def send(self, payload: NotifyPayload) -> NotifyResult: ...
