"""Oracle tablespace service layer (Epic 15 Slice 1 child #4).

Coordinates the control-plane repository (for instance existence /
access control) with the tablespace read repository. Enforces the 30-day
history-window upper bound (SPEC.md / ADR-0008 retention).
"""

from dataclasses import dataclass
from datetime import timedelta

from db_monitor_api.control_plane.repository import ControlPlaneRepository
from db_monitor_api.control_plane.service import AssetNotFoundError
from db_monitor_api.runtime_views.tablespace_domain import (
    MAX_TABLESPACE_HISTORY_DAYS,
    TablespaceHistoryQuery,
    TablespaceHistoryView,
    TablespaceSnapshotQuery,
    TablespaceSnapshotView,
)
from db_monitor_api.runtime_views.tablespace_repository import TablespaceRepository


class TablespaceWindowTooWideError(ValueError):
    """Raised when the history `[from, to]` window exceeds 30 days."""


@dataclass(frozen=True)
class TablespaceService:
    control_plane_repository: ControlPlaneRepository
    tablespace_repository: TablespaceRepository

    def get_latest_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceSnapshotQuery,
    ) -> TablespaceSnapshotView | None:
        self._ensure_instance(instance_id=instance_id, organization_id=organization_id)
        return self.tablespace_repository.fetch_latest_snapshot(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
        )

    def get_history(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceHistoryQuery,
    ) -> TablespaceHistoryView:
        self._ensure_instance(instance_id=instance_id, organization_id=organization_id)
        span = query.to_timestamp - query.from_timestamp
        if span > timedelta(days=MAX_TABLESPACE_HISTORY_DAYS):
            raise TablespaceWindowTooWideError(
                f"history window {span} exceeds max {MAX_TABLESPACE_HISTORY_DAYS} days"
            )
        if span.total_seconds() < 0:
            raise TablespaceWindowTooWideError(
                "history window 'from' must be <= 'to'"
            )
        return self.tablespace_repository.fetch_history(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
        )

    def _ensure_instance(self, *, instance_id: str, organization_id: str) -> None:
        instance = self.control_plane_repository.get_instance(
            instance_id,
            organization_id=organization_id,
        )
        if instance is None:
            raise AssetNotFoundError(f"Unknown instance: {instance_id}")
