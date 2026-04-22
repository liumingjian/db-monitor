from collections.abc import Generator
from datetime import UTC, datetime
import os
from pathlib import Path
import subprocess
import time
from typing import cast

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from db_monitor_api.analytics.repository import InMemoryAnalyticsRepository
from db_monitor_api.runtime_views.repository import InMemoryProcesslistRepository
from db_monitor_api.runtime_views.slow_query_repository import InMemorySlowQueryRepository
from db_monitor_api.runtime_views.tablespace_repository import InMemoryTablespaceRepository
from db_monitor_api.alerting.domain import (
    AlertEventType,
    AlertHistoryEvent,
    AlertRecord,
    AlertRule,
    AlertStatus,
    RuleOperator,
    RuleSeverity,
)
from db_monitor_api.alerting.postgres_repository import PostgresAlertingRepository
from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_postgres_runtime
from db_monitor_api.auth.domain import AuditEntry
from db_monitor_api.auth.postgres_repository import PostgresAuditRepository
from db_monitor_api.control_plane.domain import DatabaseEngine, SystemSetting
from db_monitor_api.control_plane.postgres_repository import PostgresControlPlaneRepository
from db_monitor_api.runtime import AppRuntime
from db_monitor_pipeline.domain import MetricKind
from db_monitor_schema.postgres import bootstrap_postgres_schema

from tests.analytics_support import build_instance, build_sample
from tests.support import StaticMySQLConnectionValidator, StaticOracleConnectionValidator

POSTGRES_GATE_DSN_ENV = "DB_MONITOR_POSTGRES_TEST_DSN"
LOCAL_POSTGRES_GATE_DSN = "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor"
POSTGRES_WAIT_SECONDS = 30
RETRY_INTERVAL_SECONDS = 1
REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def postgres_dsn() -> str:
    dsn = os.environ.get(POSTGRES_GATE_DSN_ENV, LOCAL_POSTGRES_GATE_DSN)
    _start_local_postgres()
    _wait_for_postgres(dsn)
    _reset_control_plane_tables(dsn)
    bootstrap_postgres_schema(postgres_dsn=dsn)
    return dsn


@pytest.fixture
def postgres_app(postgres_dsn: str) -> FastAPI:
    return create_app(
        runtime=build_postgres_runtime(
            analytics_repository=InMemoryAnalyticsRepository(),
            postgres_dsn=postgres_dsn,
            mysql_validator=StaticMySQLConnectionValidator(),
            oracle_validator=StaticOracleConnectionValidator(),
            processlist_repository=InMemoryProcesslistRepository(),
            slow_query_repository=InMemorySlowQueryRepository(),
            tablespace_repository=InMemoryTablespaceRepository(),
        )
    )


@pytest.fixture
def postgres_client(postgres_app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(postgres_app) as test_client:
        yield test_client


@pytest.fixture
def postgres_runtime(postgres_app: FastAPI) -> AppRuntime:
    return cast(AppRuntime, postgres_app.state.runtime)


def test_postgres_repository_persists_multi_engine_instances_and_settings(
    postgres_dsn: str,
    postgres_client: TestClient,
    postgres_runtime: AppRuntime,
) -> None:
    _login_admin(postgres_client)
    create_response = postgres_client.post(
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
            "labels": ["primary", "postgres-gate"],
            "name": "prod-primary",
        },
    )
    assert create_response.status_code == 201
    oracle_response = postgres_client.post(
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
            "labels": ["oracle", "postgres-gate"],
            "name": "prod-oracle-primary",
        },
    )
    assert oracle_response.status_code == 201
    setting_response = postgres_client.put(
        "/control/settings/notification.channel",
        json={"value": "email"},
    )
    assert setting_response.status_code == 200

    _seed_organization(
        postgres_dsn,
        organization_id="org-external",
        name="External Operations",
        slug="external-ops",
    )
    external_anchor = datetime(2026, 4, 20, 12, 0, tzinfo=UTC)
    repository = PostgresControlPlaneRepository(postgres_dsn=postgres_dsn)
    repository.create_instance(
        build_instance(
            created_at=external_anchor,
            instance_id="inst-external",
            name="external-primary",
            organization_id="org-external",
        )
    )
    repository.upsert_setting(
        SystemSetting(
            key="notification.channel",
            organization_id="org-external",
            updated_at=external_anchor,
            value="slack",
        )
    )
    rule_response = postgres_client.post(
        "/alerts/rules",
        json={
            "enabled": True,
            "engine": "mysql",
            "instance_ids": [create_response.json()["instance_id"]],
            "metric_name": "mysql_replication_lag_seconds",
            "name": "Internal Replication Lag",
            "operator": RuleOperator.GREATER_THAN.value,
            "severity": RuleSeverity.CRITICAL.value,
            "threshold": 5.0,
        },
    )
    assert rule_response.status_code == 201
    postgres_runtime.alerting_service.evaluate_samples(
        samples=(
            build_sample(
                anchor=external_anchor,
                instance_id=create_response.json()["instance_id"],
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=0,
            ),
        )
    )
    alerting_repository = PostgresAlertingRepository(postgres_dsn=postgres_dsn)
    alerting_repository.create_rule(
        AlertRule(
            created_at=external_anchor,
            enabled=True,
            engine=DatabaseEngine.MYSQL,
            instance_ids=("inst-external",),
            metric_name="mysql_replication_lag_seconds",
            name="External Replication Lag",
            organization_id="org-external",
            operator=RuleOperator.GREATER_THAN,
            rule_id="rule-external",
            severity=RuleSeverity.CRITICAL,
            threshold=5.0,
        )
    )
    alerting_repository.upsert_alert(
        AlertRecord(
            alert_id="alert-external",
            acknowledged_at=None,
            acknowledged_by_user_id=None,
            current_value=9.0,
            engine=DatabaseEngine.MYSQL,
            instance_id="inst-external",
            last_evaluated_at=external_anchor,
            metric_name="mysql_replication_lag_seconds",
            opened_at=external_anchor,
            owner_assigned_at=None,
            owner_user_id=None,
            organization_id="org-external",
            resolved_at=None,
            rule_id="rule-external",
            rule_name="External Replication Lag",
            severity=RuleSeverity.CRITICAL,
            status=AlertStatus.OPEN,
            threshold=5.0,
        )
    )
    alerting_repository.append_history(
        AlertHistoryEvent(
            alert_id="alert-external",
            detail="External alert opened.",
            event_type=AlertEventType.OPENED,
            organization_id="org-external",
            occurred_at=external_anchor,
        )
    )

    detail_response = postgres_client.get(
        f"/control/instances/{create_response.json()['instance_id']}"
    )
    assert detail_response.status_code == 200
    assert detail_response.json() == create_response.json()
    oracle_detail_response = postgres_client.get(
        f"/control/instances/{oracle_response.json()['instance_id']}"
    )
    assert oracle_detail_response.status_code == 200
    assert oracle_detail_response.json() == oracle_response.json()
    list_response = postgres_client.get("/control/instances")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert [item["engine"] for item in list_response.json()] == ["mysql", "oracle"]
    external_detail_response = postgres_client.get("/control/instances/inst-external")
    assert external_detail_response.status_code == 404
    settings_response = postgres_client.get("/control/settings")
    assert settings_response.status_code == 200
    assert settings_response.json() == [setting_response.json()]
    rule_list_response = postgres_client.get("/alerts/rules")
    assert rule_list_response.status_code == 200
    assert [rule["rule_id"] for rule in rule_list_response.json()] == [
        rule_response.json()["rule_id"]
    ]
    alerts_response = postgres_client.get("/alerts")
    assert alerts_response.status_code == 200
    assert len(alerts_response.json()) == 1
    assert alerts_response.json()[0]["rule_id"] == rule_response.json()["rule_id"]
    external_alert_response = postgres_client.get("/alerts/alert-external")
    assert external_alert_response.status_code == 404
    reloaded_runtime = build_postgres_runtime(
        analytics_repository=InMemoryAnalyticsRepository(),
        postgres_dsn=postgres_dsn,
        mysql_validator=StaticMySQLConnectionValidator(),
        oracle_validator=StaticOracleConnectionValidator(),
        processlist_repository=InMemoryProcesslistRepository(),
        slow_query_repository=InMemorySlowQueryRepository(),
        tablespace_repository=InMemoryTablespaceRepository(),
    )
    assert reloaded_runtime.audit_repository.entries[-1].action == "rules.create"

    audit_repository = PostgresAuditRepository(postgres_dsn=postgres_dsn)
    audit_repository.append(
        AuditEntry(
            action="external.audit",
            actor_user_id="user-external",
            occurred_at=external_anchor,
            organization_id="org-external",
            outcome="allowed",
            resource="external",
        )
    )
    audit_response = postgres_client.get("/auth/audit-entries?limit=2")
    assert audit_response.status_code == 200
    assert len(audit_response.json()) == 2
    assert audit_response.json()[0]["action"] == "rules.create"
    assert {entry["organization_id"] for entry in audit_response.json()} == {"org-internal"}
    assert {entry["action"] for entry in audit_response.json()} == {
        "rules.create",
        "settings.write",
    }


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


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
    raise RuntimeError("PostgreSQL did not become ready for the live gate.") from last_error


def _start_local_postgres() -> None:
    try:
        subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "up", "-d", "postgres"],
            check=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError("docker is required to provision the local PostgreSQL gate.") from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(error.stderr.strip() or "Failed to start local PostgreSQL.") from error


def _reset_control_plane_tables(dsn: str) -> None:
    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS schema_version")
            cursor.execute("DROP TABLE IF EXISTS audit_entries")
            cursor.execute("DROP TABLE IF EXISTS alert_history")
            cursor.execute("DROP TABLE IF EXISTS alert_records")
            cursor.execute("DROP TABLE IF EXISTS rule_instance_overrides")
            cursor.execute("DROP TABLE IF EXISTS alert_rules")
            cursor.execute("DROP TABLE IF EXISTS instance_parameters")
            cursor.execute("DROP TABLE IF EXISTS control_mysql_instances")
            cursor.execute("DROP TABLE IF EXISTS control_settings")
            cursor.execute("DROP TABLE IF EXISTS organization_memberships")
            cursor.execute("DROP TABLE IF EXISTS organizations")


def _seed_organization(
    dsn: str,
    *,
    organization_id: str,
    name: str,
    slug: str,
) -> None:
    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO organizations (organization_id, name, slug, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (organization_id) DO NOTHING
                """,
                (organization_id, name, slug, datetime.now(tz=UTC)),
            )
