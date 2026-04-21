from fastapi.testclient import TestClient

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import ConnectionValidation, ValidationStatus

from tests.support import StaticMySQLConnectionValidator, StaticOracleConnectionValidator


def test_onboarding_requires_successful_validation_before_persist(
    client: TestClient,
    mysql_validator: StaticMySQLConnectionValidator,
) -> None:
    mysql_validator.next_result = ConnectionValidation(
        checked_at=utc_now(),
        detail="Access denied for onboarding.",
        server_version=None,
        status=ValidationStatus.FAILED,
    )
    client.post("/auth/login", json={"password": "admin-password", "username": "admin"})

    create_response = client.post(
        "/control/instances",
        json={
            "connection": {
                "database": "mysql",
                "host": "127.0.0.1",
                "password": "secret",
                "port": 3306,
                "username": "db_monitor",
            },
            "engine": "mysql",
            "environment": "prod",
            "labels": ["primary"],
            "name": "prod-primary",
        },
    )

    assert create_response.status_code == 400
    assert create_response.json() == {"detail": "Access denied for onboarding."}

    list_response = client.get("/control/instances")

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_onboarding_creates_mysql_instance_for_admin(client: TestClient) -> None:
    client.post("/auth/login", json={"password": "admin-password", "username": "admin"})

    response = client.post(
        "/control/instances",
        json={
            "connection": {
                "database": "mysql",
                "host": "127.0.0.1",
                "password": "secret",
                "port": 3306,
                "username": "db_monitor",
            },
            "engine": "mysql",
            "environment": "prod",
            "labels": ["primary"],
            "name": "prod-primary",
        },
    )

    assert response.status_code == 201
    assert response.json()["engine"] == "mysql"
    assert response.json()["name"] == "prod-primary"
    assert response.json()["labels"] == ["primary"]


def test_onboarding_creates_oracle_instance_for_admin(
    client: TestClient,
    oracle_validator: StaticOracleConnectionValidator,
) -> None:
    del oracle_validator
    client.post("/auth/login", json={"password": "admin-password", "username": "admin"})

    response = client.post(
        "/control/instances",
        json={
            "connection": {
                "database": "ORCLCDB",
                "host": "127.0.0.1",
                "password": "secret",
                "port": 1521,
                "username": "system",
            },
            "engine": "oracle",
            "environment": "prod",
            "labels": ["oracle"],
            "name": "prod-oracle-primary",
        },
    )

    assert response.status_code == 201
    assert response.json()["engine"] == "oracle"
    assert response.json()["name"] == "prod-oracle-primary"
    assert response.json()["labels"] == ["oracle"]
