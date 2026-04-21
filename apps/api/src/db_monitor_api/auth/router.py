from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from db_monitor_api.auth.domain import AuthContext
from db_monitor_api.auth.service import AuthenticationError, SESSION_COOKIE_NAME
from db_monitor_api.dependencies import get_runtime, require_auth_context
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
