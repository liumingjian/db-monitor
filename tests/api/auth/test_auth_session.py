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


def test_admin_can_update_existing_user_roles_and_audit_change(
    client: TestClient,
    runtime: AppRuntime,
) -> None:
    login_response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )

    assert login_response.status_code == 200

    update_response = client.put(
        "/auth/users/user-viewer/roles",
        json={"roles": ["operator"]},
    )

    assert update_response.status_code == 200
    assert update_response.json() == {
        "active_organization_id": "org-internal",
        "display_name": "Read Only User",
        "effective_permissions": [
            "instances:action",
            "instances:read",
            "instances:write",
            "rules:read",
            "rules:write",
            "settings:read",
        ],
        "roles": ["operator"],
        "user_id": "user-viewer",
        "username": "viewer",
    }
    assert runtime.audit_repository.entries[-1].action == "users.roles.update"
    assert runtime.audit_repository.entries[-1].resource == "user:user-viewer"

    relogin_response = client.post(
        "/auth/login",
        json={"password": "viewer-password", "username": "viewer"},
    )

    assert relogin_response.status_code == 200

    me_response = client.get("/auth/me")

    assert me_response.status_code == 200
    assert me_response.json()["roles"] == ["operator"]
    assert me_response.json()["permissions"] == [
        "instances:action",
        "instances:read",
        "instances:write",
        "rules:read",
        "rules:write",
        "settings:read",
    ]


def test_role_update_rejects_unknown_roles(client: TestClient) -> None:
    login_response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )

    assert login_response.status_code == 200

    response = client.put(
        "/auth/users/user-viewer/roles",
        json={"roles": ["super-admin"]},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Unknown roles: super-admin"}
