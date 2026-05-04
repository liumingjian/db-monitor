"""`GET /instances/{instance_id}/slow-queries` (ADR-0007)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from db_monitor_api.auth.domain import AuthContext, Permission
from db_monitor_api.control_plane.service import AssetNotFoundError
from db_monitor_api.dependencies import get_runtime, require_permission_dependency
from db_monitor_api.runtime import AppRuntime
from db_monitor_api.runtime_views.slow_query_domain import (
    DEFAULT_SLOW_QUERY_LIMIT,
    MAX_SLOW_QUERY_LIMIT,
    SlowQueryEntryRow,
    SlowQueryQuery,
    SlowQuerySnapshotView,
)

router = APIRouter()


class SlowQueryWindowResponse(BaseModel):
    from_at: str
    to_at: str


class SlowQueryEntryResponse(BaseModel):
    event_id: int
    started_at: str
    user: str
    schema_name: str
    sql_text: str
    digest: str
    timer_wait_ms: float
    rows_examined: int
    rows_sent: int
    rows_affected: int
    errors: int


class SlowQuerySnapshotResponse(BaseModel):
    window: SlowQueryWindowResponse
    entries: list[SlowQueryEntryResponse]


def build_slow_query_router() -> APIRouter:
    return router


@router.get(
    "/instances/{instance_id}/slow-queries",
    response_model=SlowQuerySnapshotResponse,
)
def get_instance_slow_queries(
    instance_id: str,
    min_duration_ms: float | None = Query(default=None, ge=0),
    user: str | None = Query(default=None),
    schema_name: str | None = Query(default=None, alias="schema"),
    digest_prefix: str | None = Query(default=None),
    started_after: datetime | None = Query(default=None),
    started_before: datetime | None = Query(default=None),
    limit: int = Query(
        default=DEFAULT_SLOW_QUERY_LIMIT,
        ge=1,
        le=MAX_SLOW_QUERY_LIMIT,
    ),
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_READ, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> SlowQuerySnapshotResponse:
    query = SlowQueryQuery(
        digest_prefix=digest_prefix,
        limit=limit,
        min_duration_ms=min_duration_ms,
        schema_name=schema_name,
        started_after=started_after,
        started_before=started_before,
        user=user,
    )
    try:
        snapshot = runtime.slow_query_service.get_snapshot(
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
    snapshot: SlowQuerySnapshotView,
) -> SlowQuerySnapshotResponse:
    return SlowQuerySnapshotResponse(
        window=SlowQueryWindowResponse(
            from_at=snapshot.window.from_at.isoformat(),
            to_at=snapshot.window.to_at.isoformat(),
        ),
        entries=[_entry_to_response(entry) for entry in snapshot.entries],
    )


def _entry_to_response(entry: SlowQueryEntryRow) -> SlowQueryEntryResponse:
    return SlowQueryEntryResponse(
        event_id=entry.event_id,
        started_at=entry.started_at.isoformat(),
        user=entry.user,
        schema_name=entry.schema_name,
        sql_text=entry.sql_text,
        digest=entry.digest,
        timer_wait_ms=entry.timer_wait_ms,
        rows_examined=entry.rows_examined,
        rows_sent=entry.rows_sent,
        rows_affected=entry.rows_affected,
        errors=entry.errors,
    )
