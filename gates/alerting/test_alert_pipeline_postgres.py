from datetime import UTC, datetime, timedelta
import os
import time
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
import psycopg

from db_monitor_api.analytics.repository import InMemoryAnalyticsRepository
from db_monitor_api.alerting.domain import RuleSeverity
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_postgres_runtime
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    MySQLConnectionConfig,
    ValidationStatus,
)
from db_monitor_api.control_plane.mysql_validation import MySQLConnectionValidator
from db_monitor_api.runtime import AppRuntime
from db_monitor_pipeline.domain import MetricKind, MetricSample
from db_monitor_schema.postgres import bootstrap_postgres_schema

POSTGRES_GATE_DSN_ENV = "DB_MONITOR_POSTGRES_TEST_DSN"
POSTGRES_WAIT_SECONDS = 30
RETRY_INTERVAL_SECONDS = 1


class StaticMySQLConnectionValidator(MySQLConnectionValidator):
    def validate(self, config: MySQLConnectionConfig) -> ConnectionValidation:
        del config
        return ConnectionValidation(
            checked_at=datetime.now(tz=UTC),
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        )


def test_postgres_alert_pipeline_persists_rules_alerts_and_history() -> None:
    postgres_dsn = _required_env(POSTGRES_GATE_DSN_ENV)
    notifier = InMemoryNotifier()

    _wait_for_postgres(postgres_dsn)
    _reset_alert_tables(postgres_dsn)
    bootstrap_postgres_schema(postgres_dsn=postgres_dsn)
    app = _build_app(postgres_dsn=postgres_dsn, notifier=notifier)
    runtime = cast(AppRuntime, app.state.runtime)

    with TestClient(app) as client:
        _login_admin(client)
        instance_response = client.post(
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
                "labels": ["primary"],
                "name": "prod-primary",
            },
        )
        assert instance_response.status_code == 201
        instance_id = instance_response.json()["instance_id"]
        rule_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "instance_ids": [instance_id],
                "metric_name": "mysql_replication_lag_seconds",
                "name": "Replication Lag High",
                "operator": "gt",
                "severity": "critical",
                "threshold": 5.0,
            },
        )
        assert rule_response.status_code == 201

        runtime.alerting_service.evaluate_samples(
            samples=(
                _build_sample(instance_id=instance_id, metric_value=8.0, minutes_ago=7),
                _build_sample(instance_id=instance_id, metric_value=9.0, minutes_ago=1),
                _build_sample(instance_id=instance_id, metric_value=2.0, minutes_ago=0),
            )
        )
        alerts_response = client.get("/alerts")
        detail_response = client.get(f"/alerts/{alerts_response.json()[0]['alert_id']}")

    assert alerts_response.status_code == 200
    assert detail_response.status_code == 200
    assert alerts_response.json()[0]["status"] == "resolved"
    assert alerts_response.json()[0]["acknowledged_by_user_id"] is None
    assert alerts_response.json()[0]["owner_user_id"] is None
    assert any(event["event_type"] == "suppressed" for event in detail_response.json()["history"])
    assert detail_response.json()["history"][-1]["event_type"] == "resolved"
    assert detail_response.json()["record"]["severity"] == RuleSeverity.CRITICAL.value
    assert len(notifier.requests) == 1


def _build_app(*, notifier: InMemoryNotifier, postgres_dsn: str) -> FastAPI:
    return create_app(
        runtime=build_postgres_runtime(
            analytics_repository=InMemoryAnalyticsRepository(),
            postgres_dsn=postgres_dsn,
            mysql_validator=StaticMySQLConnectionValidator(),
            notifier=notifier,
        )
    )


def _build_sample(*, instance_id: str, metric_value: float, minutes_ago: int) -> MetricSample:
    return MetricSample(
        collected_at=datetime.now(tz=UTC) - timedelta(minutes=minutes_ago),
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        metric_kind=MetricKind.GAUGE,
        metric_name="mysql_replication_lag_seconds",
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
    raise RuntimeError("PostgreSQL did not become ready for the alert pipeline live gate.") from last_error


def _reset_alert_tables(dsn: str) -> None:
    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS schema_version")
            cursor.execute("DROP TABLE IF EXISTS alert_history")
            cursor.execute("DROP TABLE IF EXISTS alert_records")
            cursor.execute("DROP TABLE IF EXISTS alert_rules")
            cursor.execute("DROP TABLE IF EXISTS control_mysql_instances")
            cursor.execute("DROP TABLE IF EXISTS control_settings")
