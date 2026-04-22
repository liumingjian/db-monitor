from fastapi.testclient import TestClient
from typing import cast

from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import (
    build_app,
    build_instance,
    build_sample,
    login_admin,
    sample_anchor,
)


def _instance_metrics(instance: dict[str, object]) -> dict[str, float]:
    metrics = cast(list[dict[str, object]], instance["metrics"])
    return {
        cast(str, metric["metric_name"]): float(cast(float | int | str, metric["value"]))
        for metric in metrics
    }


def test_analytics_contract_returns_chart_ready_payloads() -> None:
    anchor = sample_anchor()
    instance_id = "inst-analytics-contract"
    app = build_app(
        instances=(build_instance(created_at=anchor, instance_id=instance_id, name="primary"),),
        samples=(
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_server_available", metric_value=1, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_server_available", metric_value=1, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_connected", metric_value=10, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_connected", metric_value=12, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_running", metric_value=2, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_running", metric_value=4, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_queries_total", metric_value=100, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_queries_total", metric_value=220, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_transactions_total", metric_value=50, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_transactions_total", metric_value=110, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=300, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=600, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=500, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=1100, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=40, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=100, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_replication_lag_seconds", metric_value=0, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_replication_lag_seconds", metric_value=1, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_uptime_seconds", metric_value=1000, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_uptime_seconds", metric_value=1300, minutes_ago=5),
        ),
    )

    with TestClient(app) as client:
        login_admin(client)

        overview_response = client.get("/analytics/overview", params={"window": "1h"})
        detail_response = client.get(
            f"/analytics/instances/{instance_id}/trends",
            params={"window": "1h"},
        )

    assert overview_response.status_code == 200
    assert detail_response.status_code == 200

    overview = overview_response.json()
    detail = detail_response.json()

    assert overview["window"] == "1h"
    assert overview["bucket_seconds"] == 300
    assert set(overview["summary"]) == {
        "engines",
        "healthy_instances",
        "total_instances",
        "unhealthy_instances",
    }
    assert overview["summary"]["engines"] == [
        {
            "engine": "mysql",
            "healthy_instances": 1,
            "total_instances": 1,
            "unhealthy_instances": 0,
        }
    ]
    assert overview["coverage"] == {
        "detail_analytics_engines": ["mysql"],
        "fleet_health_engines": ["mysql"],
        "overview_instance_metric_engines": ["mysql"],
        "overview_metric_engines": ["mysql"],
    }
    assert overview["instances"][0]["engine"] == "mysql"
    assert _instance_metrics(overview["instances"][0]) == {
        "mysql_threads_connected": 12,
        "mysql_threads_running": 4,
        "mysql_queries_per_second": 0.4,
        "mysql_bytes_received_per_second": 1.0,
        "mysql_bytes_sent_per_second": 2.0,
        "mysql_innodb_buffer_pool_reads_per_second": 0.2,
        "mysql_replication_lag_seconds": 1,
    }
    assert {card["metric_name"] for card in overview["cards"]} >= {
        "mysql_bytes_received_per_second",
        "mysql_bytes_sent_per_second",
        "mysql_innodb_buffer_pool_reads_per_second",
        "mysql_queries_per_second",
        "mysql_replication_lag_seconds",
        "mysql_threads_connected",
    }
    assert overview["charts"][0]["points"][0]["timestamp"].endswith("+00:00")

    assert detail["instance"]["instance_id"] == instance_id
    assert detail["instance"]["server_role"] == "primary"
    assert detail["instance"]["server_version"] == "8.4.0"
    assert detail["window"] == "1h"
    assert {card["metric_name"] for card in detail["cards"]} >= {
        "mysql_bytes_received_per_second",
        "mysql_bytes_sent_per_second",
        "mysql_innodb_buffer_pool_reads_per_second",
        "mysql_queries_per_second",
        "mysql_transactions_per_second",
    }
    assert {series["metric_name"] for series in detail["charts"]} >= {
        "mysql_bytes_received_per_second",
        "mysql_bytes_sent_per_second",
        "mysql_innodb_buffer_pool_reads_per_second",
        "mysql_queries_per_second",
        "mysql_threads_running",
    }


def test_analytics_contract_carries_mixed_engine_overview_instance_metadata() -> None:
    anchor = sample_anchor()
    mysql_id = "inst-mysql-contract"
    oracle_id = "inst-oracle-contract"
    app = build_app(
        instances=(
            build_instance(created_at=anchor, instance_id=mysql_id, name="primary"),
            build_instance(
                created_at=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                name="oracle-primary",
            ),
        ),
        samples=(
            build_sample(
                anchor=anchor,
                instance_id=mysql_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_server_available",
                metric_value=1,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                instance_id=mysql_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_connected",
                metric_value=12,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                instance_id=mysql_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=4,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                instance_id=mysql_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="mysql_queries_total",
                metric_value=100,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                instance_id=mysql_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="mysql_queries_total",
                metric_value=220,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                instance_id=mysql_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=2,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_server_available",
                metric_value=1,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_server_available",
                metric_value=1,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_total",
                metric_value=18,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_total",
                metric_value=24,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=4,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=6,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_session_waits",
                metric_value=1,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_session_waits",
                metric_value=2,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_user_calls_total",
                metric_value=60,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_user_calls_total",
                metric_value=120,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_physical_reads_total",
                metric_value=30,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id=oracle_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_physical_reads_total",
                metric_value=60,
                minutes_ago=5,
            ),
        ),
    )

    with TestClient(app) as client:
        login_admin(client)
        overview_response = client.get("/analytics/overview", params={"window": "1h"})

    assert overview_response.status_code == 200
    overview = overview_response.json()
    instances = {instance["instance_id"]: instance for instance in overview["instances"]}

    assert instances[mysql_id]["engine"] == "mysql"
    assert instances[oracle_id]["engine"] == "oracle"
    assert instances[oracle_id]["status"] == "healthy"
    assert _instance_metrics(instances[mysql_id])["mysql_queries_per_second"] == 0.4
    assert _instance_metrics(instances[oracle_id]) == {
        "oracle_sessions_total": 24,
        "oracle_sessions_active": 6,
        "oracle_session_waits": 2,
        "oracle_user_calls_per_second": 0.2,
        "oracle_physical_reads_per_second": 0.1,
    }
    assert {card["metric_name"] for card in overview["cards"]} >= {
        "oracle_sessions_total",
        "oracle_sessions_active",
        "oracle_session_waits",
        "oracle_user_calls_per_second",
        "oracle_physical_reads_per_second",
    }
    assert overview["summary"]["engines"] == [
        {
            "engine": "mysql",
            "healthy_instances": 1,
            "total_instances": 1,
            "unhealthy_instances": 0,
        },
        {
            "engine": "oracle",
            "healthy_instances": 1,
            "total_instances": 1,
            "unhealthy_instances": 0,
        },
    ]
    assert overview["coverage"] == {
        "detail_analytics_engines": ["mysql", "oracle"],
        "fleet_health_engines": ["mysql", "oracle"],
        "overview_instance_metric_engines": ["mysql", "oracle"],
        "overview_metric_engines": ["mysql", "oracle"],
    }


def test_analytics_contract_returns_oracle_detail_payloads() -> None:
    anchor = sample_anchor()
    engine = DatabaseEngine.ORACLE
    instance_id = "inst-analytics-oracle-contract"
    app = build_app(
        instances=(
            build_instance(
                created_at=anchor,
                engine=engine,
                instance_id=instance_id,
                name="oracle-primary",
            ),
        ),
        samples=(
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_server_available",
                metric_value=1,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_server_available",
                metric_value=1,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_total",
                metric_value=20,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_total",
                metric_value=24,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=4,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=6,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_session_waits",
                metric_value=1,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_session_waits",
                metric_value=2,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_user_calls_total",
                metric_value=100,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_user_calls_total",
                metric_value=220,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_physical_reads_total",
                metric_value=300,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_physical_reads_total",
                metric_value=450,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_uptime_seconds",
                metric_value=1000,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_uptime_seconds",
                metric_value=1300,
                minutes_ago=5,
            ),
        ),
    )

    with TestClient(app) as client:
        login_admin(client)
        detail_response = client.get(
            f"/analytics/instances/{instance_id}/trends",
            params={"window": "1h"},
        )

    assert detail_response.status_code == 200
    detail = detail_response.json()

    assert detail["instance"]["instance_id"] == instance_id
    assert detail["instance"]["server_role"] == "primary"
    assert detail["instance"]["server_version"] == "11.2.0"
    assert detail["instance"]["status"] == "healthy"
    assert detail["window"] == "1h"
    assert {card["metric_name"] for card in detail["cards"]} >= {
        "oracle_physical_reads_per_second",
        "oracle_sessions_active",
        "oracle_sessions_total",
        "oracle_uptime_seconds",
        "oracle_user_calls_per_second",
    }
    assert {series["metric_name"] for series in detail["charts"]} >= {
        "oracle_physical_reads_per_second",
        "oracle_session_waits",
        "oracle_sessions_active",
        "oracle_sessions_total",
        "oracle_user_calls_per_second",
    }
