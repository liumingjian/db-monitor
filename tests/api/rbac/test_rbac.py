from fastapi.testclient import TestClient

from db_monitor_api.runtime import AppRuntime


def test_viewer_can_read_instances(client: TestClient) -> None:
    client.post("/auth/login", json={"password": "viewer-password", "username": "viewer"})

    response = client.get("/control/mysql-instances")

    assert response.status_code == 200
    assert response.json() == []


def test_viewer_is_denied_settings_write_and_audited(
    client: TestClient,
    runtime: AppRuntime,
) -> None:
    client.post("/auth/login", json={"password": "viewer-password", "username": "viewer"})

    response = client.put(
        "/control/settings/notification.channel",
        json={"value": "email"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Missing permission: settings:write"}
    assert runtime.audit_repository.entries[-1].action == "settings.denied"
    assert runtime.audit_repository.entries[-1].outcome == "denied"


def test_admin_settings_write_records_audit_entry(
    client: TestClient,
    runtime: AppRuntime,
) -> None:
    client.post("/auth/login", json={"password": "admin-password", "username": "admin"})

    response = client.put(
        "/control/settings/notification.channel",
        json={"value": "email"},
    )

    assert response.status_code == 200
    assert response.json()["key"] == "notification.channel"
    assert response.json()["value"] == "email"
    assert runtime.audit_repository.entries[-1].action == "settings.write"
    assert runtime.audit_repository.entries[-1].outcome == "allowed"
