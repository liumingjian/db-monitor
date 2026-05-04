from collections.abc import Sequence
from dataclasses import dataclass

from db_monitor_api.alerting.notification.repository import (
    NotifyHistoryEntry,
    NotifyHistoryRepository,
)


@dataclass(frozen=True)
class NotifyHistoryService:
    repository: NotifyHistoryRepository

    def list_entries(
        self,
        *,
        organization_id: str,
        channel: str | None = None,
        limit: int = 50,
        rule_id: str | None = None,
        status: str | None = None,
    ) -> Sequence[NotifyHistoryEntry]:
        return self.repository.list_entries(
            organization_id=organization_id,
            channel=channel,
            limit=limit,
            rule_id=rule_id,
            status=status,
        )
