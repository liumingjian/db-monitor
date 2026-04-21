from typing import cast

from fastapi.testclient import TestClient

from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_api.runtime import AppRuntime
from db_monitor_pipeline.domain import MetricKind
from tests.alerting_support import build_app
from tests.analytics_support import build_instance, build_sample, login_admin, sample_anchor


def test_alert_pipeline_lifecycle_routes_expose_rules_and_alert_details() -> None:
    anchor = sample_anchor()
    notifier = InMemoryNotifier()
    app = build_app(instance_ids=("inst-alert-route",), notifier=notifier)
    runtime = cast(AppRuntime, app.state.runtime)

    with TestClient(app) as client:
        login_admin(client)
        create_rule_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": "mysql",
                "instance_ids": ["inst-alert-route"],
                "metric_name": "mysql_replication_lag_seconds",
                "name": "Replication Lag High",
                "operator": "gt",
                "severity": "critical",
                "threshold": 5.0,
            },
        )
        assert create_rule_response.status_code == 201

        runtime.alerting_service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    instance_id="inst-alert-route",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=8.0,
                    minutes_ago=1,
                ),
            )
        )
        alerts_response = client.get("/alerts")
        detail_response = client.get(f"/alerts/{alerts_response.json()[0]['alert_id']}")

    assert alerts_response.status_code == 200
    assert detail_response.status_code == 200
    assert alerts_response.json()[0]["status"] == "open"
    assert alerts_response.json()[0]["acknowledged_by_user_id"] is None
    assert alerts_response.json()[0]["owner_user_id"] is None
    assert detail_response.json()["record"]["rule_name"] == "Replication Lag High"
    assert detail_response.json()["history"][0]["event_type"] == "opened"
    assert len(notifier.requests) == 1


def test_alert_pipeline_records_suppressed_evidence_for_repeated_trigger() -> None:
    anchor = sample_anchor()
    notifier = InMemoryNotifier()
    app = build_app(instance_ids=("inst-alert-noise",), notifier=notifier)
    runtime = cast(AppRuntime, app.state.runtime)

    with TestClient(app) as client:
        login_admin(client)
        rule_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": "mysql",
                "instance_ids": ["inst-alert-noise"],
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
                build_sample(
                    anchor=anchor,
                    instance_id="inst-alert-noise",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=8.0,
                    minutes_ago=12,
                ),
                build_sample(
                    anchor=anchor,
                    instance_id="inst-alert-noise",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="mysql_replication_lag_seconds",
                    metric_value=9.0,
                    minutes_ago=6,
                ),
            )
        )
        alert_id = client.get("/alerts").json()[0]["alert_id"]
        detail_response = client.get(f"/alerts/{alert_id}")

    assert detail_response.status_code == 200
    assert [event["event_type"] for event in detail_response.json()["history"]] == [
        "opened",
        "notified",
        "suppressed",
    ]


def test_alert_pipeline_supports_oracle_rule_lifecycle() -> None:
    anchor = sample_anchor()
    notifier = InMemoryNotifier()
    app = build_app(
        instances=(
            build_instance(
                created_at=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-alert-oracle-route",
                name="inst-alert-oracle-route",
            ),
        ),
        notifier=notifier,
    )
    runtime = cast(AppRuntime, app.state.runtime)

    with TestClient(app) as client:
        login_admin(client)
        create_rule_response = client.post(
            "/alerts/rules",
            json={
                "enabled": True,
                "engine": "oracle",
                "instance_ids": ["inst-alert-oracle-route"],
                "metric_name": "oracle_sessions_active",
                "name": "Oracle Sessions Active High",
                "operator": "gt",
                "severity": "warning",
                "threshold": 6.0,
            },
        )
        assert create_rule_response.status_code == 201

        runtime.alerting_service.evaluate_samples(
            samples=(
                build_sample(
                    anchor=anchor,
                    engine=DatabaseEngine.ORACLE,
                    instance_id="inst-alert-oracle-route",
                    metric_kind=MetricKind.GAUGE,
                    metric_name="oracle_sessions_active",
                    metric_value=8.0,
                    minutes_ago=1,
                ),
            )
        )
        alerts_response = client.get("/alerts")
        detail_response = client.get(f"/alerts/{alerts_response.json()[0]['alert_id']}")

    assert alerts_response.status_code == 200
    assert alerts_response.json()[0]["engine"] == "oracle"
    assert detail_response.status_code == 200
    assert detail_response.json()["record"]["engine"] == "oracle"
    assert detail_response.json()["record"]["rule_name"] == "Oracle Sessions Active High"
    assert detail_response.json()["history"][0]["event_type"] == "opened"
    assert len(notifier.requests) == 1
