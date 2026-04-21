from dataclasses import dataclass

from db_monitor_api.control_plane.domain import DatabaseEngine


@dataclass(frozen=True)
class AlertMetricCatalogEntry:
    label: str
    metric_name: str
    unit: str


@dataclass(frozen=True)
class AlertEngineCatalog:
    engine: DatabaseEngine
    metrics: tuple[AlertMetricCatalogEntry, ...]


MYSQL_ALERT_METRICS: tuple[AlertMetricCatalogEntry, ...] = (
    AlertMetricCatalogEntry("Server Availability", "mysql_server_available", "status"),
    AlertMetricCatalogEntry("Threads Connected", "mysql_threads_connected", "connections"),
    AlertMetricCatalogEntry("Threads Running", "mysql_threads_running", "threads"),
    AlertMetricCatalogEntry("Uptime", "mysql_uptime_seconds", "seconds"),
    AlertMetricCatalogEntry("Replication Lag", "mysql_replication_lag_seconds", "seconds"),
)

ORACLE_ALERT_METRICS: tuple[AlertMetricCatalogEntry, ...] = (
    AlertMetricCatalogEntry("Server Availability", "oracle_server_available", "status"),
    AlertMetricCatalogEntry("Sessions Total", "oracle_sessions_total", "sessions"),
    AlertMetricCatalogEntry("Sessions Active", "oracle_sessions_active", "sessions"),
    AlertMetricCatalogEntry("Session Waits", "oracle_session_waits", "sessions"),
    AlertMetricCatalogEntry("Uptime", "oracle_uptime_seconds", "seconds"),
)

ALERT_METRIC_CATALOG_BY_ENGINE: dict[DatabaseEngine, tuple[AlertMetricCatalogEntry, ...]] = {
    DatabaseEngine.MYSQL: MYSQL_ALERT_METRICS,
    DatabaseEngine.ORACLE: ORACLE_ALERT_METRICS,
}


def list_alert_metric_catalog() -> tuple[AlertEngineCatalog, ...]:
    return tuple(
        AlertEngineCatalog(engine=engine, metrics=metrics)
        for engine, metrics in ALERT_METRIC_CATALOG_BY_ENGINE.items()
    )


def supports_alert_metric(*, engine: DatabaseEngine, metric_name: str) -> bool:
    return any(
        entry.metric_name == metric_name
        for entry in ALERT_METRIC_CATALOG_BY_ENGINE.get(engine, ())
    )
