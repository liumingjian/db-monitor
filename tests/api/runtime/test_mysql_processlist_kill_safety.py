"""Safety net for `POST /instances/.../processlist/.../kill` (ADR-0006).

Minimum slice-1 safety net:
- Refuse to kill the monitor user's own connection.
- Refuse when instance validation status is not PASSED.
- Both paths must return 409 and never invoke the driver KILL.
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
    ProcesslistKillBlocked,
    ProcesslistKiller,
)
from tests.support import StaticMySQLConnectionValidator


INSTANCE_ID = "inst-safety"
ORGANIZATION_ID = "org-internal"
ANCHOR = datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc)


class RecordingKiller(ProcesslistKiller):
    def __init__(self) -> None:
        self.calls: list[int] = []

    def kill(
        self,
        *,
        connection: InstanceConnectionConfig,
        process_id: int,
        monitor_user: str,
    ) -> None:
        del connection, monitor_user
        self.calls.append(process_id)


class MonitorUserMatchingKiller(ProcesslistKiller):
    """Simulates the in-DB check: target thread is the monitor user."""

    def kill(
        self,
        *,
        connection: InstanceConnectionConfig,
        process_id: int,
        monitor_user: str,
    ) -> None:
        del connection, process_id, monitor_user
        raise ProcesslistKillBlocked(
            "Refusing to kill the monitoring user's own connection."
        )


def _instance(status: ValidationStatus) -> MonitoredInstance:
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
            detail="ok" if status is ValidationStatus.PASSED else "auth failed",
            server_version="8.4.0" if status is ValidationStatus.PASSED else None,
            status=status,
        ),
    )


def _build_app(*, instance: MonitoredInstance, killer: ProcesslistKiller) -> FastAPI:
    repo = InMemoryControlPlaneRepository()
    repo.create_instance(instance)
    return create_app(
        runtime=build_local_runtime(
            control_plane_repository=repo,
            mysql_validator=StaticMySQLConnectionValidator(),
            processlist_killer=killer,
        )
    )


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def test_kill_rejected_when_validation_status_is_not_passed() -> None:
    killer = RecordingKiller()
    app = _build_app(instance=_instance(ValidationStatus.FAILED), killer=killer)

    with TestClient(app) as client:
        _login_admin(client)
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/42/kill",
            json={"reason": "drill"},
        )

    assert response.status_code == 409
    assert "not PASSED" in response.json()["detail"]
    assert killer.calls == [], "Driver must not be invoked when safety net blocks."


def test_kill_rejected_when_target_is_monitor_user_connection() -> None:
    app = _build_app(
        instance=_instance(ValidationStatus.PASSED),
        killer=MonitorUserMatchingKiller(),
    )

    with TestClient(app) as client:
        _login_admin(client)
        response = client.post(
            f"/instances/{INSTANCE_ID}/processlist/7/kill",
            json={"reason": "drill"},
        )

    assert response.status_code == 409
    assert "monitoring user" in response.json()["detail"]


def test_safety_net_block_records_failure_audit_entry() -> None:
    killer = RecordingKiller()
    app = _build_app(instance=_instance(ValidationStatus.FAILED), killer=killer)

    with TestClient(app) as client:
        _login_admin(client)
        client.post(
            f"/instances/{INSTANCE_ID}/processlist/42/kill",
            json={"reason": "drill"},
        )
        runtime = app.state.runtime
        entries = runtime.audit_repository.entries
    assert entries[-1].action == "instances.process.kill"
    assert entries[-1].outcome == "failure"
    assert entries[-1].resource == f"instance:{INSTANCE_ID}:process:42"
