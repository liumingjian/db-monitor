from fastapi.testclient import TestClient

from db_monitor_api.alerting.domain import (
    RuleInstanceOverride,
    RuleOperator,
    RuleSeverity,
)
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import (
    AlertingService,
    OverrideDraft,
    RuleNotFoundError,
)
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.control_plane.domain import DatabaseEngine
from tests.alerting_support import build_app


def _build_service(
    *, repository: InMemoryAlertingRepository | None = None
) -> AlertingService:
    return AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=InMemoryNotifier(),
        repository=repository or InMemoryAlertingRepository(),
    )


def test_repo_upsert_and_delete_override_roundtrip() -> None:
    repository = InMemoryAlertingRepository()
    service = _build_service(repository=repository)
    rule = service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-override-a", "inst-override-b"),
        metric_name="mysql_threads_running",
        name="Threads Running",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=10.0,
    )

    repository.upsert_override(
        RuleInstanceOverride(
            enabled=False,
            instance_id="inst-override-a",
            rule_id=rule.rule_id,
            threshold=99.0,
            updated_at=utc_now(),
        )
    )
    repository.upsert_override(
        RuleInstanceOverride(
            enabled=None,
            instance_id="inst-override-b",
            rule_id=rule.rule_id,
            threshold=50.0,
            updated_at=utc_now(),
        )
    )

    fetched = repository.get_rule(rule.rule_id)
    assert fetched is not None
    by_instance = {override.instance_id: override for override in fetched.overrides}
    assert by_instance["inst-override-a"].enabled is False
    assert by_instance["inst-override-a"].threshold == 99.0
    assert by_instance["inst-override-b"].enabled is None
    assert by_instance["inst-override-b"].threshold == 50.0

    # list_rules must return exactly one rule row with embedded overrides.
    rules = repository.list_rules()
    assert len(rules) == 1
    assert {override.instance_id for override in rules[0].overrides} == {
        "inst-override-a",
        "inst-override-b",
    }

    # Delete returns True on first call and False on repeat.
    assert repository.delete_override(
        instance_id="inst-override-a", rule_id=rule.rule_id
    ) is True
    assert repository.delete_override(
        instance_id="inst-override-a", rule_id=rule.rule_id
    ) is False
    remaining = repository.get_rule(rule.rule_id)
    assert remaining is not None
    assert [override.instance_id for override in remaining.overrides] == [
        "inst-override-b"
    ]


def test_repo_service_replace_overrides_writes_audit_entries() -> None:
    audit_repository = InMemoryAuditRepository()
    service = AlertingService(
        audit_service=AuditService(audit_repository),
        notifier=InMemoryNotifier(),
        repository=InMemoryAlertingRepository(),
    )
    rule = service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-a", "inst-b"),
        metric_name="mysql_threads_running",
        name="Threads Running",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=10.0,
    )

    service.replace_rule_overrides(
        actor_user_id="user-admin",
        organization_id=rule.organization_id,
        overrides=(
            OverrideDraft(instance_id="inst-a", threshold=20.0, enabled=None),
            OverrideDraft(instance_id="inst-b", threshold=None, enabled=False),
        ),
        rule_id=rule.rule_id,
    )

    # Replace with a subset → drop "inst-b" should audit a delete.
    service.replace_rule_overrides(
        actor_user_id="user-admin",
        organization_id=rule.organization_id,
        overrides=(
            OverrideDraft(instance_id="inst-a", threshold=30.0, enabled=None),
        ),
        rule_id=rule.rule_id,
    )

    actions = [entry.action for entry in audit_repository.entries]
    assert actions.count("rules.override.upsert") == 3
    assert actions.count("rules.override.delete") == 1

    refreshed = service.get_rule(
        rule_id=rule.rule_id, organization_id=rule.organization_id
    )
    assert [override.instance_id for override in refreshed.overrides] == ["inst-a"]
    assert refreshed.overrides[0].threshold == 30.0


def test_repo_service_get_rule_raises_when_unknown() -> None:
    service = _build_service()
    try:
        service.get_rule(rule_id="rule-missing", organization_id="org-internal")
    except RuleNotFoundError:
        return
    raise AssertionError("Expected RuleNotFoundError for unknown rule.")


def test_api_create_rule_accepts_overrides_and_get_rule_returns_them() -> None:
    app = build_app(instance_ids=("inst-ovr-a", "inst-ovr-b"))

    with TestClient(app) as client:
        login = client.post(
            "/auth/login",
            json={"password": "admin-password", "username": "admin"},
        )
        assert login.status_code == 200

        create_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-ovr-a", "inst-ovr-b"],
                "metric_name": "mysql_threads_running",
                "name": "Threads Running High",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.WARNING.value,
                "threshold": 4.0,
                "overrides": [
                    {"instance_id": "inst-ovr-a", "threshold": 9.0},
                    {"instance_id": "inst-ovr-b", "enabled": False},
                ],
            },
        )
        assert create_response.status_code == 201, create_response.text
        body = create_response.json()
        by_instance = {item["instance_id"]: item for item in body["overrides"]}
        assert by_instance["inst-ovr-a"]["threshold"] == 9.0
        assert by_instance["inst-ovr-a"]["enabled"] is None
        assert by_instance["inst-ovr-b"]["threshold"] is None
        assert by_instance["inst-ovr-b"]["enabled"] is False

        rule_id = body["rule_id"]
        detail_response = client.get(f"/alerts/rules/{rule_id}")
        assert detail_response.status_code == 200
        detail_body = detail_response.json()
        assert {
            item["instance_id"] for item in detail_body["overrides"]
        } == {"inst-ovr-a", "inst-ovr-b"}

        update_response = client.put(
            f"/alerts/rules/{rule_id}",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-ovr-a", "inst-ovr-b"],
                "metric_name": "mysql_threads_running",
                "name": "Threads Running High",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.WARNING.value,
                "threshold": 4.0,
                "overrides": [
                    {"instance_id": "inst-ovr-a", "threshold": 12.0, "enabled": True},
                ],
            },
        )
        assert update_response.status_code == 200, update_response.text
        updated_body = update_response.json()
        assert len(updated_body["overrides"]) == 1
        assert updated_body["overrides"][0]["instance_id"] == "inst-ovr-a"
        assert updated_body["overrides"][0]["threshold"] == 12.0
        assert updated_body["overrides"][0]["enabled"] is True


def test_api_rejects_override_referring_to_unknown_instance() -> None:
    app = build_app(instance_ids=("inst-valid",))

    with TestClient(app) as client:
        login = client.post(
            "/auth/login",
            json={"password": "admin-password", "username": "admin"},
        )
        assert login.status_code == 200

        response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": DatabaseEngine.MYSQL.value,
                "instance_ids": ["inst-valid"],
                "metric_name": "mysql_threads_running",
                "name": "Threads Running",
                "operator": RuleOperator.GREATER_THAN.value,
                "severity": RuleSeverity.WARNING.value,
                "threshold": 4.0,
                "overrides": [
                    {"instance_id": "inst-missing", "threshold": 9.0},
                ],
            },
        )
        assert response.status_code == 400
