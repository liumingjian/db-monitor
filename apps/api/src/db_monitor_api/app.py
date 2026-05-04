from db_monitor_api.analytics.router import build_analytics_router
from db_monitor_api.alerting.notification.router import build_notification_router
from db_monitor_api.alerting.router import build_alerting_router
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from db_monitor_api import APP_NAME
from db_monitor_api.auth.router import build_auth_router
from db_monitor_api.control_plane.router import build_control_plane_router
from db_monitor_api.health import ReadinessSnapshot
from db_monitor_api.runtime import AppRuntime
from db_monitor_api.runtime_views.router import build_runtime_router


def create_app(*, runtime: AppRuntime) -> FastAPI:
    app = FastAPI(title=APP_NAME)
    app.state.runtime = runtime

    @app.get("/health/live", tags=["health"])
    def live() -> dict[str, str]:
        return {"mode": runtime.runtime_mode, "status": "live"}

    @app.get("/health/ready", tags=["health"])
    def ready() -> JSONResponse:
        snapshot = runtime.readiness_probe.snapshot()
        return JSONResponse(
            content=_ready_payload(runtime=runtime, snapshot=snapshot),
            status_code=200 if snapshot.ready else 503,
        )

    app.include_router(build_auth_router())
    app.include_router(build_analytics_router())
    app.include_router(build_alerting_router())
    app.include_router(build_notification_router())
    app.include_router(build_control_plane_router())
    app.include_router(build_runtime_router())
    return app


def _ready_payload(
    *,
    runtime: AppRuntime,
    snapshot: ReadinessSnapshot,
) -> dict[str, object]:
    return {
        "dependencies": [
            {
                "detail": dependency.detail,
                "name": dependency.name,
                "ready": dependency.ready,
            }
            for dependency in snapshot.dependencies
        ],
        "mode": runtime.runtime_mode,
        "status": "ready" if snapshot.ready else "not_ready",
    }
