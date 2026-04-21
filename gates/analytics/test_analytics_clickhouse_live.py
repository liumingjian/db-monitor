from datetime import datetime, timedelta
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from db_monitor_api.analytics.repository import ClickHouseAnalyticsRepository
from db_monitor_api.app import create_app
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.settings import ClickHouseSettings
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    MySQLConnectionConfig,
    MySQLInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.mysql_validation import MySQLConnectionValidator
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.domain import MetricKind, MetricSample
from db_monitor_pipeline.sink import ClickHouseMetricSink
from db_monitor_schema.clickhouse import bootstrap_clickhouse_schema

CLICKHOUSE_DATABASE_ENV = "DB_MONITOR_CLICKHOUSE_DATABASE"
CLICKHOUSE_ENDPOINT_ENV = "DB_MONITOR_CLICKHOUSE_ENDPOINT"
CLICKHOUSE_PASSWORD_ENV = "DB_MONITOR_CLICKHOUSE_PASSWORD"
CLICKHOUSE_USERNAME_ENV = "DB_MONITOR_CLICKHOUSE_USERNAME"
READY_TIMEOUT_SECONDS = 30
RETRY_INTERVAL_SECONDS = 1


class StaticMySQLConnectionValidator(MySQLConnectionValidator):
    def validate(self, config: MySQLConnectionConfig) -> ConnectionValidation:
        del config
        return ConnectionValidation(
            checked_at=utc_now(),
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        )


def test_live_analytics_routes_query_clickhouse() -> None:
    clickhouse_database = _required_env(CLICKHOUSE_DATABASE_ENV)
    clickhouse_endpoint = _required_env(CLICKHOUSE_ENDPOINT_ENV)
    clickhouse_password = _required_env(CLICKHOUSE_PASSWORD_ENV)
    clickhouse_username = _required_env(CLICKHOUSE_USERNAME_ENV)
    instance_id = f"inst-{uuid.uuid4().hex}"
    anchor = utc_now()

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
    _seed_clickhouse(
        anchor=anchor,
        clickhouse_database=clickhouse_database,
        clickhouse_endpoint=clickhouse_endpoint,
        clickhouse_password=clickhouse_password,
        clickhouse_username=clickhouse_username,
        instance_id=instance_id,
    )

    app = _build_app(
        clickhouse_database=clickhouse_database,
        clickhouse_endpoint=clickhouse_endpoint,
        clickhouse_password=clickhouse_password,
        clickhouse_username=clickhouse_username,
        instance_id=instance_id,
        anchor=anchor,
    )

    with TestClient(app) as client:
        _login_admin(client)
        overview_response = client.get("/analytics/overview", params={"window": "1h"})
        detail_response = client.get(
            f"/analytics/mysql-instances/{instance_id}/trends",
            params={"window": "1h"},
        )

    assert overview_response.status_code == 200
    assert detail_response.status_code == 200
    overview = overview_response.json()
    detail = detail_response.json()
    assert overview["instances"][0]["instance_id"] == instance_id
    assert any(
        card["metric_name"] == "mysql_bytes_sent_per_second" and card["value"] > 0
        for card in overview["cards"]
    )
    assert any(
        card["metric_name"] == "mysql_innodb_buffer_pool_reads_per_second" and card["value"] > 0
        for card in overview["cards"]
    )
    assert detail["instance"]["status"] == "healthy"
    assert any(
        card["metric_name"] == "mysql_queries_per_second" and card["value"] > 0
        for card in detail["cards"]
    )
    assert any(
        card["metric_name"] == "mysql_bytes_sent_per_second" and card["value"] > 0
        for card in detail["cards"]
    )
    assert any(
        card["metric_name"] == "mysql_innodb_buffer_pool_reads_per_second" and card["value"] > 0
        for card in detail["cards"]
    )


def _build_app(
    *,
    anchor: datetime,
    clickhouse_database: str,
    clickhouse_endpoint: str,
    clickhouse_password: str,
    clickhouse_username: str,
    instance_id: str,
) -> FastAPI:
    control_plane_repository = InMemoryControlPlaneRepository()
    control_plane_repository.create_instance(_build_instance(anchor=anchor, instance_id=instance_id))
    return create_app(
        runtime=build_local_runtime(
            analytics_repository=ClickHouseAnalyticsRepository(
                database=clickhouse_database,
                endpoint=clickhouse_endpoint,
                password=clickhouse_password,
                username=clickhouse_username,
            ),
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
        )
    )


def _seed_clickhouse(
    *,
    anchor: datetime,
    clickhouse_database: str,
    clickhouse_endpoint: str,
    clickhouse_password: str,
    clickhouse_username: str,
    instance_id: str,
) -> None:
    ClickHouseMetricSink(
        database=clickhouse_database,
        endpoint=clickhouse_endpoint,
        password=clickhouse_password,
        username=clickhouse_username,
    ).write(
        (
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_server_available", metric_value=1.0, minutes_ago=10),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_server_available", metric_value=1.0, minutes_ago=5),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_connected", metric_value=10.0, minutes_ago=10),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_connected", metric_value=12.0, minutes_ago=5),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_running", metric_value=2.0, minutes_ago=10),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_running", metric_value=4.0, minutes_ago=5),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_queries_total", metric_value=100.0, minutes_ago=10),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_queries_total", metric_value=220.0, minutes_ago=5),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=300.0, minutes_ago=10),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=600.0, minutes_ago=5),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=500.0, minutes_ago=10),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=1100.0, minutes_ago=5),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=40.0, minutes_ago=10),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=100.0, minutes_ago=5),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_replication_lag_seconds", metric_value=2.0, minutes_ago=5),
            _build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_uptime_seconds", metric_value=1300.0, minutes_ago=5),
        )
    )


def _build_instance(*, anchor: datetime, instance_id: str) -> MySQLInstance:
    return MySQLInstance(
        connection=MySQLConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=anchor,
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        name=instance_id,
        validation=ConnectionValidation(
            checked_at=anchor,
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )


def _build_sample(
    *,
    anchor: datetime,
    instance_id: str,
    metric_kind: MetricKind,
    metric_name: str,
    metric_value: float,
    minutes_ago: int,
) -> MetricSample:
    return MetricSample(
        collected_at=anchor - timedelta(minutes=minutes_ago),
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        metric_kind=metric_kind,
        metric_name=metric_name,
        metric_value=metric_value,
    )


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


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
            rows = _run_query(
                database=database,
                endpoint=endpoint,
                password=password,
                query="SELECT 1 AS ready FORMAT JSONEachRow",
                username=username,
            )
            if rows == ['{"ready":1}']:
                return
        except Exception as error:  # pragma: no cover - gate retry path
            last_error = error
        time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("ClickHouse did not become ready for the analytics live gate.") from last_error


def _run_query(
    *,
    database: str,
    endpoint: str,
    password: str,
    query: str,
    username: str,
) -> list[str]:
    request = Request(
        url=f"{endpoint.rstrip('/')}/?{urlencode({'database': database, 'query': query})}",
        data=b"",
        headers={"X-ClickHouse-User": username, "X-ClickHouse-Key": password},
        method="POST",
    )
    with urlopen(request) as response:
        return [line for line in response.read().decode("utf-8").splitlines() if line]
