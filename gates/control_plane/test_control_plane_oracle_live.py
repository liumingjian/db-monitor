from collections.abc import Generator
import os
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient
import psycopg
import pytest

from db_monitor_api.app import create_app
from db_monitor_api.analytics.repository import InMemoryAnalyticsRepository
from db_monitor_api.bootstrap import build_postgres_runtime
from db_monitor_api.control_plane.domain import InstanceConnectionConfig, ValidationStatus
from db_monitor_api.control_plane.oracle_validation import PythonOracleConnectionValidator
from db_monitor_schema.postgres import bootstrap_postgres_schema

POSTGRES_GATE_DSN_ENV = "DB_MONITOR_POSTGRES_TEST_DSN"
LOCAL_POSTGRES_GATE_DSN = "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor"
ORACLE_HOST_ENV = "DB_MONITOR_ORACLE_TEST_HOST"
ORACLE_PASSWORD_ENV = "DB_MONITOR_ORACLE_TEST_PASSWORD"
ORACLE_PORT_ENV = "DB_MONITOR_ORACLE_TEST_PORT"
ORACLE_SERVICE_ENV = "DB_MONITOR_ORACLE_TEST_SERVICE"
ORACLE_USERNAME_ENV = "DB_MONITOR_ORACLE_TEST_USERNAME"
POSTGRES_WAIT_SECONDS = 30
ORACLE_WAIT_SECONDS = 120
RETRY_INTERVAL_SECONDS = 1


@pytest.fixture(scope="module")
def postgres_dsn() -> str:
    dsn = os.environ.get(POSTGRES_GATE_DSN_ENV, LOCAL_POSTGRES_GATE_DSN)
    _wait_for_postgres(dsn)
    _reset_control_plane_tables(dsn)
    bootstrap_postgres_schema(postgres_dsn=dsn)
    return dsn


@pytest.fixture(scope="module")
def oracle_connection() -> InstanceConnectionConfig:
    return InstanceConnectionConfig(
        database=os.environ.get(ORACLE_SERVICE_ENV, "XE"),
        host=os.environ.get(ORACLE_HOST_ENV, "127.0.0.1"),
        password=os.environ.get(ORACLE_PASSWORD_ENV, "oracle"),
        port=int(os.environ.get(ORACLE_PORT_ENV, "15211")),
        username=os.environ.get(ORACLE_USERNAME_ENV, "system"),
    )


@pytest.fixture(scope="module")
def oracle_validator(oracle_connection: InstanceConnectionConfig) -> PythonOracleConnectionValidator:
    validator = PythonOracleConnectionValidator()
    _wait_for_oracle(validator=validator, config=oracle_connection)
    return validator


@pytest.fixture
def postgres_app(
    postgres_dsn: str,
    oracle_validator: PythonOracleConnectionValidator,
) -> FastAPI:
    return create_app(
        runtime=build_postgres_runtime(
            analytics_repository=InMemoryAnalyticsRepository(),
            postgres_dsn=postgres_dsn,
            oracle_validator=oracle_validator,
        )
    )


@pytest.fixture
def postgres_client(postgres_app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(postgres_app) as test_client:
        yield test_client


def test_postgres_repository_persists_live_oracle_instance(
    postgres_client: TestClient,
    oracle_connection: InstanceConnectionConfig,
) -> None:
    _login_admin(postgres_client)
    create_response = postgres_client.post(
        "/control/instances",
        json={
            "connection": {
                "database": oracle_connection.database,
                "host": oracle_connection.host,
                "password": oracle_connection.password,
                "port": oracle_connection.port,
                "username": oracle_connection.username,
            },
            "engine": "oracle",
            "environment": "prod",
            "labels": ["oracle", "live-gate"],
            "name": "prod-oracle-primary",
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()["engine"] == "oracle"
    assert create_response.json()["validation"]["status"] == "passed"
    assert "Oracle connection validated successfully" in create_response.json()["validation"][
        "detail"
    ]

    validate_response = postgres_client.post(
        f"/control/instances/{create_response.json()['instance_id']}/validate"
    )
    assert validate_response.status_code == 200
    assert validate_response.json()["validation"]["status"] == "passed"

    detail_response = postgres_client.get(f"/control/instances/{create_response.json()['instance_id']}")
    assert detail_response.status_code == 200
    assert detail_response.json() == validate_response.json()

    list_response = postgres_client.get("/control/instances")
    assert list_response.status_code == 200
    assert [item["engine"] for item in list_response.json()] == ["oracle"]


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def _wait_for_oracle(
    *,
    validator: PythonOracleConnectionValidator,
    config: InstanceConnectionConfig,
) -> None:
    deadline = time.monotonic() + ORACLE_WAIT_SECONDS
    last_detail = "Oracle validation did not run."
    while time.monotonic() < deadline:
        validation = validator.validate(config)
        if validation.status is ValidationStatus.PASSED:
            return
        last_detail = validation.detail
        time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError(
        "Oracle XE did not become ready for the live control-plane gate: "
        f"{last_detail}"
    )


def _wait_for_postgres(dsn: str) -> None:
    deadline = time.monotonic() + POSTGRES_WAIT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(dsn) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            return
        except psycopg.Error as error:
            last_error = error
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("PostgreSQL did not become ready for the Oracle live gate.") from last_error


def _reset_control_plane_tables(dsn: str) -> None:
    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS schema_version")
            cursor.execute("DROP TABLE IF EXISTS control_mysql_instances")
            cursor.execute("DROP TABLE IF EXISTS control_settings")
