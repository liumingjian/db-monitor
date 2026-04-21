from datetime import timedelta

from fastapi.testclient import TestClient

from db_monitor_api.alerting.domain import (
    AlertEventType,
    AlertHistoryEvent,
    AlertRecord,
    AlertRule,
    AlertStatus,
    RuleOperator,
    RuleSeverity,
)
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.domain import MetricKind
from tests.alerting_support import build_app
from tests.analytics_support import build_instance, build_sample, sample_anchor
from tests.support import StaticMySQLConnectionValidator


def test_alerting_contract_exposes_workflow_fields_and_routes() -> None:
    anchor = sample_anchor()
    app = build_app(instance_ids=("inst-alert-api",))
    runtime = app.state.runtime

    with TestClient(app) as client:
        _login_admin(client)
        rule_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-alert-api"],
                "metric_name": "mysql_replication_lag_seconds",
                "name": "Replication Lag High",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.CRITICAL.value,
                "threshold": 5.0,
            },
        )
        assert rule_response.status_code == 201

        runtime.alerting_service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    instance_id="inst-alert-api",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=8.0,
                    minutes_ago=1,
                ),
            )
        )
        alert_id = client.get("/alerts").json()[0]["alert_id"]

        acknowledge_response = client.post(f"/alerts/{alert_id}/acknowledge")
        owner_response = client.put(
            f"/alerts/{alert_id}/owner",
            json={"owner_user_id": "user-ops"},
        )
        note_response = client.post(
            f"/alerts/{alert_id}/notes",
            json={"note": "Investigating replication lag."},
        )

    assert acknowledge_response.status_code == 200
    assert owner_response.status_code == 200
    assert note_response.status_code == 200
    assert rule_response.json()["engine"] == DatabaseEngine.MYSQL.value
    assert acknowledge_response.json()["record"]["status"] == "acknowledged"
    assert acknowledge_response.json()["record"]["engine"] == DatabaseEngine.MYSQL.value
    assert acknowledge_response.json()["record"]["acknowledged_by_user_id"] == "user-admin"
    assert owner_response.json()["record"]["owner_user_id"] == "user-ops"
    assert note_response.json()["history"][-1]["event_type"] == AlertEventType.NOTE_ADDED.value


def test_alerting_contract_rejects_acknowledging_resolved_alert() -> None:
    anchor = sample_anchor()
    app = build_app(instance_ids=("inst-alert-api-resolved",))
    runtime = app.state.runtime

    with TestClient(app) as client:
        _login_admin(client)
        client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-alert-api-resolved"],
                "metric_name": "mysql_replication_lag_seconds",
                "name": "Replication Lag High",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.CRITICAL.value,
                "threshold": 5.0,
            },
        )
        runtime.alerting_service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    instance_id="inst-alert-api-resolved",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=8.0,
                    minutes_ago=1,
                ),
                build_sample(
                    anchor=anchor,
                    instance_id="inst-alert-api-resolved",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=1.0,
                    minutes_ago=0,
                ),
            )
        )
        alert_id = client.get("/alerts").json()[0]["alert_id"]
        acknowledge_response = client.post(f"/alerts/{alert_id}/acknowledge")

    assert acknowledge_response.status_code == 400
    assert acknowledge_response.json() == {
        "detail": "Resolved alerts cannot be acknowledged."
    }


def test_alerting_contract_exposes_engine_scoped_rule_catalog() -> None:
    app = build_app(instance_ids=("inst-alert-api",))

    with TestClient(app) as client:
        _login_admin(client)
        response = client.get("/alerts/rule-catalog")

    assert response.status_code == 200
    assert response.json() == [
        {
            "engine": "mysql",
            "metrics": [
                {
                    "label": "Server Availability",
                    "metric_name": "mysql_server_available",
                    "unit": "status",
                },
                {
                    "label": "Threads Connected",
                    "metric_name": "mysql_threads_connected",
                    "unit": "connections",
                },
                {
                    "label": "Threads Running",
                    "metric_name": "mysql_threads_running",
                    "unit": "threads",
                },
                {
                    "label": "Uptime",
                    "metric_name": "mysql_uptime_seconds",
                    "unit": "seconds",
                },
                {
                    "label": "Replication Lag",
                    "metric_name": "mysql_replication_lag_seconds",
                    "unit": "seconds",
                },
            ],
        },
        {
            "engine": "oracle",
            "metrics": [
                {
                    "label": "Server Availability",
                    "metric_name": "oracle_server_available",
                    "unit": "status",
                },
                {
                    "label": "Sessions Total",
                    "metric_name": "oracle_sessions_total",
                    "unit": "sessions",
                },
                {
                    "label": "Sessions Active",
                    "metric_name": "oracle_sessions_active",
                    "unit": "sessions",
                },
                {
                    "label": "Session Waits",
                    "metric_name": "oracle_session_waits",
                    "unit": "sessions",
                },
                {
                    "label": "Uptime",
                    "metric_name": "oracle_uptime_seconds",
                    "unit": "seconds",
                },
            ],
        },
    ]


def test_alerting_contract_supports_oracle_rule_and_alert_payloads() -> None:
    anchor = sample_anchor()
    control_plane_repository = InMemoryControlPlaneRepository()
    control_plane_repository.create_instance(
        build_instance(
            created_at=anchor,
            engine=DatabaseEngine.ORACLE,
            instance_id="inst-alert-oracle",
            name="oracle-alert-instance",
        )
    )
    app = create_app(
        runtime=build_local_runtime(
            alerting_repository=InMemoryAlertingRepository(),
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
        )
    )
    runtime = app.state.runtime

    with TestClient(app) as client:
        _login_admin(client)
        rule_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.ORACLE.value,
                "instance_ids": ["inst-alert-oracle"],
                "metric_name": "oracle_sessions_active",
                "name": "Oracle Sessions Active High",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.WARNING.value,
                "threshold": 6.0,
            },
        )
        assert rule_response.status_code == 201

        runtime.alerting_service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    engine=DatabaseEngine.ORACLE,
                    instance_id="inst-alert-oracle",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="oracle_sessions_active",
                    metric_value=8.0,
                    minutes_ago=1,
                ),
            )
        )

        alerts_response = client.get("/alerts")
        detail_response = client.get(f"/alerts/{alerts_response.json()[0]['alert_id']}")

    assert rule_response.json()["engine"] == DatabaseEngine.ORACLE.value
    assert alerts_response.status_code == 200
    assert alerts_response.json()[0]["engine"] == DatabaseEngine.ORACLE.value
    assert detail_response.status_code == 200
    assert detail_response.json()["record"]["engine"] == DatabaseEngine.ORACLE.value
    assert detail_response.json()["record"]["metric_name"] == "oracle_sessions_active"


def test_alerting_contract_scopes_rules_and_alerts_to_active_organization() -> None:
    anchor = sample_anchor()
    alerting_repository = InMemoryAlertingRepository()
    control_plane_repository = InMemoryControlPlaneRepository()
    control_plane_repository.create_instance(
        build_instance(
            created_at=anchor,
            instance_id="inst-alert-internal",
            name="internal-alert-instance",
            organization_id="org-internal",
        )
    )
    control_plane_repository.create_instance(
        build_instance(
            created_at=anchor + timedelta(seconds=1),
            instance_id="inst-alert-external",
            name="external-alert-instance",
            organization_id="org-external",
        )
    )
    alerting_repository.create_rule(
        AlertRule(
            created_at=anchor,
            enabled=True,
            engine=DatabaseEngine.MYSQL,
            instance_ids=("inst-alert-internal",),
            metric_name="mysql_replication_lag_seconds",
            name="Internal Replication Lag",
            organization_id="org-internal",
            operator=RuleOperator.GREATER_THAN,
            rule_id="rule-internal",
            severity=RuleSeverity.CRITICAL,
            threshold=5.0,
        )
    )
    alerting_repository.create_rule(
        AlertRule(
            created_at=anchor + timedelta(seconds=1),
            enabled=True,
            engine=DatabaseEngine.MYSQL,
            instance_ids=("inst-alert-external",),
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
            alert_id="alert-internal",
            acknowledged_at=None,
            acknowledged_by_user_id=None,
            current_value=8.0,
            engine=DatabaseEngine.MYSQL,
            instance_id="inst-alert-internal",
            last_evaluated_at=anchor,
            metric_name="mysql_replication_lag_seconds",
            opened_at=anchor,
            owner_assigned_at=None,
            owner_user_id=None,
            organization_id="org-internal",
            resolved_at=None,
            rule_id="rule-internal",
            rule_name="Internal Replication Lag",
            severity=RuleSeverity.CRITICAL,
            status=AlertStatus.OPEN,
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
            instance_id="inst-alert-external",
            last_evaluated_at=anchor + timedelta(seconds=1),
            metric_name="mysql_replication_lag_seconds",
            opened_at=anchor + timedelta(seconds=1),
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
            alert_id="alert-internal",
            detail="Internal alert opened.",
            event_type=AlertEventType.OPENED,
            organization_id="org-internal",
            occurred_at=anchor,
        )
    )
    alerting_repository.append_history(
        AlertHistoryEvent(
            alert_id="alert-external",
            detail="External alert opened.",
            event_type=AlertEventType.OPENED,
            organization_id="org-external",
            occurred_at=anchor + timedelta(seconds=1),
        )
    )
    app = create_app(
        runtime=build_local_runtime(
            alerting_repository=alerting_repository,
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
        )
    )

    with TestClient(app) as client:
        _login_admin(client)
        rules_response = client.get("/alerts/rules")
        alerts_response = client.get("/alerts")
        external_detail_response = client.get("/alerts/alert-external")

    assert rules_response.status_code == 200
    assert [rule["rule_id"] for rule in rules_response.json()] == ["rule-internal"]
    assert alerts_response.status_code == 200
    assert [alert["alert_id"] for alert in alerts_response.json()] == ["alert-internal"]
    assert external_detail_response.status_code == 404
    assert external_detail_response.json() == {"detail": "Unknown alert: alert-external"}


def test_alerting_contract_rejects_rule_for_external_org_instance() -> None:
    anchor = sample_anchor()
    control_plane_repository = InMemoryControlPlaneRepository()
    control_plane_repository.create_instance(
        build_instance(
            created_at=anchor,
            instance_id="inst-alert-internal",
            name="internal-alert-instance",
            organization_id="org-internal",
        )
    )
    control_plane_repository.create_instance(
        build_instance(
            created_at=anchor + timedelta(seconds=1),
            instance_id="inst-alert-external",
            name="external-alert-instance",
            organization_id="org-external",
        )
    )
    app = create_app(
        runtime=build_local_runtime(
            alerting_repository=InMemoryAlertingRepository(),
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
        )
    )

    with TestClient(app) as client:
        _login_admin(client)
        response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-alert-external"],
                "metric_name": "mysql_replication_lag_seconds",
                "name": "Cross Org Rule",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.CRITICAL.value,
                "threshold": 5.0,
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unknown instance in organization scope: inst-alert-external"
    }


def test_alerting_contract_rejects_rule_for_instance_engine_mismatch() -> None:
    anchor = sample_anchor()
    control_plane_repository = InMemoryControlPlaneRepository()
    control_plane_repository.create_instance(
        build_instance(
            created_at=anchor,
            engine=DatabaseEngine.ORACLE,
            instance_id="inst-alert-oracle-mismatch",
            name="oracle-alert-instance",
        )
    )
    app = create_app(
        runtime=build_local_runtime(
            alerting_repository=InMemoryAlertingRepository(),
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
        )
    )

    with TestClient(app) as client:
        _login_admin(client)
        response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-alert-oracle-mismatch"],
                "metric_name": "mysql_replication_lag_seconds",
                "name": "Cross Engine Rule",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.CRITICAL.value,
                "threshold": 5.0,
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Rule scope instance engine mismatch: inst-alert-oracle-mismatch is oracle, expected mysql"
    }


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200
