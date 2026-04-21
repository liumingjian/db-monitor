from collections.abc import Callable
from typing import cast

from fastapi import Depends, HTTPException, Request, status

from db_monitor_api.auth.domain import AuthContext, Permission
from db_monitor_api.auth.service import (
    SESSION_COOKIE_NAME,
    AuthenticationError,
    PermissionDenied,
)
from db_monitor_api.runtime import AppRuntime


def get_runtime(request: Request) -> AppRuntime:
    return cast(AppRuntime, request.app.state.runtime)


def require_auth_context(
    request: Request,
    runtime: AppRuntime = Depends(get_runtime),
) -> AuthContext:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session cookie.",
        )
    try:
        return runtime.auth_service.require_session(session_id=session_id)
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error


def require_permission_dependency(
    permission: Permission,
    resource: str,
) -> Callable[..., AuthContext]:
    def dependency(
        context: AuthContext = Depends(require_auth_context),
        runtime: AppRuntime = Depends(get_runtime),
    ) -> AuthContext:
        try:
            runtime.authorization_service.require_permission(
                context=context,
                permission=permission,
                resource=resource,
            )
        except PermissionDenied as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(error),
            ) from error
        return context

    return dependency
