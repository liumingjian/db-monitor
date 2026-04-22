from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import CollectionJob, MetricKind, MetricSample

MYSQL_TRANSACTION_SOURCE_KEYS = ("Com_commit", "Com_rollback")


@dataclass(frozen=True)
class MetricDefinition:
    kind: MetricKind
    metric_name: str
    source_key: str


MYSQL_APPROVED_METRICS: tuple[MetricDefinition, ...] = (
    MetricDefinition(MetricKind.GAUGE, "mysql_threads_connected", "Threads_connected"),
    MetricDefinition(MetricKind.GAUGE, "mysql_threads_running", "Threads_running"),
    MetricDefinition(MetricKind.COUNTER, "mysql_queries_total", "Questions"),
    MetricDefinition(MetricKind.COUNTER, "mysql_transactions_total", "Transactions"),
    MetricDefinition(MetricKind.COUNTER, "mysql_bytes_received_total", "Bytes_received"),
    MetricDefinition(MetricKind.COUNTER, "mysql_bytes_sent_total", "Bytes_sent"),
    MetricDefinition(
        MetricKind.COUNTER,
        "mysql_innodb_buffer_pool_reads_total",
        "Innodb_buffer_pool_reads",
    ),
    MetricDefinition(MetricKind.GAUGE, "mysql_uptime_seconds", "Uptime"),
    MetricDefinition(
        MetricKind.GAUGE,
        "mysql_replication_lag_seconds",
        "Seconds_Behind_Source",
    ),
)
ORACLE_APPROVED_METRICS: tuple[MetricDefinition, ...] = (
    MetricDefinition(MetricKind.GAUGE, "oracle_sessions_total", "SessionsTotal"),
    MetricDefinition(MetricKind.GAUGE, "oracle_sessions_active", "SessionsActive"),
    MetricDefinition(MetricKind.GAUGE, "oracle_session_waits", "SessionWaits"),
    MetricDefinition(MetricKind.COUNTER, "oracle_user_calls_total", "UserCalls"),
    MetricDefinition(MetricKind.COUNTER, "oracle_physical_reads_total", "PhysicalReads"),
    MetricDefinition(MetricKind.GAUGE, "oracle_uptime_seconds", "UptimeSeconds"),
)
APPROVED_METRICS_BY_ENGINE: dict[DatabaseEngine, tuple[MetricDefinition, ...]] = {
    DatabaseEngine.MYSQL: MYSQL_APPROVED_METRICS,
    DatabaseEngine.ORACLE: ORACLE_APPROVED_METRICS,
}
AVAILABILITY_METRIC_BY_ENGINE: dict[DatabaseEngine, str] = {
    DatabaseEngine.MYSQL: "mysql_server_available",
    DatabaseEngine.ORACLE: "oracle_server_available",
}


def normalize_metrics(
    *,
    collected_at: datetime,
    job: CollectionJob,
    raw_metrics: Mapping[str, str],
) -> tuple[MetricSample, ...]:
    samples = [_availability_sample(collected_at=collected_at, job=job)]
    for definition in APPROVED_METRICS_BY_ENGINE.get(job.engine, ()):
        sample = _build_metric_sample(
            collected_at=collected_at,
            definition=definition,
            job=job,
            raw_metrics=raw_metrics,
        )
        if sample is not None:
            samples.append(sample)
    return tuple(samples)


def _availability_sample(*, collected_at: datetime, job: CollectionJob) -> MetricSample:
    return MetricSample(
        collected_at=collected_at,
        engine=job.engine,
        environment=job.environment,
        instance_id=job.instance_id,
        labels=job.labels,
        metric_kind=MetricKind.GAUGE,
        metric_name=AVAILABILITY_METRIC_BY_ENGINE[job.engine],
        metric_value=1.0,
    )


def _build_metric_sample(
    *,
    collected_at: datetime,
    definition: MetricDefinition,
    job: CollectionJob,
    raw_metrics: Mapping[str, str],
) -> MetricSample | None:
    raw_value = raw_metrics.get(definition.source_key)
    if raw_value is None and definition.metric_name == "mysql_transactions_total":
        raw_value = _coerce_mysql_transaction_total(raw_metrics)
    if raw_value is None:
        return None
    return MetricSample(
        collected_at=collected_at,
        engine=job.engine,
        environment=job.environment,
        instance_id=job.instance_id,
        labels=job.labels,
        metric_kind=definition.kind,
        metric_name=definition.metric_name,
        metric_value=float(raw_value),
    )


def _coerce_mysql_transaction_total(raw_metrics: Mapping[str, str]) -> str | None:
    total = 0.0
    seen = False
    for key in MYSQL_TRANSACTION_SOURCE_KEYS:
        value = raw_metrics.get(key)
        if value is None:
            continue
        total += float(value)
        seen = True
    return str(total) if seen else None
