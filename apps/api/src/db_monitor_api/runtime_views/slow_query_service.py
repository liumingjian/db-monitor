"""Slow-query read service (ADR-0007)."""

from dataclasses import dataclass
from datetime import timedelta

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.repository import ControlPlaneRepository
from db_monitor_api.control_plane.service import AssetNotFoundError
from db_monitor_api.runtime_views.slow_query_domain import (
    DEFAULT_SLOW_QUERY_WINDOW_MINUTES,
    SlowQueryQuery,
    SlowQuerySnapshotView,
    SlowQueryWindow,
)
from db_monitor_api.runtime_views.slow_query_repository import SlowQueryRepository


@dataclass(frozen=True)
class SlowQueryService:
    control_plane_repository: ControlPlaneRepository
    slow_query_repository: SlowQueryRepository

    def get_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: SlowQueryQuery,
    ) -> SlowQuerySnapshotView:
        instance = self.control_plane_repository.get_instance(
            instance_id,
            organization_id=organization_id,
        )
        if instance is None:
            raise AssetNotFoundError(f"Unknown instance: {instance_id}")
        window = _resolve_window(query)
        return self.slow_query_repository.fetch_snapshot(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
            window=window,
        )


def _resolve_window(query: SlowQueryQuery) -> SlowQueryWindow:
    now = utc_now()
    to_at = query.started_before if query.started_before is not None else now
    if query.started_after is not None:
        from_at = query.started_after
    else:
        from_at = to_at - timedelta(minutes=DEFAULT_SLOW_QUERY_WINDOW_MINUTES)
    return SlowQueryWindow(from_at=from_at, to_at=to_at)
