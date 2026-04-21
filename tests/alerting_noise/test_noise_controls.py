from db_monitor_api.alerting.domain import AlertEventType, RuleOperator, RuleSeverity
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertNoiseControlPolicy, AlertingService
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_sample, sample_anchor


def test_noise_controls_do_not_emit_suppressed_event_inside_window() -> None:
    anchor = sample_anchor()
    service = _build_service(suppression_window_seconds=300)
    _create_rule(service=service, instance_id="inst-noise-window")

    service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-noise-window",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=6,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-noise-window",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=9.0,
                minutes_ago=4,
            ),
        )
    )

    alert = service.list_alerts()[0]
    detail = service.get_alert(alert_id=alert.alert_id)

    assert [event.event_type for event in detail.history] == [
        AlertEventType.OPENED,
        AlertEventType.NOTIFIED,
    ]


def test_noise_controls_emit_windowed_suppressed_evidence_for_same_group() -> None:
    anchor = sample_anchor()
    service = _build_service(suppression_window_seconds=300)
    _create_rule(service=service, instance_id="inst-noise-suppressed")

    service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-noise-suppressed",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=8.0,
                minutes_ago=12,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-noise-suppressed",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=9.0,
                minutes_ago=6,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-noise-suppressed",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=10.0,
                minutes_ago=5,
            ),
        )
    )

    alert = service.list_alerts()[0]
    detail = service.get_alert(alert_id=alert.alert_id)

    assert [event.event_type for event in detail.history] == [
        AlertEventType.OPENED,
        AlertEventType.NOTIFIED,
        AlertEventType.SUPPRESSED,
    ]
    assert detail.history[-1].detail == (
        f"Suppressed repeated MySQL trigger for group {alert.rule_id}:{alert.instance_id} "
        "at value 9.0."
    )


def test_noise_controls_emit_windowed_suppressed_evidence_for_oracle_group() -> None:
    anchor = sample_anchor()
    service = _build_service(suppression_window_seconds=300)
    _create_rule(
        service=service,
        engine=DatabaseEngine.ORACLE,
        instance_id="inst-noise-oracle",
        metric_name="oracle_sessions_active",
        name="Oracle Sessions Active High",
        threshold=6.0,
    )

    service.evaluate_samples(
        samples=(
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-noise-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=8.0,
                minutes_ago=12,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-noise-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=9.0,
                minutes_ago=6,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-noise-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=10.0,
                minutes_ago=5,
            ),
        )
    )

    alert = service.list_alerts()[0]
    detail = service.get_alert(alert_id=alert.alert_id)

    assert alert.engine is DatabaseEngine.ORACLE
    assert [event.event_type for event in detail.history] == [
        AlertEventType.OPENED,
        AlertEventType.NOTIFIED,
        AlertEventType.SUPPRESSED,
    ]
    assert detail.history[-1].detail == (
        f"Suppressed repeated Oracle trigger for group {alert.rule_id}:{alert.instance_id} "
        "at value 9.0."
    )


def _build_service(*, suppression_window_seconds: int) -> AlertingService:
    return AlertingService(
        audit_service=AuditService(InMemoryAuditRepository()),
        notifier=InMemoryNotifier(),
        noise_control_policy=AlertNoiseControlPolicy(
            suppression_window_seconds=suppression_window_seconds
        ),
        repository=InMemoryAlertingRepository(),
    )


def _create_rule(
    *,
    service: AlertingService,
    engine: DatabaseEngine = DatabaseEngine.MYSQL,
    instance_id: str,
    metric_name: str = "mysql_replication_lag_seconds",
    name: str = "Replication Lag High",
    threshold: float = 5.0,
) -> None:
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=engine,
        instance_ids=(instance_id,),
        metric_name=metric_name,
        name=name,
        operator=RuleOperator.GREATER_THAN,
        severity=RuleSeverity.CRITICAL,
        threshold=threshold,
    )
