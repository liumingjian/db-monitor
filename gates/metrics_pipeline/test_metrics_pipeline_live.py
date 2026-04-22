from collections.abc import Mapping
import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import uuid

import redis

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    MySQLConnectionConfig,
    MySQLInstance,
    ValidationStatus,
)
from db_monitor_api.settings import ClickHouseSettings
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.collector import MySQLMetricsCollector
from db_monitor_pipeline.queue import RedisCollectionTaskQueue
from db_monitor_pipeline.scheduler import MetricsDispatchService
from db_monitor_pipeline.sink import CLICKHOUSE_METRICS_TABLE, ClickHouseMetricSink
from db_monitor_pipeline.worker import MySQLMetricsWorker
from db_monitor_schema.clickhouse import bootstrap_clickhouse_schema

CLICKHOUSE_DATABASE_ENV = "DB_MONITOR_CLICKHOUSE_DATABASE"
CLICKHOUSE_ENDPOINT_ENV = "DB_MONITOR_CLICKHOUSE_ENDPOINT"
CLICKHOUSE_PASSWORD_ENV = "DB_MONITOR_CLICKHOUSE_PASSWORD"
CLICKHOUSE_USERNAME_ENV = "DB_MONITOR_CLICKHOUSE_USERNAME"
EXPECTED_METRIC_COUNT = 9
REDIS_URL_ENV = "DB_MONITOR_REDIS_URL"
READY_TIMEOUT_SECONDS = 30
RETRY_INTERVAL_SECONDS = 1


class StaticCollector(MySQLMetricsCollector):
    def collect(self, connection: MySQLConnectionConfig) -> Mapping[str, str]:
        del connection
        return {
            "Bytes_received": "128",
            "Bytes_sent": "256",
            "Innodb_buffer_pool_reads": "2",
            "Questions": "42",
            "Seconds_Behind_Source": "0",
            "Threads_connected": "10",
            "Threads_running": "3",
            "Uptime": "3600",
        }


def test_live_metrics_pipeline_round_trips_through_redis_and_clickhouse() -> None:
    redis_url = _required_env(REDIS_URL_ENV)
    clickhouse_database = _required_env(CLICKHOUSE_DATABASE_ENV)
    clickhouse_endpoint = _required_env(CLICKHOUSE_ENDPOINT_ENV)
    clickhouse_password = _required_env(CLICKHOUSE_PASSWORD_ENV)
    clickhouse_username = _required_env(CLICKHOUSE_USERNAME_ENV)
    queue_name = f"db-monitor:test:{uuid.uuid4().hex}"
    instance_id = f"inst-{uuid.uuid4().hex}"

    _wait_for_redis(redis_url)
    _wait_for_clickhouse(
        database=clickhouse_database,
        endpoint=clickhouse_endpoint,
        password=clickhouse_password,
        username=clickhouse_username,
    )
    bootstrap_clickhouse_schema(
        settings=ClickHouseSettings(
            database=clickhouse_database,
            endpoint=clickhouse_endpoint,
            password=clickhouse_password,
            username=clickhouse_username,
        )
    )

    repository = InMemoryControlPlaneRepository()
    repository.create_instance(_build_instance(instance_id=instance_id))

    dispatched = MetricsDispatchService(
        control_plane_repository=repository,
        queue=RedisCollectionTaskQueue(queue_name=queue_name, redis_url=redis_url),
    ).dispatch_collection_jobs()
    result = MySQLMetricsWorker(
        collector=StaticCollector(),
        queue=RedisCollectionTaskQueue(queue_name=queue_name, redis_url=redis_url),
        sink=ClickHouseMetricSink(
            database=clickhouse_database,
            endpoint=clickhouse_endpoint,
            password=clickhouse_password,
            username=clickhouse_username,
        ),
    ).process_next()

    assert dispatched == 1
    assert result.status == "processed"
    assert result.processed_metrics == EXPECTED_METRIC_COUNT
    rows = _wait_for_metric_rows(
        database=clickhouse_database,
        endpoint=clickhouse_endpoint,
        instance_id=instance_id,
        password=clickhouse_password,
        username=clickhouse_username,
    )
    assert len(rows) == EXPECTED_METRIC_COUNT
    assert {str(row["metric_name"]) for row in rows} >= {
        "mysql_queries_total",
        "mysql_server_available",
        "mysql_threads_connected",
    }


def _build_instance(*, instance_id: str) -> MySQLInstance:
    return MySQLInstance(
        connection=MySQLConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=utc_now(),
        environment="prod",
        instance_id=instance_id,
        labels=("primary", "live-gate"),
        name=instance_id,
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=utc_now(),
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _wait_for_redis(redis_url: str) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    last_error: Exception | None = None
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    while time.monotonic() < deadline:
        try:
            client.ping()
            return
        except redis.RedisError as error:
            last_error = error
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("Redis did not become ready for the live gate.") from last_error


def _wait_for_clickhouse(
    *,
    database: str,
    endpoint: str,
    password: str,
    username: str,
) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
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
        except Exception as error:  # pragma: no cover - gate retry path
            last_error = error
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("ClickHouse did not become ready for the live gate.") from last_error


def _wait_for_metric_rows(
    *,
    database: str,
    endpoint: str,
    instance_id: str,
    password: str,
    username: str,
) -> list[dict[str, object]]:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    last_rows: list[dict[str, object]] = []
    while time.monotonic() < deadline:
        last_rows = _run_clickhouse_query(
            database=database,
            endpoint=endpoint,
            password=password,
            query=(
                "SELECT metric_name, metric_value "
                f"FROM {CLICKHOUSE_METRICS_TABLE} "
                f"WHERE instance_id = '{instance_id}' "
                "ORDER BY metric_name FORMAT JSONEachRow"
            ),
            username=username,
        )
        if len(last_rows) == EXPECTED_METRIC_COUNT:
            return last_rows
        time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError(
        f"Expected {EXPECTED_METRIC_COUNT} metric rows in ClickHouse, got {len(last_rows)}."
    )


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
        headers={"X-ClickHouse-User": username, "X-ClickHouse-Key": password},
        method="POST",
    )
    with urlopen(request) as response:
        body = response.read().decode("utf-8")
    return [json.loads(line) for line in body.splitlines() if line]
