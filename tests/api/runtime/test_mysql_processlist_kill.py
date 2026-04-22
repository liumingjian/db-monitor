"""ADR-0006 / ADR-0011 D2: MySQL processlist kill endpoint.

Covers the happy path, permission gating (viewer denied, operator
allowed), unknown instance (404), pymysql failure translated to 502,
and missing-authentication (401).
"""

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    InstanceConnectionConfig,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_api.runtime_views.kill import (
    ProcesslistKillFailed,
    ProcesslistKiller,
)
from tests.support import StaticMySQLConnectionValidator


INSTANCE_ID = "inst-kill"
ORGANIZATION_ID = "org-internal"
ANCHOR = datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc)


class RecordingKiller(ProcesslistKiller):
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, str]] = []

    def kill(
        self,
        *,
        connection: InstanceConnectionConfig,
        process_id: int,
        monitor_user: str,
    ) -> None:
        self.calls.append((connection.host, process_id, monitor_user))


class FailingKiller(ProcesslistKiller):
    def kill(
        self,
        *,
        connection: InstanceConnectionConfig,
        process_id: int,
        monitor_user: str,
    ) -> None:
        del connection, process_id, monitor_user
        raise ProcesslistKillFailed("pymysql: (2013, 'Lost connection')")


def _passed_instance() -> MonitoredInstance:
    return MonitoredInstance(
        connection=InstanceConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=ANCHOR,
        engine=DatabaseEngine.MYSQL,
        environment="prod",
        instance_id=INSTANCE_ID,
        labels=("primary",),
        name="prod-primary",
        organization_id=ORGANIZATION_ID,
        validation=ConnectionValidation(
            checked_at=ANCHOR,
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )


def _build_app(
    *,
    instances: tuple[MonitoredInstance, ...],
    killer: ProcesslistKiller,
) -> FastAPI:
    repo = InMemoryControlPlaneRepository()
    for instance in instances:
        repo.create_instance(instance)
    return create_app(
        runtime=build_local_runtime(
            control_plane_repository=repo,
            mysql_validator=StaticMySQLConnectionValidator(),
            processlist_killer=killer,
        )
    )


def _login(client: TestClient, username: str, password: str) -> None:
    response = client.post(
        "/auth/login",
        json={"password": password, "username": username},
    )
    assert response.status_code == 200


def test_admin_can_kill_process_and_response_shape_is_stable() -> None:
    killer = RecordingKiller()
    app = _build_app(instances=(_passed_instance(),), killer=killer)

    with TestClient(app) as client:
        _login(client, "admin", "admin-password")
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/42/kill",
            json={"reason": "blocking head-of-line write"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["killed"] is True
    assert body["notes"] is None
    assert isinstance(body["checked_at"], str)
    assert killer.calls == [("127.0.0.1", 42, "db_monitor")]


def test_operator_can_kill_process() -> None:
    killer = RecordingKiller()
    app = _build_app(instances=(_passed_instance(),), killer=killer)

    with TestClient(app) as client:
        _login(client, "operator", "operator-password")
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/99/kill",
            json={"reason": "ops drill"},
        )

    assert response.status_code == 200
    assert response.json()["killed"] is True


def test_viewer_is_denied_kill() -> None:
    killer = RecordingKiller()
    app = _build_app(instances=(_passed_instance(),), killer=killer)

    with TestClient(app) as client:
        _login(client, "viewer", "viewer-password")
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/42/kill",
            json={"reason": "curious"},
        )

    assert response.status_code == 403
    assert response.json() == {"detail": "Missing permission: instances:action"}
    assert killer.calls == []


def test_missing_authentication_returns_401() -> None:
    killer = RecordingKiller()
    app = _build_app(instances=(_passed_instance(),), killer=killer)

    with TestClient(app) as client:
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/42/kill",
            json={"reason": "noop"},
        )

    assert response.status_code == 401


def test_unknown_instance_returns_404() -> None:
    killer = RecordingKiller()
    app = _build_app(instances=(), killer=killer)

    with TestClient(app) as client:
        _login(client, "admin", "admin-password")
        response = client.post(
            "/instances/inst-missing/processlist/42/kill",
            json={"reason": "noop"},
        )

    assert response.status_code == 404


def test_kill_request_without_body_is_accepted() -> None:
    killer = RecordingKiller()
    app = _build_app(instances=(_passed_instance(),), killer=killer)

    with TestClient(app) as client:
        _login(client, "admin", "admin-password")
        response = client.post(f"/instances/{INSTANCE_ID}/processlist/42/kill")

    assert response.status_code == 200
    assert response.json()["killed"] is True


def test_kill_failure_from_driver_is_surfaced_as_502() -> None:
    app = _build_app(instances=(_passed_instance(),), killer=FailingKiller())

    with TestClient(app) as client:
        _login(client, "admin", "admin-password")
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/42/kill",
            json={"reason": "drill"},
        )

    assert response.status_code == 502
    assert "Lost connection" in response.json()["detail"]
