import json
import os
from pathlib import Path
import subprocess
import time
from typing import cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import psycopg

from db_monitor_api.bootstrap import build_runtime_from_settings
from db_monitor_api.settings import ApiSettings, ClickHouseSettings, load_api_settings
from db_monitor_pipeline.process_settings import (
    SchedulerProcessSettings,
    WorkerProcessSettings,
    load_scheduler_process_settings,
    load_worker_process_settings,
)
from db_monitor_pipeline.processes import build_scheduler_process, build_worker_process
from db_monitor_schema.clickhouse import read_clickhouse_schema_version
from db_monitor_schema.postgres import read_postgres_schema_version

CLICKHOUSE_DATABASE_ENV = "DB_MONITOR_CLICKHOUSE_DATABASE"
CLICKHOUSE_ENDPOINT_ENV = "DB_MONITOR_CLICKHOUSE_ENDPOINT"
CLICKHOUSE_PASSWORD_ENV = "DB_MONITOR_CLICKHOUSE_PASSWORD"
CLICKHOUSE_USERNAME_ENV = "DB_MONITOR_CLICKHOUSE_USERNAME"
POSTGRES_DSN_ENV = "DB_MONITOR_POSTGRES_DSN"
READY_TIMEOUT_SECONDS = 30
REPO_ROOT = Path(__file__).resolve().parents[2]
RETRY_INTERVAL_SECONDS = 1


def test_schema_bootstrap_gate_initializes_runtime_schema_and_unblocks_startup() -> None:
    postgres_dsn = _required_env(POSTGRES_DSN_ENV)
    settings = load_api_settings()
    if settings.clickhouse is None:
        raise RuntimeError("Schema bootstrap gate requires ClickHouse settings.")

    _wait_for_postgres(postgres_dsn)
    _wait_for_clickhouse(settings)
    _reset_postgres_schema(postgres_dsn)
    _reset_clickhouse_schema(settings)
    _assert_verify_runtime_fails()

    bootstrap_result = _run_schema_command("bootstrap-runtime")
    verify_result = _run_schema_command("verify-runtime")

    postgres_version = read_postgres_schema_version(postgres_dsn=postgres_dsn)
    clickhouse_version = read_clickhouse_schema_version(settings=settings.clickhouse)
    assert postgres_version is not None
    assert clickhouse_version is not None
    assert bootstrap_result["schemas"] == verify_result["schemas"]
    assert build_runtime_from_settings(settings).runtime_mode == "postgres"
    assert build_scheduler_process(_scheduler_settings(postgres_dsn)).poll_seconds > 0
    assert build_worker_process(_worker_settings()).poll_seconds > 0


def _assert_verify_runtime_fails() -> None:
    result = subprocess.run(
        ["uv", "run", "python", "-m", "db_monitor_schema", "verify-runtime"],
        capture_output=True,
        check=False,
        cwd=REPO_ROOT,
        env=_schema_command_env(),
        text=True,
    )
    if result.returncode == 0:
        raise AssertionError("verify-runtime unexpectedly succeeded before bootstrap.")
    if "bootstrapped" not in (result.stdout + result.stderr):
        raise AssertionError(result.stdout + result.stderr)


def _run_schema_command(command: str) -> dict[str, object]:
    result = subprocess.run(
        ["uv", "run", "python", "-m", "db_monitor_schema", command],
        capture_output=True,
        check=False,
        cwd=REPO_ROOT,
        env=_schema_command_env(),
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return cast(dict[str, object], json.loads(result.stdout))


def _scheduler_settings(postgres_dsn: str) -> SchedulerProcessSettings:
    return load_scheduler_process_settings(
        {
            "DB_MONITOR_POSTGRES_DSN": postgres_dsn,
            "DB_MONITOR_REDIS_URL": "redis://127.0.0.1:6379/0",
        }
    )


def _worker_settings() -> WorkerProcessSettings:
    return load_worker_process_settings(
        {
            "DB_MONITOR_CLICKHOUSE_DATABASE": _required_env(CLICKHOUSE_DATABASE_ENV),
            "DB_MONITOR_CLICKHOUSE_ENDPOINT": _required_env(CLICKHOUSE_ENDPOINT_ENV),
            "DB_MONITOR_CLICKHOUSE_PASSWORD": _required_env(CLICKHOUSE_PASSWORD_ENV),
            "DB_MONITOR_CLICKHOUSE_USERNAME": _required_env(CLICKHOUSE_USERNAME_ENV),
            "DB_MONITOR_REDIS_URL": "redis://127.0.0.1:6379/0",
        }
    )


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _wait_for_postgres(postgres_dsn: str) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
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
    raise RuntimeError("PostgreSQL did not become ready for the schema bootstrap gate.") from last_error


def _wait_for_clickhouse(settings: ApiSettings) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            clickhouse = _clickhouse_settings(settings)
            rows = _run_clickhouse_query(
                database=_required_env(CLICKHOUSE_DATABASE_ENV),
                endpoint=clickhouse.endpoint,
                password=clickhouse.password,
                query="SELECT 1 AS ready FORMAT JSONEachRow",
                username=clickhouse.username,
            )
            if rows == [{"ready": 1}]:
                return
        except Exception as error:  # pragma: no cover - retry path
            last_error = error
        time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("ClickHouse did not become ready for the schema bootstrap gate.") from last_error


def _reset_postgres_schema(postgres_dsn: str) -> None:
    with psycopg.connect(postgres_dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS schema_version")
            cursor.execute("DROP TABLE IF EXISTS alert_history")
            cursor.execute("DROP TABLE IF EXISTS alert_records")
            cursor.execute("DROP TABLE IF EXISTS rule_instance_overrides")
            cursor.execute("DROP TABLE IF EXISTS alert_rules")
            cursor.execute("DROP TABLE IF EXISTS instance_parameters")
            cursor.execute("DROP TABLE IF EXISTS control_mysql_instances")
            cursor.execute("DROP TABLE IF EXISTS control_settings")


def _reset_clickhouse_schema(settings: ApiSettings) -> None:
    database = _required_env(CLICKHOUSE_DATABASE_ENV)
    clickhouse = _clickhouse_settings(settings)
    for table in (
        "schema_version",
        "metric_samples",
        "mysql_processlist",
        "mysql_slow_query_events",
        "oracle_tablespaces",
    ):
        _run_clickhouse_query(
            database=database,
            endpoint=clickhouse.endpoint,
            password=clickhouse.password,
            query=f"DROP TABLE IF EXISTS {table}",
            username=clickhouse.username,
        )


def _clickhouse_settings(settings: ApiSettings) -> ClickHouseSettings:
    if settings.clickhouse is None:
        raise RuntimeError("Schema bootstrap gate requires ClickHouse settings.")
    return settings.clickhouse


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


def _schema_command_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "apps" / "api" / "src")
    return env
