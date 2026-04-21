import importlib
import json
import os
import time

from fastapi.testclient import TestClient
from httpx import Response
import psycopg
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from db_monitor_api.settings import load_api_settings
from db_monitor_schema.runtime import bootstrap_api_runtime_schema

READY_WAIT_SECONDS = 30
RETRY_INTERVAL_SECONDS = 1


def test_api_runtime_reports_ready_with_live_postgres_and_clickhouse() -> None:
    _require_env("DB_MONITOR_RUNTIME")
    postgres_dsn = _require_env("DB_MONITOR_POSTGRES_DSN")
    clickhouse_database = _require_env("DB_MONITOR_CLICKHOUSE_DATABASE")
    clickhouse_endpoint = _require_env("DB_MONITOR_CLICKHOUSE_ENDPOINT")
    clickhouse_username = _require_env("DB_MONITOR_CLICKHOUSE_USERNAME")
    clickhouse_password = _require_env("DB_MONITOR_CLICKHOUSE_PASSWORD")
    settings = load_api_settings()

    _wait_for_postgres(postgres_dsn)
    _wait_for_clickhouse(
        database=clickhouse_database,
        endpoint=clickhouse_endpoint,
        password=clickhouse_password,
        username=clickhouse_username,
    )
    bootstrap_api_runtime_schema(settings)
    app = importlib.import_module("db_monitor_api.main").build_app_from_environment()

    with TestClient(app) as client:
        live_response = client.get("/health/live")
        ready_response = _wait_until_ready(client)

    assert live_response.status_code == 200
    assert live_response.json() == {"mode": "postgres", "status": "live"}
    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"
    assert ready_response.json()["mode"] == "postgres"
    assert ready_response.json()["dependencies"] == [
        {
            "detail": "SELECT 1 ok",
            "name": "postgres",
            "ready": True,
        },
        {
            "detail": "SELECT 1 ok",
            "name": "clickhouse",
            "ready": True,
        },
    ]


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _wait_until_ready(client: TestClient) -> Response:
    deadline = time.monotonic() + READY_WAIT_SECONDS
    last_response = client.get("/health/ready")
    while time.monotonic() < deadline:
        if last_response.status_code == 200:
            return last_response
        time.sleep(RETRY_INTERVAL_SECONDS)
        last_response = client.get("/health/ready")
    return last_response


def _wait_for_clickhouse(
    *,
    database: str,
    endpoint: str,
    password: str,
    username: str,
) -> None:
    deadline = time.monotonic() + READY_WAIT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            rows = _run_clickhouse_query(
                database=database,
                endpoint=endpoint,
                password=password,
                query="SELECT 1 AS ready FORMAT JSONEachRow",
                username=username,
            )
            if rows == [{"ready": 1}]:
                return
        except Exception as error:  # pragma: no cover - retry path
            last_error = error
        time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("ClickHouse did not become ready for the API runtime gate.") from last_error


def _wait_for_postgres(postgres_dsn: str) -> None:
    deadline = time.monotonic() + READY_WAIT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(postgres_dsn) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            return
        except psycopg.Error as error:
            last_error = error
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("PostgreSQL did not become ready for the API runtime gate.") from last_error


def _run_clickhouse_query(
    *,
    database: str,
    endpoint: str,
    password: str,
    query: str,
    username: str,
) -> list[dict[str, object]]:
    request = Request(
        url=f"{endpoint.rstrip('/')}/?{urlencode({'database': database, 'query': query})}",
        data=b"",
        headers={"X-ClickHouse-Key": password, "X-ClickHouse-User": username},
        method="POST",
    )
    with urlopen(request) as response:
        body = response.read().decode("utf-8")
    return [json.loads(line) for line in body.splitlines() if line]
