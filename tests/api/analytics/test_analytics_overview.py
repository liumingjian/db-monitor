from math import isclose

from db_monitor_api.analytics.domain import OverviewEngineSummary, TimeWindow
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_api.analytics.repository import InMemoryAnalyticsRepository
from db_monitor_api.analytics.service import AnalyticsService
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.domain import MetricKind
from tests.analytics_support import build_instance, build_sample, sample_anchor


def _instance_metrics(instance: object) -> dict[str, float]:
    return {
        metric.metric_name: metric.value
        for metric in instance.metrics  # type: ignore[attr-defined]
    }


def test_analytics_overview_aggregates_metadata_and_metric_series() -> None:
    anchor = sample_anchor()
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(build_instance(created_at=anchor, instance_id="inst-a", name="primary-a"))
    repository.create_instance(build_instance(created_at=anchor, instance_id="inst-b", name="primary-b"))

    analytics_repository = InMemoryAnalyticsRepository(
        samples=(
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.GAUGE, metric_name="mysql_server_available", metric_value=1, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.GAUGE, metric_name="mysql_server_available", metric_value=1, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_connected", metric_value=10, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_connected", metric_value=12, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_running", metric_value=2, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_running", metric_value=3, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.COUNTER, metric_name="mysql_queries_total", metric_value=100, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.COUNTER, metric_name="mysql_queries_total", metric_value=220, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=300, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=600, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=400, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=1000, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=40, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=100, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-a", metric_kind=MetricKind.GAUGE, metric_name="mysql_replication_lag_seconds", metric_value=1, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.GAUGE, metric_name="mysql_server_available", metric_value=1, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.GAUGE, metric_name="mysql_server_available", metric_value=1, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_connected", metric_value=5, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_connected", metric_value=6, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_running", metric_value=1, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.GAUGE, metric_name="mysql_threads_running", metric_value=2, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.COUNTER, metric_name="mysql_queries_total", metric_value=50, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.COUNTER, metric_name="mysql_queries_total", metric_value=110, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=100, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_received_total", metric_value=250, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=200, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.COUNTER, metric_name="mysql_bytes_sent_total", metric_value=500, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=20, minutes_ago=10),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.COUNTER, metric_name="mysql_innodb_buffer_pool_reads_total", metric_value=50, minutes_ago=5),
            build_sample(anchor=anchor, instance_id="inst-b", metric_kind=MetricKind.GAUGE, metric_name="mysql_replication_lag_seconds", metric_value=5, minutes_ago=5),
        ),
    )

    snapshot = AnalyticsService(
        analytics_repository=analytics_repository,
        control_plane_repository=repository,
    ).get_overview(window=TimeWindow.ONE_HOUR)

    cards = {card.metric_name: card.value for card in snapshot.cards}
    instances = {instance.instance_id: instance for instance in snapshot.instances}

    assert snapshot.summary.total_instances == 2
    assert snapshot.summary.healthy_instances == 2
    assert snapshot.summary.unhealthy_instances == 0
    assert snapshot.summary.engines == (
        OverviewEngineSummary(
            engine=DatabaseEngine.MYSQL,
            total_instances=2,
            healthy_instances=2,
            unhealthy_instances=0,
        ),
    )
    assert snapshot.coverage.detail_analytics_engines == (DatabaseEngine.MYSQL,)
    assert snapshot.coverage.fleet_health_engines == (DatabaseEngine.MYSQL,)
    assert snapshot.coverage.overview_instance_metric_engines == (DatabaseEngine.MYSQL,)
    assert snapshot.coverage.overview_metric_engines == (DatabaseEngine.MYSQL,)
    assert isclose(cards["mysql_threads_connected"], 18.0)
    assert isclose(cards["mysql_queries_per_second"], 0.6)
    assert isclose(cards["mysql_bytes_received_per_second"], 1.5)
    assert isclose(cards["mysql_bytes_sent_per_second"], 3.0)
    assert isclose(cards["mysql_innodb_buffer_pool_reads_per_second"], 0.3)
    assert isclose(cards["mysql_replication_lag_seconds"], 5.0)
    assert instances["inst-a"].engine is DatabaseEngine.MYSQL
    assert instances["inst-b"].engine is DatabaseEngine.MYSQL
    assert isclose(_instance_metrics(instances["inst-a"])["mysql_queries_per_second"], 0.4)
    assert isclose(_instance_metrics(instances["inst-b"])["mysql_queries_per_second"], 0.2)
    assert isclose(
        _instance_metrics(instances["inst-a"])["mysql_replication_lag_seconds"],
        1.0,
    )
    assert isclose(
        _instance_metrics(instances["inst-b"])["mysql_replication_lag_seconds"],
        5.0,
    )
    assert len(snapshot.charts) == 7


def test_analytics_overview_preserves_mixed_engine_instance_metadata() -> None:
    anchor = sample_anchor()
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(build_instance(created_at=anchor, instance_id="inst-mysql", name="primary-a"))
    repository.create_instance(
        build_instance(
            created_at=anchor,
            engine=DatabaseEngine.ORACLE,
            instance_id="inst-oracle",
            name="oracle-a",
        )
    )

    analytics_repository = InMemoryAnalyticsRepository(
        samples=(
            build_sample(
                anchor=anchor,
                instance_id="inst-mysql",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_server_available",
                metric_value=1,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-mysql",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_connected",
                metric_value=12,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-mysql",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_threads_running",
                metric_value=4,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-mysql",
                metric_kind=MetricKind.COUNTER,
                metric_name="mysql_queries_total",
                metric_value=220,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-mysql",
                metric_kind=MetricKind.COUNTER,
                metric_name="mysql_queries_total",
                metric_value=100,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                instance_id="inst-mysql",
                metric_kind=MetricKind.GAUGE,
                metric_name="mysql_replication_lag_seconds",
                metric_value=2,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_server_available",
                metric_value=1,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_server_available",
                metric_value=1,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_total",
                metric_value=20,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_total",
                metric_value=24,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=4,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_sessions_active",
                metric_value=6,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_session_waits",
                metric_value=1,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.GAUGE,
                metric_name="oracle_session_waits",
                metric_value=2,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_user_calls_total",
                metric_value=60,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_user_calls_total",
                metric_value=120,
                minutes_ago=5,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_physical_reads_total",
                metric_value=40,
                minutes_ago=10,
            ),
            build_sample(
                anchor=anchor,
                engine=DatabaseEngine.ORACLE,
                instance_id="inst-oracle",
                metric_kind=MetricKind.COUNTER,
                metric_name="oracle_physical_reads_total",
                metric_value=70,
                minutes_ago=5,
            ),
        ),
    )

    snapshot = AnalyticsService(
        analytics_repository=analytics_repository,
        control_plane_repository=repository,
    ).get_overview(window=TimeWindow.ONE_HOUR)

    instances = {instance.instance_id: instance for instance in snapshot.instances}
    oracle = instances["inst-oracle"]

    assert snapshot.summary.total_instances == 2
    assert snapshot.summary.healthy_instances == 2
    assert snapshot.summary.engines == (
        OverviewEngineSummary(
            engine=DatabaseEngine.MYSQL,
            total_instances=1,
            healthy_instances=1,
            unhealthy_instances=0,
        ),
        OverviewEngineSummary(
            engine=DatabaseEngine.ORACLE,
            total_instances=1,
            healthy_instances=1,
            unhealthy_instances=0,
        ),
    )
    assert snapshot.coverage.detail_analytics_engines == (
        DatabaseEngine.MYSQL,
        DatabaseEngine.ORACLE,
    )
    assert snapshot.coverage.fleet_health_engines == (
        DatabaseEngine.MYSQL,
        DatabaseEngine.ORACLE,
    )
    assert snapshot.coverage.overview_instance_metric_engines == (
        DatabaseEngine.MYSQL,
        DatabaseEngine.ORACLE,
    )
    assert snapshot.coverage.overview_metric_engines == (
        DatabaseEngine.MYSQL,
        DatabaseEngine.ORACLE,
    )
    assert oracle.engine is DatabaseEngine.ORACLE
    assert oracle.status.value == "healthy"
    oracle_metrics = _instance_metrics(oracle)
    assert isclose(oracle_metrics["oracle_sessions_total"], 24.0)
    assert isclose(oracle_metrics["oracle_sessions_active"], 6.0)
    assert isclose(oracle_metrics["oracle_session_waits"], 2.0)
    assert isclose(oracle_metrics["oracle_user_calls_per_second"], 0.2)
    assert isclose(oracle_metrics["oracle_physical_reads_per_second"], 0.1)
