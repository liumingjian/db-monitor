from fastapi.testclient import TestClient

from db_monitor_api.runtime import AppRuntime


def test_session_lifecycle_persists_across_requests(
    client: TestClient,
    runtime: AppRuntime,
) -> None:
    login_response = client.post(
        "/auth/login",
        json={"password": "operator-password", "username": "operator"},
    )

    assert login_response.status_code == 200
    assert "dbmon_session" in client.cookies

    me_response = client.get("/auth/me")

    assert me_response.status_code == 200
    assert me_response.json()["username"] == "operator"
    assert me_response.json()["active_organization"] == {
        "name": "Internal Operations",
        "organization_id": "org-internal",
        "slug": "internal-ops",
    }
    assert me_response.json()["organization_memberships"] == [
        {
            "organization": {
                "name": "Internal Operations",
                "organization_id": "org-internal",
                "slug": "internal-ops",
            },
            "roles": ["operator"],
        }
    ]
    assert runtime.audit_repository.entries[0].action == "auth.login"

    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 204
    assert "dbmon_session" not in client.cookies
    assert runtime.audit_repository.entries[-1].action == "auth.logout"


def test_session_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "wrong-password", "username": "viewer"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password."}


def test_admin_can_read_recent_audit_entries(client: TestClient) -> None:
    login_response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )

    assert login_response.status_code == 200

    response = client.get("/auth/audit-entries?limit=5")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["action"] == "auth.login"
    assert response.json()[0]["organization_id"] == "org-internal"


def test_non_admin_is_denied_audit_history(client: TestClient, runtime: AppRuntime) -> None:
    login_response = client.post(
        "/auth/login",
        json={"password": "viewer-password", "username": "viewer"},
    )

    assert login_response.status_code == 200

    response = client.get("/auth/audit-entries")

    assert response.status_code == 403
    assert response.json() == {"detail": "Missing permission: settings:write"}
    assert runtime.audit_repository.entries[-1].action == "audit.denied"
    assert runtime.audit_repository.entries[-1].outcome == "denied"
