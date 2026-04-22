from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from db_monitor_api.auth.domain import AuthContext, Permission
from db_monitor_api.control_plane.service import AssetNotFoundError
from db_monitor_api.dependencies import get_runtime, require_permission_dependency
from db_monitor_api.runtime import AppRuntime
from db_monitor_api.runtime_views.domain import (
    DEFAULT_PROCESSLIST_LIMIT,
    MAX_PROCESSLIST_LIMIT,
    ProcesslistEntryRow,
    ProcesslistQuery,
    ProcesslistSnapshotView,
)
from db_monitor_api.runtime_views.kill import (
    ProcesslistKillBlocked,
    ProcesslistKillFailed,
)

router = APIRouter()


class ProcesslistEntryResponse(BaseModel):
    process_id: int
    user: str
    host: str
    db: str
    command: str
    time_seconds: int
    state: str
    info: str
    trx_started_at: str | None


class ProcesslistSnapshotResponse(BaseModel):
    snapshot_at: str | None
    entries: list[ProcesslistEntryResponse]


class KillProcesslistRequest(BaseModel):
    reason: str | None = None


class KillProcesslistResponse(BaseModel):
    checked_at: str
    killed: bool
    notes: str | None


def build_runtime_router() -> APIRouter:
    return router


@router.get(
    "/instances/{instance_id}/processlist",
    response_model=ProcesslistSnapshotResponse,
)
def get_instance_processlist(
    instance_id: str,
    user: str | None = Query(default=None),
    host: str | None = Query(default=None),
    command: str | None = Query(default=None),
    min_time_seconds: int | None = Query(default=None, ge=0),
    collected_after: datetime | None = Query(default=None),
    collected_before: datetime | None = Query(default=None),
    limit: int = Query(
        default=DEFAULT_PROCESSLIST_LIMIT,
        ge=1,
        le=MAX_PROCESSLIST_LIMIT,
    ),
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_READ, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> ProcesslistSnapshotResponse:
    query = ProcesslistQuery(
        collected_after=collected_after,
        collected_before=collected_before,
        command=command,
        host=host,
        limit=limit,
        min_time_seconds=min_time_seconds,
        user=user,
    )
    try:
        snapshot = runtime.processlist_service.get_latest_snapshot(
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


def _snapshot_to_response(
    snapshot: ProcesslistSnapshotView | None,
) -> ProcesslistSnapshotResponse:
    if snapshot is None:
        return ProcesslistSnapshotResponse(snapshot_at=None, entries=[])
    return ProcesslistSnapshotResponse(
        snapshot_at=snapshot.collected_at.isoformat(),
        entries=[_entry_to_response(entry) for entry in snapshot.entries],
    )


@router.post(
    "/instances/{instance_id}/processlist/{process_id}/kill",
    response_model=KillProcesslistResponse,
)
def kill_instance_process(
    instance_id: str,
    process_id: int,
    payload: KillProcesslistRequest | None = None,
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_ACTION, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> KillProcesslistResponse:
    reason = payload.reason if payload is not None else None
    try:
        result = runtime.processlist_kill_service.kill_process(
            actor_user_id=context.user.user_id,
            instance_id=instance_id,
            organization_id=context.active_organization.organization_id,
            process_id=process_id,
            reason=reason,
        )
    except AssetNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ProcesslistKillBlocked as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except ProcesslistKillFailed as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error
    return KillProcesslistResponse(
        checked_at=result.checked_at.isoformat(),
        killed=result.killed,
        notes=result.notes,
    )


def _entry_to_response(entry: ProcesslistEntryRow) -> ProcesslistEntryResponse:
    return ProcesslistEntryResponse(
        process_id=entry.process_id,
        user=entry.user,
        host=entry.host,
        db=entry.db,
        command=entry.command,
        time_seconds=entry.time_seconds,
        state=entry.state,
        info=entry.info,
        trx_started_at=(
            None if entry.trx_started_at is None else entry.trx_started_at.isoformat()
        ),
    )
