from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Protocol

from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
)


@dataclass(frozen=True)
class NotifyHistoryEntry:
    attempt: int
    attempted_at: datetime
    channel: str
    delivered_at: datetime | None
    error: str | None
    instance_id: str | None
    organization_id: str
    rule_id: str
    status: str


class NotifyHistoryRepository(Protocol):
    def record(self, *, payload: NotifyPayload, result: NotifyResult) -> None: ...

    def list_entries(
        self,
        *,
        organization_id: str,
        channel: str | None = None,
        limit: int = 50,
        rule_id: str | None = None,
        status: str | None = None,
    ) -> Sequence[NotifyHistoryEntry]: ...


def _entry_from(payload: NotifyPayload, result: NotifyResult) -> NotifyHistoryEntry:
    return NotifyHistoryEntry(
        attempt=result.attempt,
        attempted_at=result.delivered_at or payload.occurred_at,
        channel=result.channel,
        delivered_at=result.delivered_at if result.status.value == "delivered" else None,
        error=result.error,
        instance_id=payload.instance_id,
        organization_id=payload.organization_id,
        rule_id=payload.rule_id,
        status=result.status.value,
    )


class InMemoryNotifyHistoryRepository:
    def __init__(self) -> None:
        self._entries: list[NotifyHistoryEntry] = []
        self._lock = RLock()

    def record(self, *, payload: NotifyPayload, result: NotifyResult) -> None:
        entry = _entry_from(payload, result)
        with self._lock:
            self._entries.append(entry)

    def list_entries(
        self,
        *,
        organization_id: str,
        channel: str | None = None,
        limit: int = 50,
        rule_id: str | None = None,
        status: str | None = None,
    ) -> Sequence[NotifyHistoryEntry]:
        with self._lock:
            snapshot = tuple(self._entries)
        filtered = tuple(
            entry
            for entry in reversed(snapshot)
            if entry.organization_id == organization_id
            and (channel is None or entry.channel == channel)
            and (rule_id is None or entry.rule_id == rule_id)
            and (status is None or entry.status == status)
        )
        bounded_limit = max(1, min(limit, 500))
        return filtered[:bounded_limit]
