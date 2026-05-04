from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from db_monitor_api.alerting.notification.repository import NotifyHistoryEntry
from db_monitor_api.auth.domain import AuthContext, Permission
from db_monitor_api.dependencies import get_runtime, require_permission_dependency
from db_monitor_api.runtime import AppRuntime

_NOTIFY_HISTORY_DEFAULT_LIMIT = 50
_NOTIFY_HISTORY_MAX_LIMIT = 500

router = APIRouter()


class NotifyHistoryResponse(BaseModel):
    attempt: int
    attempted_at: str
    channel: str
    delivered_at: str | None
    error: str | None
    instance_id: str | None
    organization_id: str
    rule_id: str
    status: str


def build_notification_router() -> APIRouter:
    return router


@router.get(
    "/admin/notify-history",
    response_model=list[NotifyHistoryResponse],
    tags=["notifications"],
)
def list_notify_history(
    channel: str | None = Query(default=None),
    limit: int = Query(
        default=_NOTIFY_HISTORY_DEFAULT_LIMIT,
        ge=1,
        le=_NOTIFY_HISTORY_MAX_LIMIT,
    ),
    rule_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    context: AuthContext = Depends(
        require_permission_dependency(Permission.SETTINGS_READ, "notify-history")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[NotifyHistoryResponse]:
    entries = runtime.notify_history_service.list_entries(
        channel=channel,
        limit=limit,
        organization_id=context.active_organization.organization_id,
        rule_id=rule_id,
        status=status,
    )
    return [_build_response(entry) for entry in entries]


def _build_response(entry: NotifyHistoryEntry) -> NotifyHistoryResponse:
    return NotifyHistoryResponse(
        attempt=entry.attempt,
        attempted_at=entry.attempted_at.isoformat(),
        channel=entry.channel,
        delivered_at=entry.delivered_at.isoformat() if entry.delivered_at is not None else None,
        error=entry.error,
        instance_id=entry.instance_id,
        organization_id=entry.organization_id,
        rule_id=entry.rule_id,
        status=entry.status,
    )
