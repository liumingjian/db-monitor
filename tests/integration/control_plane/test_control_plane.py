from dataclasses import replace
from datetime import timedelta

from fastapi.testclient import TestClient

from db_monitor_api.app import create_app
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.control_plane.domain import ConnectionValidation, SystemSetting, ValidationStatus
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_api.runtime import AppRuntime

from tests.analytics_support import build_instance
from tests.support import StaticMySQLConnectionValidator, StaticOracleConnectionValidator


def test_settings_api_returns_stable_control_plane_state_and_audits(
    client: TestClient,
    runtime: AppRuntime,
) -> None:
    client.post("/auth/login", json={"password": "admin-password", "username": "admin"})

    write_response = client.put(
        "/control/settings/notification.channel",
        json={"value": "email"},
    )

    assert write_response.status_code == 200
    assert write_response.json()["key"] == "notification.channel"

    list_response = client.get("/control/settings")

    assert list_response.status_code == 200
    assert list_response.json() == [write_response.json()]
    assert runtime.audit_repository.entries[-1].action == "settings.write"


def test_instance_detail_and_revalidation_update_control_plane_state(
    client: TestClient,
    mysql_validator: StaticMySQLConnectionValidator,
) -> None:
    client.post("/auth/login", json={"password": "admin-password", "username": "admin"})
    create_response = client.post(
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
            "labels": ["primary"],
            "name": "prod-primary",
        },
    )
    instance_id = create_response.json()["instance_id"]
    mysql_validator.next_result = ConnectionValidation(
        checked_at=utc_now(),
        detail="Replication lag prevented validation.",
        server_version="8.4.0",
        status=ValidationStatus.FAILED,
    )

    validate_response = client.post(f"/control/instances/{instance_id}/validate")

    assert validate_response.status_code == 200
    assert validate_response.json()["engine"] == "mysql"
    assert validate_response.json()["validation"]["status"] == "failed"
    assert validate_response.json()["validation"]["detail"] == "Replication lag prevented validation."

    detail_response = client.get(f"/control/instances/{instance_id}")

    assert detail_response.status_code == 200
    assert detail_response.json() == validate_response.json()


def test_oracle_instance_detail_and_revalidation_use_oracle_validator(
    client: TestClient,
    oracle_validator: StaticOracleConnectionValidator,
) -> None:
    client.post("/auth/login", json={"password": "admin-password", "username": "admin"})
    create_response = client.post(
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
            "labels": ["oracle"],
            "name": "prod-oracle-primary",
        },
    )
    instance_id = create_response.json()["instance_id"]
    oracle_validator.next_result = ConnectionValidation(
        checked_at=utc_now(),
        detail="Listener rejected the supplied Oracle DSN.",
        server_version=None,
        status=ValidationStatus.FAILED,
    )

    validate_response = client.post(f"/control/instances/{instance_id}/validate")

    assert validate_response.status_code == 200
    assert validate_response.json()["engine"] == "oracle"
    assert validate_response.json()["validation"]["status"] == "failed"
    assert (
        validate_response.json()["validation"]["detail"]
        == "Listener rejected the supplied Oracle DSN."
    )

    detail_response = client.get(f"/control/instances/{instance_id}")

    assert detail_response.status_code == 200
    assert detail_response.json() == validate_response.json()


def test_in_memory_repository_supports_organization_scoped_reads() -> None:
    anchor = utc_now()
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(
        build_instance(
            created_at=anchor,
            instance_id="inst-internal",
            name="internal-primary",
            organization_id="org-internal",
        )
    )
    repository.create_instance(
        build_instance(
            created_at=anchor + timedelta(seconds=1),
            instance_id="inst-external",
            name="external-primary",
            organization_id="org-external",
        )
    )
    repository.upsert_setting(
        SystemSetting(
            key="notification.channel",
            organization_id="org-internal",
            updated_at=anchor,
            value="email",
        )
    )
    repository.upsert_setting(
        SystemSetting(
            key="notification.channel",
            organization_id="org-external",
            updated_at=anchor,
            value="slack",
        )
    )

    internal_instances = repository.list_instances(organization_id="org-internal")
    internal_settings = repository.list_settings(organization_id="org-internal")

    assert [instance.instance_id for instance in internal_instances] == ["inst-internal"]
    assert repository.get_instance("inst-external", organization_id="org-internal") is None
    assert [setting.value for setting in internal_settings] == ["email"]
    assert len(repository.list_instances(organization_id=None)) == 2


def test_control_plane_routes_scope_instances_and_settings_to_active_organization() -> None:
    anchor = utc_now()
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(
        build_instance(
            created_at=anchor,
            instance_id="inst-internal",
            name="internal-primary",
            organization_id="org-internal",
        )
    )
    repository.create_instance(
        build_instance(
            created_at=anchor + timedelta(seconds=1),
            instance_id="inst-external",
            name="external-primary",
            organization_id="org-external",
        )
    )
    repository.upsert_setting(
        SystemSetting(
            key="notification.channel",
            organization_id="org-internal",
            updated_at=anchor,
            value="email",
        )
    )
    repository.upsert_setting(
        SystemSetting(
            key="notification.channel",
            organization_id="org-external",
            updated_at=anchor,
            value="slack",
        )
    )

    app = create_app(
        runtime=build_local_runtime(
            control_plane_repository=repository,
            mysql_validator=StaticMySQLConnectionValidator(),
            oracle_validator=StaticOracleConnectionValidator(),
        )
    )

    with TestClient(app) as client:
        login_response = client.post(
            "/auth/login",
            json={"password": "admin-password", "username": "admin"},
        )

        assert login_response.status_code == 200

        list_response = client.get("/control/instances")
        settings_response = client.get("/control/settings")
        external_detail_response = client.get("/control/instances/inst-external")

        assert list_response.status_code == 200
        assert [item["instance_id"] for item in list_response.json()] == ["inst-internal"]
        assert settings_response.status_code == 200
        assert settings_response.json() == [
            {
                "key": "notification.channel",
                "updated_at": anchor.isoformat(),
                "value": "email",
            }
        ]
        assert external_detail_response.status_code == 404
        assert external_detail_response.json() == {"detail": "Unknown instance: inst-external"}


def test_control_plane_routes_filter_instances_by_prd_closeout_fields() -> None:
    anchor = utc_now()
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(
        build_instance(
            created_at=anchor,
            instance_id="inst-prod-primary",
            name="prod-primary",
            status=ValidationStatus.PASSED,
        )
    )
    repository.create_instance(
        replace(
            build_instance(
                created_at=anchor + timedelta(seconds=1),
                instance_id="inst-stage-replica",
                name="stage-replica",
                status=ValidationStatus.FAILED,
            ),
            environment="stage",
        )
    )
    repository.create_instance(
        build_instance(
            created_at=anchor + timedelta(seconds=2),
            instance_id="inst-prod-analytics",
            name="prod-analytics",
            status=ValidationStatus.PASSED,
        )
    )
    app = create_app(
        runtime=build_local_runtime(
            control_plane_repository=repository,
            mysql_validator=StaticMySQLConnectionValidator(),
            oracle_validator=StaticOracleConnectionValidator(),
        )
    )

    with TestClient(app) as client:
        login_response = client.post(
            "/auth/login",
            json={"password": "admin-password", "username": "admin"},
        )

        assert login_response.status_code == 200

        prod_response = client.get("/control/instances", params={"environment": "prod"})
        failed_response = client.get("/control/instances", params={"status": "failed"})
        named_response = client.get("/control/instances", params={"name": "analytics"})
        label_response = client.get("/control/instances", params={"label": "primary"})

    assert prod_response.status_code == 200
    assert [item["instance_id"] for item in prod_response.json()] == [
        "inst-prod-primary",
        "inst-prod-analytics",
    ]
    assert failed_response.status_code == 200
    assert [item["instance_id"] for item in failed_response.json()] == ["inst-stage-replica"]
    assert named_response.status_code == 200
    assert [item["instance_id"] for item in named_response.json()] == ["inst-prod-analytics"]
    assert label_response.status_code == 200
    assert [item["instance_id"] for item in label_response.json()] == [
        "inst-prod-primary",
        "inst-stage-replica",
        "inst-prod-analytics",
    ]
