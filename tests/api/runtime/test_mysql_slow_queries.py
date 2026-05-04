"""`GET /instances/{instance_id}/slow-queries` contract (ADR-0007)."""

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
from db_monitor_api.runtime_views.slow_query_domain import SlowQueryEntryRow
from db_monitor_api.runtime_views.slow_query_repository import InMemorySlowQueryRepository
from tests.support import StaticMySQLConnectionValidator


INSTANCE_ID = "inst-slowq-api"
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


def _entry(
    *,
    event_id: int,
    timer_wait_ms: float,
    started_at: datetime,
    user: str = "app",
    schema_name: str = "ordering",
    digest: str = "digest-default",
) -> SlowQueryEntryRow:
    return SlowQueryEntryRow(
        event_id=event_id,
        started_at=started_at,
        user=user,
        schema_name=schema_name,
        sql_text=f"SELECT {event_id}",
        digest=digest,
        timer_wait_ms=timer_wait_ms,
        rows_examined=100,
        rows_sent=10,
        rows_affected=0,
        errors=0,
    )


def _build_app(
    *,
    entries: tuple[SlowQueryEntryRow, ...] = (),
    instances: tuple[MonitoredInstance, ...] = (),
) -> FastAPI:
    control_plane_repository = InMemoryControlPlaneRepository()
    for instance in instances:
        control_plane_repository.create_instance(instance)
    slow_query_repository = InMemorySlowQueryRepository()
    for entry in entries:
        slow_query_repository.add(
            instance_id=INSTANCE_ID,
            organization_id=ORGANIZATION_ID,
            entry=entry,
        )
    return create_app(
        runtime=build_local_runtime(
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
            slow_query_repository=slow_query_repository,
        )
    )


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def test_returns_top_entries_sorted_by_duration() -> None:
    entries = (
        _entry(event_id=1, timer_wait_ms=1500.0, started_at=ANCHOR - timedelta(minutes=1)),
        _entry(event_id=2, timer_wait_ms=4500.0, started_at=ANCHOR - timedelta(minutes=2)),
        _entry(event_id=3, timer_wait_ms=2500.0, started_at=ANCHOR - timedelta(minutes=3)),
    )
    app = _build_app(instances=(_instance(),), entries=entries)

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/slow-queries",
            params={
                "started_after": (ANCHOR - timedelta(minutes=15)).isoformat(),
                "started_before": ANCHOR.isoformat(),
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert [entry["event_id"] for entry in body["entries"]] == [2, 3, 1]
    assert body["window"]["from_at"].startswith("2026-04-22T09:45")
    assert body["window"]["to_at"].startswith("2026-04-22T10:00")


def test_filters_by_min_duration_and_user_and_schema() -> None:
    entries = (
        _entry(event_id=1, timer_wait_ms=1500.0, started_at=ANCHOR - timedelta(minutes=1)),
        _entry(
            event_id=2,
            timer_wait_ms=5500.0,
            started_at=ANCHOR - timedelta(minutes=2),
            user="reports",
        ),
        _entry(
            event_id=3,
            timer_wait_ms=9500.0,
            started_at=ANCHOR - timedelta(minutes=3),
            user="app",
            schema_name="analytics",
        ),
    )
    app = _build_app(instances=(_instance(),), entries=entries)

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/slow-queries",
            params={
                "min_duration_ms": 2000,
                "user": "app",
                "schema": "ordering",
                "started_after": (ANCHOR - timedelta(minutes=15)).isoformat(),
                "started_before": ANCHOR.isoformat(),
            },
        )

    assert response.status_code == 200
    body = response.json()
    # event 1: below min_duration; event 2: wrong user; event 3: wrong schema.
    assert body["entries"] == []


def test_digest_prefix_filter_applies() -> None:
    entries = (
        _entry(
            event_id=1,
            timer_wait_ms=1500.0,
            started_at=ANCHOR - timedelta(minutes=1),
            digest="abcdef1234",
        ),
        _entry(
            event_id=2,
            timer_wait_ms=5500.0,
            started_at=ANCHOR - timedelta(minutes=2),
            digest="abcxyz9999",
        ),
        _entry(
            event_id=3,
            timer_wait_ms=9500.0,
            started_at=ANCHOR - timedelta(minutes=3),
            digest="999fff0000",
        ),
    )
    app = _build_app(instances=(_instance(),), entries=entries)

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/slow-queries",
            params={
                "digest_prefix": "abc",
                "started_after": (ANCHOR - timedelta(minutes=15)).isoformat(),
                "started_before": ANCHOR.isoformat(),
            },
        )

    assert response.status_code == 200
    event_ids = [entry["event_id"] for entry in response.json()["entries"]]
    assert set(event_ids) == {1, 2}


def test_limit_rejected_when_over_cap() -> None:
    app = _build_app(instances=(_instance(),))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(
            f"/instances/{INSTANCE_ID}/slow-queries",
            params={"limit": 500},
        )

    assert response.status_code == 422


def test_returns_empty_window_when_no_entries() -> None:
    app = _build_app(instances=(_instance(),))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get(f"/instances/{INSTANCE_ID}/slow-queries")

    assert response.status_code == 200
    assert response.json()["entries"] == []


def test_returns_404_for_unknown_instance() -> None:
    app = _build_app()

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get("/instances/inst-missing/slow-queries")

    assert response.status_code == 404


def test_requires_authentication() -> None:
    app = _build_app(instances=(_instance(),))

    with TestClient(app) as client:
        response = client.get(f"/instances/{INSTANCE_ID}/slow-queries")

    assert response.status_code == 401
