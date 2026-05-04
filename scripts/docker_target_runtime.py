from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import psycopg
import pymysql

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
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    MySQLConnectionConfig,
    MySQLInstance,
    SystemSetting,
    ValidationStatus,
)
from db_monitor_api.control_plane.postgres_repository import PostgresControlPlaneRepository
from db_monitor_api.settings import ClickHouseSettings, load_api_settings
from db_monitor_pipeline.domain import MetricKind, MetricSample
from db_monitor_pipeline.sink import ClickHouseMetricSink
from db_monitor_schema.runtime import bootstrap_api_runtime_schema, verify_api_runtime_schema

ORGANIZATION_ID = "org-internal"
PRIMARY_INSTANCE_ID = "inst-prod-primary"
READY_TIMEOUT_SECONDS = 90
RETRY_INTERVAL_SECONDS = 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("bootstrap", "seed"))
    args = parser.parse_args()
    if args.command == "bootstrap":
        bootstrap_runtime()
    else:
        seed_runtime()
    return 0


def bootstrap_runtime() -> None:
    settings = load_runtime_settings()
    wait_for_postgres(settings["postgres_dsn"])
    wait_for_clickhouse(settings["clickhouse"])
    versions = bootstrap_api_runtime_schema(settings["api"])
    print(json.dumps({"command": "bootstrap", "schemas": [version.__dict__ for version in versions]}))


def seed_runtime() -> None:
    settings = load_runtime_settings()
    mysql_connection = load_mysql_connection()
    wait_for_postgres(settings["postgres_dsn"])
    wait_for_clickhouse(settings["clickhouse"])
    wait_for_mysql(mysql_connection)
    verify_api_runtime_schema(
        analytics_repository=None,
        clickhouse=settings["clickhouse"],
        postgres_dsn=settings["postgres_dsn"],
    )
    reset_postgres_state(settings["postgres_dsn"])
    reset_clickhouse_state(settings["clickhouse"])
    mysql_version = read_mysql_version(mysql_connection)
    seed_postgres_state(settings["postgres_dsn"], mysql_connection, mysql_version)
    seed_clickhouse_state(settings["clickhouse"])
    print(
        json.dumps(
            {
                "command": "seed",
                "instance_id": PRIMARY_INSTANCE_ID,
                "mysql_version": mysql_version,
                "oracle_baseline": "delegated-to-root-signoff",
            }
        )
    )


def load_runtime_settings() -> dict[str, object]:
    api_settings = load_api_settings()
    if api_settings.postgres_dsn is None or api_settings.clickhouse is None:
        raise RuntimeError("Docker target runtime requires persistent Postgres + ClickHouse settings.")
    return {
        "api": api_settings,
        "clickhouse": api_settings.clickhouse,
        "postgres_dsn": api_settings.postgres_dsn,
    }


def load_mysql_connection() -> MySQLConnectionConfig:
    return MySQLConnectionConfig(
        database=required("DB_MONITOR_TARGET_MYSQL_DATABASE"),
        host=required("DB_MONITOR_TARGET_MYSQL_HOST"),
        password=required("DB_MONITOR_TARGET_MYSQL_PASSWORD"),
        port=int(required("DB_MONITOR_TARGET_MYSQL_PORT")),
        username=required("DB_MONITOR_TARGET_MYSQL_USERNAME"),
    )


def required(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def wait_for_postgres(postgres_dsn: str) -> None:
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
    raise RuntimeError("PostgreSQL did not become ready for docker target bootstrap.") from last_error


def wait_for_clickhouse(settings: ClickHouseSettings) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            rows = run_clickhouse_query(
                database=settings.database,
                endpoint=settings.endpoint,
                password=settings.password,
                query="SELECT 1 AS ready FORMAT JSONEachRow",
                username=settings.username,
            )
            if rows == [{"ready": 1}]:
                return
        except Exception as error:  # pragma: no cover - retry path
            last_error = error
        time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("ClickHouse did not become ready for docker target bootstrap.") from last_error


def wait_for_mysql(connection: MySQLConnectionConfig) -> None:
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with pymysql.connect(
                database=connection.database,
                host=connection.host,
                password=connection.password,
                port=connection.port,
                user=connection.username,
            ) as mysql_connection:
                with mysql_connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            return
        except pymysql.MySQLError as error:
            last_error = error
            time.sleep(RETRY_INTERVAL_SECONDS)
    raise RuntimeError("MySQL did not become ready for docker target bootstrap.") from last_error


def reset_postgres_state(postgres_dsn: str) -> None:
    table_names = (
        "alert_history",
        "alert_records",
        "alert_rules",
        "audit_entries",
        "control_settings",
        "control_mysql_instances",
        "organization_memberships",
    )
    with psycopg.connect(postgres_dsn) as connection:
        with connection.cursor() as cursor:
            for table_name in table_names:
                cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")


def reset_clickhouse_state(settings: ClickHouseSettings) -> None:
    run_clickhouse_query(
        database=settings.database,
        endpoint=settings.endpoint,
        password=settings.password,
        query="TRUNCATE TABLE IF EXISTS metric_samples",
        username=settings.username,
    )


def read_mysql_version(connection: MySQLConnectionConfig) -> str:
    with pymysql.connect(
        database=connection.database,
        host=connection.host,
        password=connection.password,
        port=connection.port,
        user=connection.username,
    ) as mysql_connection:
        with mysql_connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            row = cursor.fetchone()
    return str(row[0]) if row is not None else "unknown"


def seed_postgres_state(
    postgres_dsn: str,
    mysql_connection: MySQLConnectionConfig,
    mysql_version: str,
) -> None:
    anchor = utc_now()
    control_plane_repository = PostgresControlPlaneRepository(postgres_dsn=postgres_dsn)
    alerting_repository = PostgresAlertingRepository(postgres_dsn=postgres_dsn)
    control_plane_repository.upsert_instance(
        MySQLInstance(
            connection=mysql_connection,
            created_at=anchor - timedelta(minutes=15),
            environment="prod",
            instance_id=PRIMARY_INSTANCE_ID,
            labels=("primary", "critical"),
            name="prod-primary",
            organization_id=ORGANIZATION_ID,
            validation=ConnectionValidation(
                checked_at=anchor - timedelta(minutes=1),
                detail="Docker target seed validated the MySQL probe path.",
                server_version=mysql_version,
                status=ValidationStatus.PASSED,
            ),
        )
    )
    control_plane_repository.upsert_setting(
        SystemSetting(
            key="notification.channel",
            organization_id=ORGANIZATION_ID,
            updated_at=anchor,
            value="email",
        )
    )
    alerting_repository.create_rule(
        AlertRule(
            created_at=anchor - timedelta(minutes=6),
            enabled=True,
            engine=DatabaseEngine.MYSQL,
            instance_ids=(PRIMARY_INSTANCE_ID,),
            metric_name="mysql_replication_lag_seconds",
            name="Replication Lag High",
            organization_id=ORGANIZATION_ID,
            operator=RuleOperator.GREATER_THAN,
            rule_id="rule-lag",
            severity=RuleSeverity.CRITICAL,
            threshold=5,
        )
    )
    alerting_repository.upsert_alert(
        AlertRecord(
            alert_id="alert-lag",
            acknowledged_at=None,
            acknowledged_by_user_id=None,
            current_value=8.0,
            engine=DatabaseEngine.MYSQL,
            instance_id=PRIMARY_INSTANCE_ID,
            last_evaluated_at=anchor,
            metric_name="mysql_replication_lag_seconds",
            opened_at=anchor - timedelta(minutes=5),
            owner_assigned_at=None,
            owner_user_id=None,
            organization_id=ORGANIZATION_ID,
            resolved_at=None,
            rule_id="rule-lag",
            rule_name="Replication Lag High",
            severity=RuleSeverity.CRITICAL,
            status=AlertStatus.OPEN,
            threshold=5.0,
        )
    )
    for event in build_history(anchor):
        alerting_repository.append_history(event)


def build_history(anchor: datetime) -> tuple[AlertHistoryEvent, ...]:
    return (
        AlertHistoryEvent(
            alert_id="alert-lag",
            detail=(
                "MySQL rule 'Replication Lag High' triggered on prod-primary: "
                "mysql_replication_lag_seconds=8.0 threshold=5.0."
            ),
            event_type=AlertEventType.OPENED,
            organization_id=ORGANIZATION_ID,
            occurred_at=anchor - timedelta(minutes=5),
        ),
        AlertHistoryEvent(
            alert_id="alert-lag",
            detail="Notifier sent critical MySQL alert.",
            event_type=AlertEventType.NOTIFIED,
            organization_id=ORGANIZATION_ID,
            occurred_at=anchor - timedelta(minutes=5),
        ),
    )


def seed_clickhouse_state(settings: ClickHouseSettings) -> None:
    ClickHouseMetricSink(
        database=settings.database,
        endpoint=settings.endpoint,
        password=settings.password,
        username=settings.username,
    ).write(build_metric_samples())


def build_metric_samples() -> tuple[MetricSample, ...]:
    anchor = datetime.now(tz=UTC)
    samples: list[MetricSample] = []
    snapshots = (
        (15, {"mysql_server_available": (MetricKind.GAUGE, 1), "mysql_threads_connected": (MetricKind.GAUGE, 16), "mysql_threads_running": (MetricKind.GAUGE, 3), "mysql_queries_total": (MetricKind.COUNTER, 120), "mysql_bytes_received_total": (MetricKind.COUNTER, 1000), "mysql_bytes_sent_total": (MetricKind.COUNTER, 1800), "mysql_innodb_buffer_pool_reads_total": (MetricKind.COUNTER, 40), "mysql_replication_lag_seconds": (MetricKind.GAUGE, 3), "mysql_uptime_seconds": (MetricKind.GAUGE, 1200)}),
        (10, {"mysql_server_available": (MetricKind.GAUGE, 1), "mysql_threads_connected": (MetricKind.GAUGE, 18), "mysql_threads_running": (MetricKind.GAUGE, 4), "mysql_queries_total": (MetricKind.COUNTER, 180), "mysql_bytes_received_total": (MetricKind.COUNTER, 1400), "mysql_bytes_sent_total": (MetricKind.COUNTER, 2400), "mysql_innodb_buffer_pool_reads_total": (MetricKind.COUNTER, 70), "mysql_replication_lag_seconds": (MetricKind.GAUGE, 4), "mysql_uptime_seconds": (MetricKind.GAUGE, 1500)}),
        (5, {"mysql_server_available": (MetricKind.GAUGE, 1), "mysql_threads_connected": (MetricKind.GAUGE, 20), "mysql_threads_running": (MetricKind.GAUGE, 4), "mysql_queries_total": (MetricKind.COUNTER, 240), "mysql_bytes_received_total": (MetricKind.COUNTER, 1950), "mysql_bytes_sent_total": (MetricKind.COUNTER, 3200), "mysql_innodb_buffer_pool_reads_total": (MetricKind.COUNTER, 115), "mysql_replication_lag_seconds": (MetricKind.GAUGE, 5), "mysql_uptime_seconds": (MetricKind.GAUGE, 1800)}),
    )
    for minutes_ago, values in snapshots:
        for metric_name, (metric_kind, metric_value) in values.items():
            samples.append(
                MetricSample(
                    collected_at=anchor - timedelta(minutes=minutes_ago),
                    engine=DatabaseEngine.MYSQL,
                    environment="prod",
                    instance_id=PRIMARY_INSTANCE_ID,
                    labels=("primary", "critical"),
                    metric_kind=metric_kind,
                    metric_name=metric_name,
                    metric_value=metric_value,
                )
            )
    return tuple(samples)


def run_clickhouse_query(
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


if __name__ == "__main__":
    raise SystemExit(main())
