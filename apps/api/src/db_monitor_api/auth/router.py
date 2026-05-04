from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from db_monitor_api.auth.domain import AuthContext, ManagedUser, Permission, RoleCatalogEntry
from db_monitor_api.auth.service import (
    AuthenticationError,
    ManagedUserNotFoundError,
    SESSION_COOKIE_NAME,
    UnknownRoleError,
)
from db_monitor_api.dependencies import (
    get_runtime,
    require_auth_context,
    require_permission_dependency,
)
from db_monitor_api.runtime import AppRuntime

router = APIRouter()


class LoginRequest(BaseModel):
    password: str
    username: str


class OrganizationResponse(BaseModel):
    organization_id: str
    name: str
    slug: str


class OrganizationMembershipResponse(BaseModel):
    organization: OrganizationResponse
    roles: list[str]


class SessionUserResponse(BaseModel):
    active_organization: OrganizationResponse
    display_name: str
    organization_memberships: list[OrganizationMembershipResponse]
    permissions: list[str]
    roles: list[str]
    user_id: str
    username: str


class AuditEntryResponse(BaseModel):
    action: str
    actor_user_id: str
    occurred_at: datetime
    organization_id: str
    outcome: str
    resource: str


class ManagedUserResponse(BaseModel):
    active_organization_id: str
    display_name: str
    effective_permissions: list[str]
    roles: list[str]
    user_id: str
    username: str


class RoleCatalogEntryResponse(BaseModel):
    permissions: list[str]
    role: str


class UpdateUserRolesRequest(BaseModel):
    roles: list[str] = Field(default_factory=list)


def build_auth_router() -> APIRouter:
    return router


@router.post("/auth/login", response_model=SessionUserResponse)
def login(
    payload: LoginRequest,
    response: Response,
    runtime: AppRuntime = Depends(get_runtime),
) -> SessionUserResponse:
    try:
        context = runtime.auth_service.login(
            password=payload.password,
            username=payload.username,
        )
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=context.session.session_id,
        httponly=True,
        samesite="lax",
    )
    return _build_session_response(context)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    context: AuthContext = Depends(require_auth_context),
    runtime: AppRuntime = Depends(get_runtime),
) -> None:
    runtime.auth_service.logout(session_id=context.session.session_id)
    response.delete_cookie(key=SESSION_COOKIE_NAME)


@router.get("/auth/me", response_model=SessionUserResponse)
def me(context: AuthContext = Depends(require_auth_context)) -> SessionUserResponse:
    return _build_session_response(context)


@router.get("/auth/audit-entries", response_model=list[AuditEntryResponse])
def list_audit_entries(
    limit: int = Query(default=50, ge=1, le=200),
    context: AuthContext = Depends(
        require_permission_dependency(Permission.SETTINGS_WRITE, "audit")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[AuditEntryResponse]:
    return [
        AuditEntryResponse(
            action=entry.action,
            actor_user_id=entry.actor_user_id,
            occurred_at=entry.occurred_at,
            organization_id=entry.organization_id,
            outcome=entry.outcome,
            resource=entry.resource,
        )
        for entry in runtime.audit_service.list_entries(
            limit=limit,
            organization_id=context.active_organization.organization_id,
        )
    ]


@router.get("/auth/users", response_model=list[ManagedUserResponse])
def list_users(
    context: AuthContext = Depends(
        require_permission_dependency(Permission.SETTINGS_WRITE, "users")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[ManagedUserResponse]:
    return [
        _build_managed_user_response(user)
        for user in runtime.auth_service.list_managed_users(
            organization_id=context.active_organization.organization_id
        )
    ]


@router.get("/auth/roles", response_model=list[RoleCatalogEntryResponse])
def list_roles(
    _: AuthContext = Depends(
        require_permission_dependency(Permission.SETTINGS_WRITE, "users")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[RoleCatalogEntryResponse]:
    return [
        _build_role_catalog_entry_response(entry)
        for entry in runtime.auth_service.list_role_catalog()
    ]


@router.put("/auth/users/{user_id}/roles", response_model=ManagedUserResponse)
def update_user_roles(
    user_id: str,
    payload: UpdateUserRolesRequest,
    context: AuthContext = Depends(
        require_permission_dependency(Permission.SETTINGS_WRITE, "users")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> ManagedUserResponse:
    try:
        user = runtime.auth_service.update_user_roles(
            actor_user_id=context.user.user_id,
            organization_id=context.active_organization.organization_id,
            roles=frozenset(payload.roles),
            target_user_id=user_id,
        )
    except ManagedUserNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except UnknownRoleError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return _build_managed_user_response(user)


def _build_session_response(context: AuthContext) -> SessionUserResponse:
    return SessionUserResponse(
        active_organization=OrganizationResponse(
            organization_id=context.active_organization.organization_id,
            name=context.active_organization.name,
            slug=context.active_organization.slug,
        ),
        display_name=context.user.display_name,
        organization_memberships=[
            OrganizationMembershipResponse(
                organization=OrganizationResponse(
                    organization_id=membership.organization.organization_id,
                    name=membership.organization.name,
                    slug=membership.organization.slug,
                ),
                roles=sorted(membership.roles),
            )
            for membership in sorted(
                context.user.organization_memberships,
                key=lambda membership: membership.organization.slug,
            )
        ],
        permissions=sorted(permission.value for permission in context.permissions),
        roles=sorted(context.user.roles),
        user_id=context.user.user_id,
        username=context.user.username,
    )


def _build_managed_user_response(user: ManagedUser) -> ManagedUserResponse:
    return ManagedUserResponse(
        active_organization_id=user.active_organization_id,
        display_name=user.display_name,
        effective_permissions=sorted(
            permission.value for permission in user.effective_permissions
        ),
        roles=sorted(user.roles),
        user_id=user.user_id,
        username=user.username,
    )


def _build_role_catalog_entry_response(
    entry: RoleCatalogEntry,
) -> RoleCatalogEntryResponse:
    return RoleCatalogEntryResponse(
        permissions=sorted(permission.value for permission in entry.permissions),
        role=entry.role,
    )
