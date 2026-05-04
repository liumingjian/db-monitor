from dataclasses import dataclass

from db_monitor_api.control_plane.repository import ControlPlaneRepository
from db_monitor_api.control_plane.service import AssetNotFoundError
from db_monitor_api.runtime_views.domain import (
    ProcesslistQuery,
    ProcesslistSnapshotView,
)
from db_monitor_api.runtime_views.repository import ProcesslistRepository


@dataclass(frozen=True)
class ProcesslistService:
    control_plane_repository: ControlPlaneRepository
    processlist_repository: ProcesslistRepository

    def get_latest_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: ProcesslistQuery,
    ) -> ProcesslistSnapshotView | None:
        instance = self.control_plane_repository.get_instance(
            instance_id,
            organization_id=organization_id,
        )
        if instance is None:
            raise AssetNotFoundError(f"Unknown instance: {instance_id}")
        return self.processlist_repository.fetch_latest_snapshot(
            instance_id=instance_id,
            organization_id=organization_id,
            query=query,
        )
