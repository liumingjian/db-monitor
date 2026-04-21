from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient

from db_monitor_api.analytics.repository import InMemoryAnalyticsRepository
from db_monitor_api.app import create_app
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    MySQLConnectionConfig,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.domain import MetricKind, MetricSample
from tests.support import StaticMySQLConnectionValidator


def build_app(
    *,
    instances: tuple[MonitoredInstance, ...],
    samples: tuple[MetricSample, ...],
) -> FastAPI:
    control_plane_repository = InMemoryControlPlaneRepository()
    for instance in instances:
        control_plane_repository.create_instance(instance)
    return create_app(
        runtime=build_local_runtime(
            analytics_repository=InMemoryAnalyticsRepository(samples=samples),
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
        )
    )


def build_instance(
    *,
    created_at: datetime,
    engine: DatabaseEngine = DatabaseEngine.MYSQL,
    instance_id: str,
    name: str,
    organization_id: str = "org-internal",
    status: ValidationStatus = ValidationStatus.PASSED,
) -> MonitoredInstance:
    return MonitoredInstance(
        connection=MySQLConnectionConfig(
            database="XE" if engine is DatabaseEngine.ORACLE else "mysql",
            host="127.0.0.1",
            password="secret",
            port=15211 if engine is DatabaseEngine.ORACLE else 3306,
            username="system" if engine is DatabaseEngine.ORACLE else "db_monitor",
        ),
        created_at=created_at,
        engine=engine,
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        name=name,
        organization_id=organization_id,
        validation=ConnectionValidation(
            checked_at=created_at,
            detail="ok" if status is ValidationStatus.PASSED else "failed",
            server_version="11.2.0" if engine is DatabaseEngine.ORACLE else "8.4.0",
            status=status,
        ),
    )


def build_sample(
    *,
    anchor: datetime,
    engine: DatabaseEngine = DatabaseEngine.MYSQL,
    instance_id: str,
    metric_kind: MetricKind,
    metric_name: str,
    metric_value: float,
    minutes_ago: int,
) -> MetricSample:
    return MetricSample(
        collected_at=anchor - timedelta(minutes=minutes_ago),
        engine=engine,
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        metric_kind=metric_kind,
        metric_name=metric_name,
        metric_value=metric_value,
    )


def login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def sample_anchor() -> datetime:
    return utc_now()
