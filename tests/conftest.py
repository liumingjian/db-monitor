from collections.abc import Generator
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.runtime import AppRuntime
from tests.support import StaticMySQLConnectionValidator, StaticOracleConnectionValidator


@pytest.fixture
def mysql_validator() -> StaticMySQLConnectionValidator:
    return StaticMySQLConnectionValidator()


@pytest.fixture
def oracle_validator() -> StaticOracleConnectionValidator:
    return StaticOracleConnectionValidator()


@pytest.fixture
def app(
    mysql_validator: StaticMySQLConnectionValidator,
    oracle_validator: StaticOracleConnectionValidator,
) -> FastAPI:
    return create_app(
        runtime=build_local_runtime(
            mysql_validator=mysql_validator,
            oracle_validator=oracle_validator,
        )
    )


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def runtime(app: FastAPI) -> AppRuntime:
    return cast(AppRuntime, app.state.runtime)
