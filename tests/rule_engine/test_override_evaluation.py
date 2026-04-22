from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from db_monitor_api.alerting.domain import (
    AlertStatus,
    RuleInstanceOverride,
    RuleOperator,
    RuleSeverity,
)
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertingService
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_sample, sample_anchor


def _build_service(
    repository: InMemoryAlertingRepository | None = None,
    notifier: InMemoryNotifier | None = None,
) -> AlertingService:
    return AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=notifier or InMemoryNotifier(),
        repository=repository or InMemoryAlertingRepository(),
    )


def test_override_threshold_supersedes_rule_threshold() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    service = _build_service(repository=repository)
    rule = service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-low", "inst-high"),
        metric_name="mysql_threads_running",
        name="Threads Running High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=5.0,
    )
    repository.upsert_override(
        RuleInstanceOverride(
            enabled=None,
            instance_id="inst-high",
            rule_id=rule.rule_id,
            threshold=20.0,
            updated_at=utc_now(),
        )
    )

    summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-low",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=6.0,
                minutes_ago=1,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-high",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=6.0,
                minutes_ago=1,
            ),
        )
    )
    alerts = service.list_alerts()

    assert summary.opened_alerts == 1
    assert [alert.instance_id for alert in alerts] == ["inst-low"]
    # Opened alert should record the effective threshold on that instance.
    assert alerts[0].threshold == 5.0


def test_override_disabled_skips_instance_evaluation() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    service = _build_service(repository=repository)
    rule = service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-on", "inst-off"),
        metric_name="mysql_threads_running",
        name="Threads Running High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=5.0,
    )
    repository.upsert_override(
        RuleInstanceOverride(
            enabled=False,
            instance_id="inst-off",
            rule_id=rule.rule_id,
            threshold=None,
            updated_at=utc_now(),
        )
    )

    summary = service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-on",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=6.0,
                minutes_ago=1,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-off",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=99.0,
                minutes_ago=1,
            ),
        )
    )

    assert summary.opened_alerts == 1
    alerts = service.list_alerts()
    assert [alert.instance_id for alert in alerts] == ["inst-on"]


def test_override_effective_threshold_recorded_on_opened_alert() -> None:
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    service = _build_service(repository=repository)
    rule = service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-high",),
        metric_name="mysql_threads_running",
        name="Threads Running High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=5.0,
    )
    repository.upsert_override(
        RuleInstanceOverride(
            enabled=None,
            instance_id="inst-high",
            rule_id=rule.rule_id,
            threshold=50.0,
            updated_at=utc_now(),
        )
    )

    service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-high",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=60.0,
                minutes_ago=1,
            ),
        )
    )

    alerts = service.list_alerts()
    assert len(alerts) == 1
    assert alerts[0].threshold == 50.0
    assert alerts[0].status is AlertStatus.OPEN


def test_evaluation_does_not_call_list_rules_twice_or_new_repo_methods() -> None:
    """D5 hard boundary: _evaluate_sample() must not introduce any new DB calls.

    The only repo methods invoked during evaluation should be list_rules (once),
    find_active_alert (once per matching sample), upsert_alert, and append_history.
    No per-sample call to list_rules, get_rule, or any override-loading method.
    """
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    service = _build_service(repository=repository)
    rule = service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-a", "inst-b"),
        metric_name="mysql_threads_running",
        name="Threads Running High",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=5.0,
    )
    repository.upsert_override(
        RuleInstanceOverride(
            enabled=None,
            instance_id="inst-a",
            rule_id=rule.rule_id,
            threshold=30.0,
            updated_at=utc_now(),
        )
    )

    samples = tuple(
        build_sample(
            anchor=anchor,
            instance_id=instance_id,
            metric_kind=MetricKind.GAUGE,
            metric_name="mysql_threads_running",
            metric_value=6.0,
            minutes_ago=1,
        )
        for instance_id in ("inst-a", "inst-b")
    )

    with patch.object(
        repository, "list_rules", wraps=repository.list_rules
    ) as list_rules_spy, patch.object(
        repository, "find_active_alert", wraps=repository.find_active_alert
    ) as find_active_alert_spy, patch.object(
        repository, "get_rule", wraps=repository.get_rule
    ) as get_rule_spy:
        service.evaluate_samples(samples=samples)

    assert list_rules_spy.call_count == 1, (
        "evaluate_samples() must call list_rules exactly once per invocation"
    )
    # inst-a threshold 30 > 6, inst-b threshold 5 < 6 → only inst-b matches.
    # But find_active_alert runs for EVERY matching sample regardless of threshold match,
    # since _evaluate_sample calls it before checking the operator. This preserves the
    # pre-existing N+1 count; we just need to confirm it hasn't doubled.
    assert find_active_alert_spy.call_count == 2, (
        "find_active_alert must be called exactly once per matching sample (N+1 preserved)"
    )
    assert get_rule_spy.call_count == 0, (
        "_evaluate_sample must not perform per-sample rule reload"
    )


def test_list_rules_returns_one_row_per_rule_with_json_aggregated_overrides() -> None:
    """D5 hard boundary: list_rules() must return |rules| rows, not |rules|x|overrides|."""
    repository = InMemoryAlertingRepository()
    service = _build_service(repository=repository)
    rule = service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-1", "inst-2", "inst-3"),
        metric_name="mysql_threads_running",
        name="Threads Running",
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.WARNING,
        threshold=5.0,
    )
    for instance_id in ("inst-1", "inst-2", "inst-3"):
        repository.upsert_override(
            RuleInstanceOverride(
                enabled=None,
                instance_id=instance_id,
                rule_id=rule.rule_id,
                threshold=10.0,
                updated_at=utc_now(),
            )
        )

    rules = repository.list_rules()
    assert len(rules) == 1
    assert len(rules[0].overrides) == 3


def test_evaluation_completes_large_rule_sample_matrix_correctly() -> None:
    """Case 1 scaffold: 10 rules x ~2 overrides x 5 samples, confirm summary correctness."""
    anchor = sample_anchor()
    repository = InMemoryAlertingRepository()
    service = _build_service(repository=repository)

    # Build 10 rules each scoped to two instances: inst-active and inst-suppressed.
    rule_count = 10
    rules = []
    for rule_index in range(rule_count):
        rule = service.create_rule(
            actor_user_id="user-admin",
            enabled=True,
            engine=DatabaseEngine.MYSQL,
            instance_ids=(f"inst-active-{rule_index}", f"inst-suppressed-{rule_index}"),
            metric_name="mysql_threads_running",
            name=f"Threads Running {rule_index}",
            operator=RuleOperator.GREATER_THAN,
            severity=RuleSeverity.WARNING,
            threshold=5.0,
        )
        rules.append(rule)
        repository.upsert_override(
            RuleInstanceOverride(
                enabled=False,
                instance_id=f"inst-suppressed-{rule_index}",
                rule_id=rule.rule_id,
                threshold=None,
                updated_at=utc_now(),
            )
        )
        repository.upsert_override(
            RuleInstanceOverride(
                enabled=None,
                instance_id=f"inst-active-{rule_index}",
                rule_id=rule.rule_id,
                threshold=100.0,
                updated_at=utc_now(),
            )
        )

    samples = []
    for rule_index in range(rule_count):
        for instance_prefix in ("inst-active", "inst-suppressed"):
            samples.append(
                build_sample(
                    anchor=anchor,
                    instance_id=f"{instance_prefix}-{rule_index}",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_threads_running",
                    metric_value=6.0,
                    minutes_ago=1,
                )
            )

    summary = service.evaluate_samples(samples=tuple(samples))
    # No alerts should open because inst-active has override threshold 100 and
    # inst-suppressed has enabled=False.
    assert summary.opened_alerts == 0
    assert summary.notified_alerts == 0
    assert summary.resolved_alerts == 0
