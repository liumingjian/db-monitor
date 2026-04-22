"""Oracle tablespace HTTP surface (Epic 15 Slice 1 child #4).

Two endpoints, both gated by `INSTANCES_READ`:

- `GET /instances/{instance_id}/tablespaces` — latest snapshot or a
  time-windowed historical snapshot via `collected_after?` / `collected_before?`.
- `GET /instances/{instance_id}/tablespaces/{tablespace_name}/history` —
  per-tablespace trend series over a bounded `[from, to]` window
  (max 30 days).

The module registers routes on the shared `runtime_views.router.router`
APIRouter so a single `include_router(build_runtime_router())` call in
`app.create_app` exposes them at the correct `/instances/{id}/...`
prefix (ADR-0005 layout).
"""

from datetime import datetime

from fastapi import Depends, HTTPException, Query, status
from pydantic import BaseModel

from db_monitor_api.auth.domain import AuthContext, Permission
from db_monitor_api.control_plane.service import AssetNotFoundError
from db_monitor_api.dependencies import get_runtime, require_permission_dependency
from db_monitor_api.runtime import AppRuntime
from db_monitor_api.runtime_views.router import router
from db_monitor_api.runtime_views.tablespace_domain import (
    TablespaceEntryRow,
    TablespaceHistoryPoint,
    TablespaceHistoryQuery,
    TablespaceHistoryView,
    TablespaceSnapshotQuery,
    TablespaceSnapshotView,
)
from db_monitor_api.runtime_views.tablespace_service import (
    TablespaceWindowTooWideError,
)


class TablespaceEntryResponse(BaseModel):
    tablespace_name: str
    status: str
    used_bytes: int
    total_bytes: int
    used_rate_percent: float
    autoextensible: bool


class TablespaceSnapshotResponse(BaseModel):
    snapshot_at: str | None
    entries: list[TablespaceEntryResponse]


class TablespaceHistoryEntryResponse(BaseModel):
    collected_at: str
    used_bytes: int
    total_bytes: int
    used_rate_percent: float


class TablespaceHistoryResponse(BaseModel):
    entries: list[TablespaceHistoryEntryResponse]


@router.get(
    "/instances/{instance_id}/tablespaces",
    response_model=TablespaceSnapshotResponse,
)
def get_instance_tablespaces(
    instance_id: str,
    collected_after: datetime | None = Query(default=None),
    collected_before: datetime | None = Query(default=None),
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_READ, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> TablespaceSnapshotResponse:
    query = TablespaceSnapshotQuery(
        collected_after=collected_after,
        collected_before=collected_before,
    )
    try:
        snapshot = runtime.tablespace_service.get_latest_snapshot(
            instance_id=instance_id,
            organization_id=context.active_organization.organization_id,
            query=query,
        )
    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    return _snapshot_to_response(snapshot)


@router.get(
    "/instances/{instance_id}/tablespaces/{tablespace_name}/history",
    response_model=TablespaceHistoryResponse,
)
def get_instance_tablespace_history(
    instance_id: str,
    tablespace_name: str,
    from_: datetime = Query(alias="from"),
    to: datetime = Query(),
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_READ, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> TablespaceHistoryResponse:
    query = TablespaceHistoryQuery(
        tablespace_name=tablespace_name,
        from_timestamp=from_,
        to_timestamp=to,
    )
    try:
        history = runtime.tablespace_service.get_history(
            instance_id=instance_id,
            organization_id=context.active_organization.organization_id,
            query=query,
        )
    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except TablespaceWindowTooWideError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    return _history_to_response(history)


def _snapshot_to_response(
    snapshot: TablespaceSnapshotView | None,
) -> TablespaceSnapshotResponse:
    if snapshot is None:
        return TablespaceSnapshotResponse(snapshot_at=None, entries=[])
    return TablespaceSnapshotResponse(
        snapshot_at=snapshot.collected_at.isoformat(),
        entries=[_entry_to_response(entry) for entry in snapshot.entries],
    )


def _entry_to_response(entry: TablespaceEntryRow) -> TablespaceEntryResponse:
    return TablespaceEntryResponse(
        tablespace_name=entry.tablespace_name,
        status=entry.status,
        used_bytes=entry.used_bytes,
        total_bytes=entry.total_bytes,
        used_rate_percent=entry.used_rate_percent,
        autoextensible=entry.autoextensible,
    )


def _history_to_response(history: TablespaceHistoryView) -> TablespaceHistoryResponse:
    return TablespaceHistoryResponse(
        entries=[_point_to_response(point) for point in history.entries],
    )


def _point_to_response(point: TablespaceHistoryPoint) -> TablespaceHistoryEntryResponse:
    return TablespaceHistoryEntryResponse(
        collected_at=point.collected_at.isoformat(),
        used_bytes=point.used_bytes,
        total_bytes=point.total_bytes,
        used_rate_percent=point.used_rate_percent,
    )
