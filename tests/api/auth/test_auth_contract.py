from fastapi.testclient import TestClient


def test_login_contract_returns_identity_and_permissions(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "active_organization": {
            "name": "Internal Operations",
            "organization_id": "org-internal",
            "slug": "internal-ops",
        },
        "display_name": "Platform Admin",
        "organization_memberships": [
            {
                "organization": {
                    "name": "Internal Operations",
                    "organization_id": "org-internal",
                    "slug": "internal-ops",
                },
                "roles": ["admin"],
            }
        ],
        "permissions": [
            "instances:action",
            "instances:read",
            "instances:write",
            "rules:read",
            "rules:write",
            "settings:read",
            "settings:write",
        ],
        "roles": ["admin"],
        "user_id": "user-admin",
        "username": "admin",
    }


def test_me_contract_requires_authenticated_session(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing session cookie."}


def test_admin_can_read_user_directory_and_role_catalog(client: TestClient) -> None:
    login_response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )

    assert login_response.status_code == 200

    users_response = client.get("/auth/users")
    roles_response = client.get("/auth/roles")

    assert users_response.status_code == 200
    assert users_response.json() == [
        {
            "active_organization_id": "org-internal",
            "display_name": "Operations Engineer",
            "effective_permissions": [
                "instances:action",
                "instances:read",
                "instances:write",
                "rules:read",
                "rules:write",
                "settings:read",
            ],
            "roles": ["operator"],
            "user_id": "user-ops",
            "username": "operator",
        },
        {
            "active_organization_id": "org-internal",
            "display_name": "Platform Admin",
            "effective_permissions": [
                "instances:action",
                "instances:read",
                "instances:write",
                "rules:read",
                "rules:write",
                "settings:read",
                "settings:write",
            ],
            "roles": ["admin"],
            "user_id": "user-admin",
            "username": "admin",
        },
        {
            "active_organization_id": "org-internal",
            "display_name": "Read Only User",
            "effective_permissions": [
                "instances:read",
                "rules:read",
                "settings:read",
            ],
            "roles": ["viewer"],
            "user_id": "user-viewer",
            "username": "viewer",
        },
    ]
    assert roles_response.status_code == 200
    assert roles_response.json() == [
        {
            "permissions": [
                "instances:action",
                "instances:read",
                "instances:write",
                "rules:read",
                "rules:write",
                "settings:read",
                "settings:write",
            ],
            "role": "admin",
        },
        {
            "permissions": [
                "instances:action",
                "instances:read",
                "instances:write",
                "rules:read",
                "rules:write",
                "settings:read",
            ],
            "role": "operator",
        },
        {
            "permissions": [
                "instances:read",
                "rules:read",
                "settings:read",
            ],
            "role": "viewer",
        },
    ]
