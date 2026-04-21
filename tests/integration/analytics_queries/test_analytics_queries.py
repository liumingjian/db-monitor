from fastapi.testclient import TestClient

from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import (
    build_app,
    build_instance,
    build_sample,
    login_admin,
    sample_anchor,
)


def test_analytics_queries_return_overview_and_instance_trends() -> None:
    anchor = sample_anchor()
    instance_id = "inst-analytics-route"
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
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=300, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=600, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=500, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=1100, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=40, minutes_ago=10),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=100, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_replication_lag_seconds", metric_value=2, minutes_ago=5),
            build_sample(anchor=anchor, instance_id=instance_id, metric_kind=MetricKind.GAUGE, metric_name="mysql_uptime_seconds", metric_value=1300, minutes_ago=5),
        ),
    )

    with TestClient(app) as client:
        login_admin(client)
        overview_response = client.get("/analytics/overview", params={"window": "1h"})
        detail_response = client.get(
            f"/analytics/mysql-instances/{instance_id}/trends",
            params={"window": "1h"},
        )

    assert overview_response.status_code == 200
    assert detail_response.status_code == 200
    assert overview_response.json()["instances"][0]["instance_id"] == instance_id
    assert overview_response.json()["instances"][0]["engine"] == "mysql"
    assert overview_response.json()["coverage"]["overview_metric_engines"] == ["mysql"]
    assert any(
        card["metric_name"] == "mysql_innodb_buffer_pool_reads_per_second"
        for card in overview_response.json()["cards"]
    )
    assert detail_response.json()["instance"]["status"] == "healthy"
    assert detail_response.json()["cards"][0]["metric_name"] == "mysql_uptime_seconds"
    assert any(
        series["metric_name"] == "mysql_queries_per_second"
        for series in detail_response.json()["charts"]
    )
    assert any(
        series["metric_name"] == "mysql_bytes_sent_per_second"
        for series in detail_response.json()["charts"]
    )
    assert any(
        series["metric_name"] == "mysql_innodb_buffer_pool_reads_per_second"
        for series in detail_response.json()["charts"]
    )


def test_analytics_queries_return_oracle_instance_trends() -> None:
    anchor = sample_anchor()
    engine = DatabaseEngine.ORACLE
    instance_id = "inst-oracle-analytics-route"
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
                metric_value=12,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_total",
                metric_value=16,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=3,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=5,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_session_waits",
                metric_value=1,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_user_calls_total",
                metric_value=50,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_user_calls_total",
                metric_value=110,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_physical_reads_total",
                metric_value=80,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_physical_reads_total",
                metric_value=140,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=engine,
                instance_id=instance_id,
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_uptime_seconds",
                metric_value=1500,
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
    assert detail_response.json()["instance"]["status"] == "healthy"
    assert detail_response.json()["cards"][0]["metric_name"] == "oracle_uptime_seconds"
    assert any(
        series["metric_name"] == "oracle_user_calls_per_second"
        for series in detail_response.json()["charts"]
    )
    assert any(
        series["metric_name"] == "oracle_physical_reads_per_second"
        for series in detail_response.json()["charts"]
    )
