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
