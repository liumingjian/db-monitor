from datetime import UTC, datetime

from fastapi.testclient import TestClient

from db_monitor_api.alerting.notification import (
    InMemoryNotifyHistoryRepository,
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)
from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_local_runtime


def _seed_history(repo: InMemoryNotifyHistoryRepository) -> None:
    payload = NotifyPayload(
        rule_id="rule-1",
        rule_name="Too many connections",
        organization_id="org-internal",
        instance_id="mysql-1",
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity="critical",
        occurred_at=datetime(2026, 4, 22, 12, 0, tzinfo=UTC),
    )
    repo.record(
        payload=payload,
        result=NotifyResult(
            channel="feishu",
            status=NotifyStatus.DELIVERED,
            attempt=1,
            delivered_at=datetime(2026, 4, 22, 12, 0, 2, tzinfo=UTC),
            error=None,
        ),
    )
    repo.record(
        payload=payload,
        result=NotifyResult(
            channel="smtp",
            status=NotifyStatus.FAILED,
            attempt=3,
            delivered_at=None,
            error="Connection refused",
        ),
    )


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def _build_app_with_history() -> InMemoryNotifyHistoryRepository:
    history_repo = InMemoryNotifyHistoryRepository()
    _seed_history(history_repo)
    return history_repo


def test_list_notify_history_returns_most_recent_first() -> None:
    history_repo = _build_app_with_history()
    app = create_app(runtime=build_local_runtime(notify_history_repository=history_repo))
    with TestClient(app) as client:
        _login_admin(client)
        response = client.get("/admin/notify-history")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["channel"] == "smtp"
    assert body[0]["status"] == "failed"
    assert body[1]["channel"] == "feishu"
    assert body[1]["status"] == "delivered"
    assert body[1]["delivered_at"] is not None


def test_list_notify_history_filters_by_status() -> None:
    history_repo = _build_app_with_history()
    app = create_app(runtime=build_local_runtime(notify_history_repository=history_repo))
    with TestClient(app) as client:
        _login_admin(client)
        response = client.get("/admin/notify-history?status=failed")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["channel"] == "smtp"


def test_list_notify_history_filters_by_channel_and_rule() -> None:
    history_repo = _build_app_with_history()
    app = create_app(runtime=build_local_runtime(notify_history_repository=history_repo))
    with TestClient(app) as client:
        _login_admin(client)
        response = client.get("/admin/notify-history?channel=feishu&rule_id=rule-1")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["channel"] == "feishu"


def test_list_notify_history_limit_bounded() -> None:
    history_repo = _build_app_with_history()
    app = create_app(runtime=build_local_runtime(notify_history_repository=history_repo))
    with TestClient(app) as client:
        _login_admin(client)
        response = client.get("/admin/notify-history?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_notify_history_requires_authentication() -> None:
    runtime = build_local_runtime()
    app = create_app(runtime=runtime)
    with TestClient(app) as client:
        response = client.get("/admin/notify-history")
    assert response.status_code == 401
