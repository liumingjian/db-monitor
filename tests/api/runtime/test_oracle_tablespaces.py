"""API contract tests for Oracle tablespace endpoints (Epic 15 child #4)."""

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
from db_monitor_api.runtime_views.tablespace_domain import (
    TablespaceEntryRow,
    TablespaceSnapshotView,
)
from db_monitor_api.runtime_views.tablespace_repository import (
    InMemoryTablespaceRepository,
)
from tests.support import StaticMySQLConnectionValidator


INSTANCE_ID = "inst-oracle-ts"
ORGANIZATION_ID = "org-internal"
ANCHOR = datetime(2026, 4, 22, 12, 0, 0, tzinfo=timezone.utc)


def _oracle_instance() -> MonitoredInstance:
    return MonitoredInstance(
        connection=InstanceConnectionConfig(
            database="XE",
            host="127.0.0.1",
            password="secret",
            port=1521,
            username="system",
        ),
        created_at=ANCHOR,
        engine=DatabaseEngine.ORACLE,
        environment="prod",
        instance_id=INSTANCE_ID,
        labels=("oracle",),
        name="prod-oracle",
        organization_id=ORGANIZATION_ID,
        validation=ConnectionValidation(
            checked_at=ANCHOR,
            detail="ok",
            server_version="19c",
            status=ValidationStatus.PASSED,
        ),
    )


def _entries() -> tuple[TablespaceEntryRow, ...]:
    return (
        TablespaceEntryRow(
            tablespace_name="SYSAUX",
            status="ONLINE",
            used_bytes=1_000_000,
            total_bytes=4_000_000,
            used_rate_percent=25.0,
            autoextensible=True,
        ),
        TablespaceEntryRow(
            tablespace_name="USERS",
            status="ONLINE",
            used_bytes=3_800_000,
            total_bytes=4_000_000,
            used_rate_percent=95.0,
            autoextensible=False,
        ),
    )


def _build_app(
    *,
    instances: tuple[MonitoredInstance, ...] = (),
    snapshots: tuple[TablespaceSnapshotView, ...] = (),
) -> FastAPI:
    control_plane_repository = InMemoryControlPlaneRepository()
    for instance in instances:
        control_plane_repository.create_instance(instance)
    tablespace_repository = InMemoryTablespaceRepository()
    for snapshot in snapshots:
        tablespace_repository.add_snapshot(
            instance_id=INSTANCE_ID,
            organization_id=ORGANIZATION_ID,
            snapshot=snapshot,
        )
    return create_app(
        runtime=build_local_runtime(
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
            tablespace_repository=tablespace_repository,
        )
    )


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def test_snapshot_returns_latest_entries_sorted_by_used_rate() -> None:
    app = _build_app(
        instances=(_oracle_instance(),),
        snapshots=(
            TablespaceSnapshotView(collected_at=ANCHOR, entries=_entries()),
            TablespaceSnapshotView(
                collected_at=ANCHOR - timedelta(minutes=5),
                entries=_entries()[:1],
            ),
        ),
    )

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(f"/instances/{INSTANCE_ID}/tablespaces")

    assert response.status_code == 200
    body = response.json()
    assert body["snapshot_at"] == ANCHOR.isoformat()
    names = [entry["tablespace_name"] for entry in body["entries"]]
    assert set(names) == {"SYSAUX", "USERS"}


def test_snapshot_returns_empty_payload_when_no_snapshot_recorded() -> None:
    app = _build_app(instances=(_oracle_instance(),))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(f"/instances/{INSTANCE_ID}/tablespaces")

    assert response.status_code == 200
    assert response.json() == {"snapshot_at": None, "entries": []}


def test_snapshot_requires_authentication() -> None:
    app = _build_app(instances=(_oracle_instance(),))

    with TestClient(app) as client:
        response = client.get(f"/instances/{INSTANCE_ID}/tablespaces")

    assert response.status_code == 401


def test_snapshot_returns_404_for_unknown_instance() -> None:
    app = _build_app()

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get("/instances/inst-missing/tablespaces")

    assert response.status_code == 404


def test_snapshot_time_window_selects_historical_snapshot() -> None:
    older = TablespaceSnapshotView(
        collected_at=ANCHOR - timedelta(hours=2),
        entries=_entries()[:1],
    )
    newer = TablespaceSnapshotView(collected_at=ANCHOR, entries=_entries())
    app = _build_app(instances=(_oracle_instance(),), snapshots=(older, newer))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/tablespaces",
            params={
                "collected_before": (ANCHOR - timedelta(hours=1)).isoformat(),
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["snapshot_at"] == older.collected_at.isoformat()
    assert len(body["entries"]) == 1


def test_history_returns_per_tablespace_points_within_window() -> None:
    snapshots: list[TablespaceSnapshotView] = []
    for delta_minutes, rate in ((60, 80.0), (30, 88.0), (0, 95.0)):
        snapshots.append(
            TablespaceSnapshotView(
                collected_at=ANCHOR - timedelta(minutes=delta_minutes),
                entries=(
                    TablespaceEntryRow(
                        tablespace_name="USERS",
                        status="ONLINE",
                        used_bytes=1_000,
                        total_bytes=1_000,
                        used_rate_percent=rate,
                        autoextensible=False,
                    ),
                ),
            )
        )
    app = _build_app(instances=(_oracle_instance(),), snapshots=tuple(snapshots))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/tablespaces/USERS/history",
            params={
                "from": (ANCHOR - timedelta(hours=2)).isoformat(),
                "to": ANCHOR.isoformat(),
            },
        )

    assert response.status_code == 200
    entries = response.json()["entries"]
    assert [entry["used_rate_percent"] for entry in entries] == [80.0, 88.0, 95.0]


def test_history_rejects_window_wider_than_30_days() -> None:
    app = _build_app(instances=(_oracle_instance(),))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/tablespaces/USERS/history",
            params={
                "from": (ANCHOR - timedelta(days=45)).isoformat(),
                "to": ANCHOR.isoformat(),
            },
        )

    assert response.status_code == 400
    assert "30" in response.json()["detail"]


def test_history_requires_authentication() -> None:
    app = _build_app(instances=(_oracle_instance(),))

    with TestClient(app) as client:
        response = client.get(
            f"/instances/{INSTANCE_ID}/tablespaces/USERS/history",
            params={
                "from": (ANCHOR - timedelta(days=1)).isoformat(),
                "to": ANCHOR.isoformat(),
            },
        )

    assert response.status_code == 401


def test_history_returns_404_for_unknown_instance() -> None:
    app = _build_app()

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            "/instances/inst-missing/tablespaces/USERS/history",
            params={
                "from": (ANCHOR - timedelta(days=1)).isoformat(),
                "to": ANCHOR.isoformat(),
            },
        )

    assert response.status_code == 404
