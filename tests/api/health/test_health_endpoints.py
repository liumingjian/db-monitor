from fastapi.testclient import TestClient

from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.health import DependencyStatus


class FailingDependencyCheck:
    def check(self) -> DependencyStatus:
        return DependencyStatus(
            detail="dial tcp 127.0.0.1:8123: connect refused",
            name="clickhouse",
            ready=False,
        )


def test_live_endpoint_reports_runtime_mode() -> None:
    app = create_app(runtime=build_local_runtime())

    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"mode": "local", "status": "live"}


def test_ready_endpoint_returns_service_unavailable_on_failed_dependency() -> None:
    app = create_app(
        runtime=build_local_runtime(
            dependency_checks=(FailingDependencyCheck(),),
        )
    )

    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "dependencies": [
            {
                "detail": "dial tcp 127.0.0.1:8123: connect refused",
                "name": "clickhouse",
                "ready": False,
            }
        ],
        "mode": "local",
        "status": "not_ready",
    }
