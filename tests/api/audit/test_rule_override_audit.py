from fastapi.testclient import TestClient

from db_monitor_api.alerting.domain import RuleOperator, RuleSeverity
from db_monitor_api.control_plane.domain import DatabaseEngine
from tests.alerting_support import build_app


def _login_admin(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"password": "admin-password", "username": "admin"},
    )
    assert response.status_code == 200


def test_rule_override_audit_records_upsert_and_delete_actions() -> None:
    app = build_app(instance_ids=("inst-aud-a", "inst-aud-b"))
    runtime = app.state.runtime

    with TestClient(app) as client:
        _login_admin(client)
        create_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-aud-a", "inst-aud-b"],
                "metric_name": "mysql_threads_running",
                "name": "Threads Running",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.WARNING.value,
                "threshold": 5.0,
                "overrides": [
                    {"instance_id": "inst-aud-a", "threshold": 10.0},
                    {"instance_id": "inst-aud-b", "enabled": False},
                ],
            },
        )
        assert create_response.status_code == 201
        rule_id = create_response.json()["rule_id"]

        # Replace overrides with a subset to trigger a delete on inst-aud-b.
        update_response = client.put(
            f"/alerts/rules/{rule_id}",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-aud-a", "inst-aud-b"],
                "metric_name": "mysql_threads_running",
                "name": "Threads Running",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.WARNING.value,
                "threshold": 5.0,
                "overrides": [
                    {"instance_id": "inst-aud-a", "threshold": 20.0},
                ],
            },
        )
        assert update_response.status_code == 200

    audit_entries = runtime.audit_service.list_entries(
        limit=100, organization_id="org-internal"
    )
    actions = [entry.action for entry in audit_entries]

    assert actions.count("rules.override.upsert") == 3
    assert actions.count("rules.override.delete") == 1

    delete_entry = next(
        entry for entry in audit_entries if entry.action == "rules.override.delete"
    )
    assert rule_id in delete_entry.resource
    assert "inst-aud-b" in delete_entry.resource
    assert delete_entry.actor_user_id == "user-admin"
    assert delete_entry.outcome == "allowed"


def test_rule_override_audit_records_rule_update_action() -> None:
    app = build_app(instance_ids=("inst-upd",))
    runtime = app.state.runtime

    with TestClient(app) as client:
        _login_admin(client)
        create_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-upd"],
                "metric_name": "mysql_threads_running",
                "name": "Original",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.WARNING.value,
                "threshold": 5.0,
            },
        )
        assert create_response.status_code == 201
        rule_id = create_response.json()["rule_id"]

        update_response = client.put(
            f"/alerts/rules/{rule_id}",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-upd"],
                "metric_name": "mysql_threads_running",
                "name": "Renamed",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.WARNING.value,
                "threshold": 7.0,
                "overrides": [],
            },
        )
        assert update_response.status_code == 200

    actions = [
        entry.action
        for entry in runtime.audit_service.list_entries(
            limit=100, organization_id="org-internal"
        )
    ]
    assert "rules.update" in actions
