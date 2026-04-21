from fastapi.testclient import TestClient

from tests.support import StaticOracleConnectionValidator


def test_mysql_instance_contract_hides_password_and_exposes_validation(
    client: TestClient,
) -> None:
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
            "labels": ["primary", "critical"],
            "name": "prod-primary",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["connection"] == {
        "database": "mysql",
        "host": "127.0.0.1",
        "port": 3306,
        "username": "db_monitor",
    }
    assert body["engine"] == "mysql"
    assert body["validation"]["status"] == "passed"
    assert "password" not in body["connection"]


def test_oracle_instance_contract_uses_dsn_identifier(
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
            "labels": ["oracle", "baseline"],
            "name": "prod-oracle-primary",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["connection"] == {
        "database": "ORCLCDB",
        "host": "127.0.0.1",
        "port": 1521,
        "username": "system",
    }
    assert body["engine"] == "oracle"
    assert body["validation"]["status"] == "passed"
    assert "password" not in body["connection"]


def test_legacy_mysql_instance_route_remains_available(client: TestClient) -> None:
    client.post("/auth/login", json={"password": "admin-password", "username": "admin"})

    response = client.post(
        "/control/mysql-instances",
        json={
            "connection": {
                "database": "mysql",
                "host": "127.0.0.1",
                "password": "secret",
                "port": 3306,
                "username": "db_monitor",
            },
            "environment": "prod",
            "labels": ["legacy"],
            "name": "legacy-primary",
        },
    )

    assert response.status_code == 201
    assert response.json()["engine"] == "mysql"
