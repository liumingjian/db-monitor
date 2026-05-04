from datetime import datetime, timedelta, timezone

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
from db_monitor_api.runtime_views.domain import (
    ProcesslistEntryRow,
    ProcesslistSnapshotView,
)
from db_monitor_api.runtime_views.repository import InMemoryProcesslistRepository
from tests.support import StaticMySQLConnectionValidator


INSTANCE_ID = "inst-processlist-api"
ORGANIZATION_ID = "org-internal"
ANCHOR = datetime(2026, 4, 22, 10, 0, 0, tzinfo=timezone.utc)


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


def _entries() -> tuple[ProcesslistEntryRow, ...]:
    trx_started = ANCHOR - timedelta(seconds=15)
    return (
        ProcesslistEntryRow(
            process_id=101,
            user="app",
            host="10.0.0.2:31000",
            db="ordering",
            command="Query",
            time_seconds=12,
            state="Sending data",
            info="SELECT * FROM orders",
            trx_started_at=trx_started,
        ),
        ProcesslistEntryRow(
            process_id=202,
            user="replica",
            host="10.0.0.3:31002",
            db="",
            command="Sleep",
            time_seconds=900,
            state="",
            info="",
            trx_started_at=None,
        ),
        ProcesslistEntryRow(
            process_id=303,
            user="app",
            host="10.0.0.2:31010",
            db="ordering",
            command="Query",
            time_seconds=1,
            state="Writing to net",
            info="SELECT 1",
            trx_started_at=None,
        ),
    )


def _build_app(
    *,
    snapshots: tuple[ProcesslistSnapshotView, ...] = (),
    instances: tuple[MonitoredInstance, ...] = (),
) -> FastAPI:
    control_plane_repository = InMemoryControlPlaneRepository()
    for instance in instances:
        control_plane_repository.create_instance(instance)
    processlist_repository = InMemoryProcesslistRepository()
    for snapshot in snapshots:
        processlist_repository.add_snapshot(
            instance_id=INSTANCE_ID,
            organization_id=ORGANIZATION_ID,
            snapshot=snapshot,
        )
    return create_app(
        runtime=build_local_runtime(
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
            processlist_repository=processlist_repository,
        )
    )


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def test_returns_latest_snapshot_with_all_entries_by_default() -> None:
    snapshot_at = ANCHOR
    app = _build_app(
        instances=(_instance(),),
        snapshots=(
            ProcesslistSnapshotView(collected_at=snapshot_at, entries=_entries()),
            ProcesslistSnapshotView(
                collected_at=snapshot_at - timedelta(minutes=1),
                entries=_entries()[:1],
            ),
        ),
    )

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(f"/instances/{INSTANCE_ID}/processlist")

    assert response.status_code == 200
    body = response.json()
    assert body["snapshot_at"] == snapshot_at.isoformat()
    assert [entry["process_id"] for entry in body["entries"]] == [101, 202, 303]
    sleep_entry = body["entries"][1]
    assert sleep_entry["command"] == "Sleep", "ADR-0005: Sleep rows are part of full-coverage"


def test_filters_by_user_host_command_and_min_time() -> None:
    app = _build_app(
        instances=(_instance(),),
        snapshots=(
            ProcesslistSnapshotView(collected_at=ANCHOR, entries=_entries()),
        ),
    )

    with TestClient(app) as client:
        _login_admin(client)
        user_filtered = client.get(
            f"/instances/{INSTANCE_ID}/processlist",
            params={"user": "app", "min_time_seconds": 10},
        )

    assert user_filtered.status_code == 200
    body = user_filtered.json()
    assert len(body["entries"]) == 1
    assert body["entries"][0]["process_id"] == 101


def test_returns_empty_payload_when_no_snapshot_present() -> None:
    app = _build_app(instances=(_instance(),))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(f"/instances/{INSTANCE_ID}/processlist")

    assert response.status_code == 200
    assert response.json() == {"snapshot_at": None, "entries": []}


def test_returns_404_for_unknown_instance() -> None:
    app = _build_app()

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get("/instances/inst-missing/processlist")

    assert response.status_code == 404


def test_requires_authentication() -> None:
    app = _build_app(instances=(_instance(),))

    with TestClient(app) as client:
        response = client.get(f"/instances/{INSTANCE_ID}/processlist")

    assert response.status_code == 401


def test_limit_cannot_exceed_500() -> None:
    app = _build_app(instances=(_instance(),))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/processlist",
            params={"limit": 600},
        )

    assert response.status_code == 422


def test_limit_applies_after_filter() -> None:
    long_entries = tuple(
        ProcesslistEntryRow(
            process_id=1000 + idx,
            user="app",
            host="10.0.0.2:31000",
            db="ordering",
            command="Query",
            time_seconds=20,
            state="Sending data",
            info="",
            trx_started_at=None,
        )
        for idx in range(5)
    )
    app = _build_app(
        instances=(_instance(),),
        snapshots=(
            ProcesslistSnapshotView(collected_at=ANCHOR, entries=long_entries),
        ),
    )

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/processlist",
            params={"limit": 2},
        )

    assert response.status_code == 200
    assert len(response.json()["entries"]) == 2


def test_time_window_filters_snapshot_selection() -> None:
    older = ProcesslistSnapshotView(
        collected_at=ANCHOR - timedelta(minutes=30),
        entries=_entries()[:1],
    )
    newer = ProcesslistSnapshotView(collected_at=ANCHOR, entries=_entries())
    app = _build_app(instances=(_instance(),), snapshots=(older, newer))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/processlist",
            params={
                "collected_before": (ANCHOR - timedelta(minutes=10)).isoformat(),
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["snapshot_at"] == older.collected_at.isoformat()
    assert len(body["entries"]) == 1
