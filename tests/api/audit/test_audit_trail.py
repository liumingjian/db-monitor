"""Audit trail assertions for ADR-0011 D2 action names.

Covers the `instances.process.kill` action emitted by the runtime
action endpoint with both success and failure outcomes, plus the
permission-denied path where the authorization service emits
`instances.denied` for the `instances` resource.
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


INSTANCE_ID = "inst-audit"
ORGANIZATION_ID = "org-internal"
ANCHOR = datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc)


class RecordingKiller(ProcesslistKiller):
    def kill(
        self,
        *,
        connection: InstanceConnectionConfig,
        process_id: int,
        monitor_user: str,
    ) -> None:
        del connection, process_id, monitor_user


class FailingKiller(ProcesslistKiller):
    def kill(
        self,
        *,
        connection: InstanceConnectionConfig,
        process_id: int,
        monitor_user: str,
    ) -> None:
        del connection, process_id, monitor_user
        raise ProcesslistKillFailed("pymysql: Connection refused")


def _instance() -> MonitoredInstance:
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


def _build_app(*, killer: ProcesslistKiller) -> FastAPI:
    repo = InMemoryControlPlaneRepository()
    repo.create_instance(_instance())
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


def test_successful_kill_records_instances_process_kill_success_audit() -> None:
    app = _build_app(killer=RecordingKiller())

    with TestClient(app) as client:
        _login(client, "admin", "admin-password")
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/123/kill",
            json={"reason": "runaway query"},
        )
        assert response.status_code == 200
        entries = app.state.runtime.audit_repository.entries

    kill_entry = entries[-1]
    assert kill_entry.action == "instances.process.kill"
    assert kill_entry.outcome == "success"
    assert kill_entry.actor_user_id == "user-admin"
    assert kill_entry.organization_id == ORGANIZATION_ID
    assert kill_entry.resource == f"instance:{INSTANCE_ID}:process:123"


def test_failed_kill_records_instances_process_kill_failure_audit() -> None:
    app = _build_app(killer=FailingKiller())

    with TestClient(app) as client:
        _login(client, "admin", "admin-password")
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/77/kill",
            json={"reason": "drill"},
        )
        assert response.status_code == 502
        entries = app.state.runtime.audit_repository.entries

    kill_entry = entries[-1]
    assert kill_entry.action == "instances.process.kill"
    assert kill_entry.outcome == "failure"
    assert kill_entry.resource == f"instance:{INSTANCE_ID}:process:77"


def test_viewer_kill_attempt_is_audited_as_permission_denied() -> None:
    app = _build_app(killer=RecordingKiller())

    with TestClient(app) as client:
        _login(client, "viewer", "viewer-password")
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/1/kill",
            json={"reason": "noop"},
        )
        assert response.status_code == 403
        entries = app.state.runtime.audit_repository.entries

    # AuthorizationService emits `<resource>.denied`; no kill action recorded.
    actions = [entry.action for entry in entries]
    assert "instances.process.kill" not in actions
    assert entries[-1].action == "instances.denied"
    assert entries[-1].outcome == "denied"
