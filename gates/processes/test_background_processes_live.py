from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import subprocess
import time
from typing import cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import psycopg
import redis

from db_monitor_api.settings import ClickHouseSettings
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    MySQLConnectionConfig,
    MySQLInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.postgres_repository import PostgresControlPlaneRepository
from db_monitor_pipeline.queue import DEFAULT_QUEUE_NAME, REDIS_DEDUPE_SUFFIX
from db_monitor_schema.clickhouse import bootstrap_clickhouse_schema
from db_monitor_schema.postgres import bootstrap_postgres_schema

CLICKHOUSE_WAIT_SECONDS = 30
POSTGRES_WAIT_SECONDS = 30
REDIS_WAIT_SECONDS = 30
REPO_ROOT = Path(__file__).resolve().parents[2]
RETRY_INTERVAL_SECONDS = 1
TEST_INSTANCE_ID = "inst-process-live"
TEST_MYSQL_CONNECTION = MySQLConnectionConfig(
    database="mysql_probe",
    host="127.0.0.1",
    password="db_monitor",
    port=3306,
    username="db_monitor",
)


def test_background_process_entrypoints_dispatch_and_collect_metrics() -> None:
    env = _build_process_env()

    _wait_for_postgres(env["DB_MONITOR_POSTGRES_DSN"])
    _wait_for_clickhouse(env)
    _wait_for_redis(env["DB_MONITOR_REDIS_URL"])
    _reset_live_state(env)
    bootstrap_clickhouse_schema(settings=_clickhouse_settings(env))

    idle_worker_result = _run_process(module="db_monitor_worker_mysql.main", env=env)
    _seed_validated_instance(env["DB_MONITOR_POSTGRES_DSN"])
    scheduler_result = _run_process(module="db_monitor_scheduler.main", env=env)

    assert idle_worker_result["status"] == "idle"
    assert idle_worker_result["processed_metrics"] == 0
    assert scheduler_result["status"] == "dispatched"
    assert scheduler_result["dispatched_jobs"] == 1
    assert _redis_queue_size(env["DB_MONITOR_REDIS_URL"]) == 1


def _build_process_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "DB_MONITOR_CLICKHOUSE_DATABASE": "db_monitor",
            "DB_MONITOR_CLICKHOUSE_ENDPOINT": "http://127.0.0.1:8123",
            "DB_MONITOR_CLICKHOUSE_PASSWORD": "db_monitor",
            "DB_MONITOR_CLICKHOUSE_USERNAME": "db_monitor",
            "DB_MONITOR_POSTGRES_DSN": _required_env("DB_MONITOR_POSTGRES_DSN"),
            "DB_MONITOR_REDIS_URL": _required_env("DB_MONITOR_REDIS_URL"),
            "DB_MONITOR_SCHEDULER_MODE": "oneshot",
            "DB_MONITOR_WORKER_MYSQL_MODE": "oneshot",
            "PYTHONPATH": os.pathsep.join(
                [
                    str(REPO_ROOT / "apps" / "api" / "src"),
                    str(REPO_ROOT / "apps" / "scheduler" / "src"),
                    str(REPO_ROOT / "apps" / "worker-mysql" / "src"),
                ]
            ),
        }
    )
    return env


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _wait_for_postgres(postgres_dsn: str) -> None:
    deadline = time.monotonic() + POSTGRES_WAIT_SECONDS
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(postgres_dsn) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            return
        except psycopg.Error:
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("PostgreSQL did not become ready for the background process gate.")


def _wait_for_redis(redis_url: str) -> None:
    deadline = time.monotonic() + REDIS_WAIT_SECONDS
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    while time.monotonic() < deadline:
        try:
            if client.ping():
                return
        except redis.RedisError:
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("Redis did not become ready for the background process gate.")


def _wait_for_clickhouse(env: dict[str, str]) -> None:
    deadline = time.monotonic() + CLICKHOUSE_WAIT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            rows = _run_clickhouse_query(
                database=env["DB_MONITOR_CLICKHOUSE_DATABASE"],
                endpoint=env["DB_MONITOR_CLICKHOUSE_ENDPOINT"],
                password=env["DB_MONITOR_CLICKHOUSE_PASSWORD"],
                query="SELECT 1 AS ready FORMAT JSONEachRow",
                username=env["DB_MONITOR_CLICKHOUSE_USERNAME"],
            )
            if rows == [{"ready": 1}]:
                return
        except Exception as error:  # pragma: no cover - retry path
            last_error = error
        time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("ClickHouse did not become ready for the background process gate.") from last_error


def _reset_live_state(env: dict[str, str]) -> None:
    with psycopg.connect(env["DB_MONITOR_POSTGRES_DSN"]) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS schema_version")
            cursor.execute("DROP TABLE IF EXISTS control_mysql_instances")
            cursor.execute("DROP TABLE IF EXISTS control_settings")
    bootstrap_postgres_schema(postgres_dsn=env["DB_MONITOR_POSTGRES_DSN"])
    redis.Redis.from_url(env["DB_MONITOR_REDIS_URL"], decode_responses=True).delete(
        DEFAULT_QUEUE_NAME,
        f"{DEFAULT_QUEUE_NAME}{REDIS_DEDUPE_SUFFIX}",
    )


def _seed_validated_instance(postgres_dsn: str) -> None:
    repository = PostgresControlPlaneRepository(postgres_dsn=postgres_dsn)
    repository.upsert_instance(
        MySQLInstance(
            connection=TEST_MYSQL_CONNECTION,
            created_at=utc_now(),
            environment="prod",
            instance_id=TEST_INSTANCE_ID,
            labels=("primary", "live-gate"),
            name="prod-primary-live",
            validation=ConnectionValidation(
                checked_at=datetime.now(tz=UTC) - timedelta(minutes=1),
                detail="Seeded for background process live gate.",
                server_version="8.4.0",
                status=ValidationStatus.PASSED,
            ),
        )
    )


def _run_process(*, env: dict[str, str], module: str) -> dict[str, object]:
    result = subprocess.run(
        ["uv", "run", "python", "-m", module],
        capture_output=True,
        check=False,
        cwd=REPO_ROOT,
        env=env,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{module} failed with exit code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    payload = result.stdout.strip().splitlines()[-1]
    return cast(dict[str, object], json.loads(payload))


def _redis_queue_size(redis_url: str) -> int:
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    return int(cast(int, client.llen(DEFAULT_QUEUE_NAME)))


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


def _clickhouse_settings(env: dict[str, str]) -> ClickHouseSettings:
    return ClickHouseSettings(
        database=env["DB_MONITOR_CLICKHOUSE_DATABASE"],
        endpoint=env["DB_MONITOR_CLICKHOUSE_ENDPOINT"],
        password=env["DB_MONITOR_CLICKHOUSE_PASSWORD"],
        username=env["DB_MONITOR_CLICKHOUSE_USERNAME"],
    )
