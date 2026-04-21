from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from db_monitor_api.analytics.domain import (
    ChartPoint,
    InstanceHealthStatus,
    InstanceMetadata,
    InstanceTrendSnapshot,
    MetricCard,
    MetricSeries,
    OverviewCoverage,
    OverviewEngineSummary,
    OverviewInstanceSnapshot,
    OverviewSnapshot,
    OverviewSummary,
    TimeWindow,
)
from db_monitor_api.analytics.repository import AnalyticsRepository
from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    DatabaseEngine,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import ControlPlaneRepository
from db_monitor_pipeline.domain import MetricSample

AVAILABILITY_METRIC_BY_ENGINE: dict[DatabaseEngine, str] = {
    DatabaseEngine.MYSQL: "mysql_server_available",
    DatabaseEngine.ORACLE: "oracle_server_available",
}

OVERVIEW_METRIC_ENGINES: tuple[DatabaseEngine, ...] = (DatabaseEngine.MYSQL,)
OVERVIEW_INSTANCE_METRIC_ENGINES: tuple[DatabaseEngine, ...] = (DatabaseEngine.MYSQL,)


class AnalyticsInstanceNotFoundError(Exception):
    pass


class MetricAggregation(StrEnum):
    MAX = "max"
    SUM = "sum"


class MetricTransform(StrEnum):
    GAUGE = "gauge"
    RATE = "rate"


@dataclass(frozen=True)
class MetricSpec:
    aggregation: MetricAggregation
    label: str
    output_metric_name: str
    source_metric_name: str
    transform: MetricTransform
    unit: str


OVERVIEW_CARD_SPECS: tuple[MetricSpec, ...] = (
    MetricSpec(MetricAggregation.SUM, "Threads Connected", "mysql_threads_connected", "mysql_threads_connected", MetricTransform.GAUGE, "connections"),
    MetricSpec(MetricAggregation.SUM, "Threads Running", "mysql_threads_running", "mysql_threads_running", MetricTransform.GAUGE, "threads"),
    MetricSpec(MetricAggregation.SUM, "QPS", "mysql_queries_per_second", "mysql_queries_total", MetricTransform.RATE, "qps"),
    MetricSpec(MetricAggregation.SUM, "Inbound Throughput", "mysql_bytes_received_per_second", "mysql_bytes_received_total", MetricTransform.RATE, "bytes/s"),
    MetricSpec(MetricAggregation.SUM, "Outbound Throughput", "mysql_bytes_sent_per_second", "mysql_bytes_sent_total", MetricTransform.RATE, "bytes/s"),
    MetricSpec(
        MetricAggregation.SUM,
        "Buffer Pool Reads",
        "mysql_innodb_buffer_pool_reads_per_second",
        "mysql_innodb_buffer_pool_reads_total",
        MetricTransform.RATE,
        "reads/s",
    ),
    MetricSpec(MetricAggregation.MAX, "Replication Lag", "mysql_replication_lag_seconds", "mysql_replication_lag_seconds", MetricTransform.GAUGE, "seconds"),
)

OVERVIEW_CHART_SPECS: tuple[MetricSpec, ...] = (
    MetricSpec(MetricAggregation.SUM, "Threads Connected", "mysql_threads_connected", "mysql_threads_connected", MetricTransform.GAUGE, "connections"),
    MetricSpec(MetricAggregation.SUM, "Threads Running", "mysql_threads_running", "mysql_threads_running", MetricTransform.GAUGE, "threads"),
    MetricSpec(MetricAggregation.SUM, "QPS", "mysql_queries_per_second", "mysql_queries_total", MetricTransform.RATE, "qps"),
    MetricSpec(MetricAggregation.SUM, "Inbound Throughput", "mysql_bytes_received_per_second", "mysql_bytes_received_total", MetricTransform.RATE, "bytes/s"),
    MetricSpec(MetricAggregation.SUM, "Outbound Throughput", "mysql_bytes_sent_per_second", "mysql_bytes_sent_total", MetricTransform.RATE, "bytes/s"),
    MetricSpec(
        MetricAggregation.SUM,
        "Buffer Pool Reads",
        "mysql_innodb_buffer_pool_reads_per_second",
        "mysql_innodb_buffer_pool_reads_total",
        MetricTransform.RATE,
        "reads/s",
    ),
    MetricSpec(MetricAggregation.MAX, "Replication Lag", "mysql_replication_lag_seconds", "mysql_replication_lag_seconds", MetricTransform.GAUGE, "seconds"),
)

INSTANCE_CARD_SPECS: tuple[MetricSpec, ...] = (
    MetricSpec(MetricAggregation.SUM, "Uptime", "mysql_uptime_seconds", "mysql_uptime_seconds", MetricTransform.GAUGE, "seconds"),
    MetricSpec(MetricAggregation.SUM, "Threads Connected", "mysql_threads_connected", "mysql_threads_connected", MetricTransform.GAUGE, "connections"),
    MetricSpec(MetricAggregation.SUM, "Threads Running", "mysql_threads_running", "mysql_threads_running", MetricTransform.GAUGE, "threads"),
    MetricSpec(MetricAggregation.SUM, "QPS", "mysql_queries_per_second", "mysql_queries_total", MetricTransform.RATE, "qps"),
    MetricSpec(MetricAggregation.SUM, "Inbound Throughput", "mysql_bytes_received_per_second", "mysql_bytes_received_total", MetricTransform.RATE, "bytes/s"),
    MetricSpec(MetricAggregation.SUM, "Outbound Throughput", "mysql_bytes_sent_per_second", "mysql_bytes_sent_total", MetricTransform.RATE, "bytes/s"),
    MetricSpec(
        MetricAggregation.SUM,
        "Buffer Pool Reads",
        "mysql_innodb_buffer_pool_reads_per_second",
        "mysql_innodb_buffer_pool_reads_total",
        MetricTransform.RATE,
        "reads/s",
    ),
    MetricSpec(MetricAggregation.MAX, "Replication Lag", "mysql_replication_lag_seconds", "mysql_replication_lag_seconds", MetricTransform.GAUGE, "seconds"),
)

INSTANCE_CHART_SPECS: tuple[MetricSpec, ...] = (
    MetricSpec(MetricAggregation.SUM, "Threads Connected", "mysql_threads_connected", "mysql_threads_connected", MetricTransform.GAUGE, "connections"),
    MetricSpec(MetricAggregation.SUM, "Threads Running", "mysql_threads_running", "mysql_threads_running", MetricTransform.GAUGE, "threads"),
    MetricSpec(MetricAggregation.SUM, "QPS", "mysql_queries_per_second", "mysql_queries_total", MetricTransform.RATE, "qps"),
    MetricSpec(MetricAggregation.SUM, "Inbound Throughput", "mysql_bytes_received_per_second", "mysql_bytes_received_total", MetricTransform.RATE, "bytes/s"),
    MetricSpec(MetricAggregation.SUM, "Outbound Throughput", "mysql_bytes_sent_per_second", "mysql_bytes_sent_total", MetricTransform.RATE, "bytes/s"),
    MetricSpec(
        MetricAggregation.SUM,
        "Buffer Pool Reads",
        "mysql_innodb_buffer_pool_reads_per_second",
        "mysql_innodb_buffer_pool_reads_total",
        MetricTransform.RATE,
        "reads/s",
    ),
    MetricSpec(MetricAggregation.MAX, "Replication Lag", "mysql_replication_lag_seconds", "mysql_replication_lag_seconds", MetricTransform.GAUGE, "seconds"),
)

ORACLE_INSTANCE_CARD_SPECS: tuple[MetricSpec, ...] = (
    MetricSpec(MetricAggregation.SUM, "Uptime", "oracle_uptime_seconds", "oracle_uptime_seconds", MetricTransform.GAUGE, "seconds"),
    MetricSpec(MetricAggregation.SUM, "Sessions Total", "oracle_sessions_total", "oracle_sessions_total", MetricTransform.GAUGE, "sessions"),
    MetricSpec(MetricAggregation.SUM, "Sessions Active", "oracle_sessions_active", "oracle_sessions_active", MetricTransform.GAUGE, "sessions"),
    MetricSpec(MetricAggregation.SUM, "Session Waits", "oracle_session_waits", "oracle_session_waits", MetricTransform.GAUGE, "sessions"),
    MetricSpec(
        MetricAggregation.SUM,
        "User Calls",
        "oracle_user_calls_per_second",
        "oracle_user_calls_total",
        MetricTransform.RATE,
        "calls/s",
    ),
    MetricSpec(
        MetricAggregation.SUM,
        "Physical Reads",
        "oracle_physical_reads_per_second",
        "oracle_physical_reads_total",
        MetricTransform.RATE,
        "reads/s",
    ),
)

ORACLE_INSTANCE_CHART_SPECS: tuple[MetricSpec, ...] = (
    MetricSpec(MetricAggregation.SUM, "Sessions Total", "oracle_sessions_total", "oracle_sessions_total", MetricTransform.GAUGE, "sessions"),
    MetricSpec(MetricAggregation.SUM, "Sessions Active", "oracle_sessions_active", "oracle_sessions_active", MetricTransform.GAUGE, "sessions"),
    MetricSpec(MetricAggregation.SUM, "Session Waits", "oracle_session_waits", "oracle_session_waits", MetricTransform.GAUGE, "sessions"),
    MetricSpec(
        MetricAggregation.SUM,
        "User Calls",
        "oracle_user_calls_per_second",
        "oracle_user_calls_total",
        MetricTransform.RATE,
        "calls/s",
    ),
    MetricSpec(
        MetricAggregation.SUM,
        "Physical Reads",
        "oracle_physical_reads_per_second",
        "oracle_physical_reads_total",
        MetricTransform.RATE,
        "reads/s",
    ),
)

INSTANCE_CARD_SPECS_BY_ENGINE: dict[DatabaseEngine, tuple[MetricSpec, ...]] = {
    DatabaseEngine.MYSQL: INSTANCE_CARD_SPECS,
    DatabaseEngine.ORACLE: ORACLE_INSTANCE_CARD_SPECS,
}

INSTANCE_CHART_SPECS_BY_ENGINE: dict[DatabaseEngine, tuple[MetricSpec, ...]] = {
    DatabaseEngine.MYSQL: INSTANCE_CHART_SPECS,
    DatabaseEngine.ORACLE: ORACLE_INSTANCE_CHART_SPECS,
}


@dataclass(frozen=True)
class AnalyticsService:
    analytics_repository: AnalyticsRepository
    control_plane_repository: ControlPlaneRepository

    def get_overview(self, *, window: TimeWindow) -> OverviewSnapshot:
        generated_at = utc_now()
        instances = self.control_plane_repository.list_instances(organization_id=None)
        indexed_samples = self._load_indexed_samples(
            generated_at=generated_at,
            instance_ids=tuple(instance.instance_id for instance in instances),
            metric_names=_required_metric_names(
                OVERVIEW_CARD_SPECS + OVERVIEW_CHART_SPECS,
                availability_metrics=tuple(AVAILABILITY_METRIC_BY_ENGINE.values()),
            ),
            window=window,
        )
        snapshots = tuple(
            _build_overview_instance_snapshot(
                instance=instance,
                metric_samples=indexed_samples.get(instance.instance_id, {}),
            )
            for instance in instances
        )
        return OverviewSnapshot(
            bucket_seconds=window.bucket_seconds,
            cards=_build_cards(
                metric_samples_by_instance=indexed_samples.values(),
                specs=OVERVIEW_CARD_SPECS,
            ),
            charts=_build_series(
                bucket_seconds=window.bucket_seconds,
                metric_samples_by_instance=indexed_samples.values(),
                specs=OVERVIEW_CHART_SPECS,
            ),
            coverage=_build_overview_coverage(instances=instances),
            generated_at=generated_at,
            instances=snapshots,
            summary=OverviewSummary(
                engines=_build_overview_engine_summaries(snapshots),
                total_instances=len(snapshots),
                healthy_instances=sum(
                    1 for snapshot in snapshots if snapshot.status is InstanceHealthStatus.HEALTHY
                ),
                unhealthy_instances=sum(
                    1 for snapshot in snapshots if snapshot.status is InstanceHealthStatus.UNHEALTHY
                ),
            ),
            window=window,
        )

    def get_instance_trends(
        self,
        *,
        instance_id: str,
        window: TimeWindow,
    ) -> InstanceTrendSnapshot:
        generated_at = utc_now()
        instance = self.control_plane_repository.get_instance(
            instance_id,
            organization_id=None,
        )
        if instance is None:
            raise AnalyticsInstanceNotFoundError(f"Unknown instance: {instance_id}")
        card_specs = INSTANCE_CARD_SPECS_BY_ENGINE[instance.engine]
        chart_specs = INSTANCE_CHART_SPECS_BY_ENGINE[instance.engine]
        indexed_samples = self._load_indexed_samples(
            generated_at=generated_at,
            instance_ids=(instance_id,),
            metric_names=_required_metric_names(
                card_specs + chart_specs,
                availability_metrics=(AVAILABILITY_METRIC_BY_ENGINE[instance.engine],),
            ),
            window=window,
        )
        metric_samples = indexed_samples.get(instance_id, {})
        status = _resolve_status(instance=instance, metric_samples=metric_samples)
        return InstanceTrendSnapshot(
            bucket_seconds=window.bucket_seconds,
            cards=_build_cards(
                metric_samples_by_instance=(metric_samples,),
                specs=card_specs,
            ),
            charts=_build_series(
                bucket_seconds=window.bucket_seconds,
                metric_samples_by_instance=(metric_samples,),
                specs=chart_specs,
            ),
            generated_at=generated_at,
            instance=InstanceMetadata(
                environment=instance.environment,
                instance_id=instance.instance_id,
                labels=instance.labels,
                name=instance.name,
                status=status,
            ),
            window=window,
        )

    def _load_indexed_samples(
        self,
        *,
        generated_at: datetime,
        instance_ids: tuple[str, ...],
        metric_names: tuple[str, ...],
        window: TimeWindow,
    ) -> dict[str, dict[str, tuple[MetricSample, ...]]]:
        if not instance_ids:
            return {}
        samples = self.analytics_repository.list_metric_samples(
            collected_after=generated_at - window.duration,
            instance_ids=instance_ids,
            metric_names=metric_names,
        )
        return _index_metric_samples(samples)


def _required_metric_names(
    specs: tuple[MetricSpec, ...],
    *,
    availability_metrics: tuple[str, ...],
) -> tuple[str, ...]:
    names = list(availability_metrics)
    names.extend(spec.source_metric_name for spec in specs)
    return tuple(dict.fromkeys(names))


def _build_overview_engine_summaries(
    snapshots: tuple[OverviewInstanceSnapshot, ...],
) -> tuple[OverviewEngineSummary, ...]:
    engines = tuple(
        sorted({snapshot.engine for snapshot in snapshots}, key=lambda engine: engine.value)
    )
    return tuple(
        OverviewEngineSummary(
            engine=engine,
            total_instances=sum(1 for snapshot in snapshots if snapshot.engine is engine),
            healthy_instances=sum(
                1
                for snapshot in snapshots
                if snapshot.engine is engine and snapshot.status is InstanceHealthStatus.HEALTHY
            ),
            unhealthy_instances=sum(
                1
                for snapshot in snapshots
                if snapshot.engine is engine and snapshot.status is InstanceHealthStatus.UNHEALTHY
            ),
        )
        for engine in engines
    )


def _build_overview_coverage(
    *,
    instances: tuple[MonitoredInstance, ...],
) -> OverviewCoverage:
    present_engines = tuple(
        sorted({instance.engine for instance in instances}, key=lambda engine: engine.value)
    )
    return OverviewCoverage(
        detail_analytics_engines=tuple(
            engine for engine in present_engines if engine in INSTANCE_CARD_SPECS_BY_ENGINE
        ),
        fleet_health_engines=tuple(
            engine for engine in present_engines if engine in AVAILABILITY_METRIC_BY_ENGINE
        ),
        overview_instance_metric_engines=tuple(
            engine
            for engine in present_engines
            if engine in OVERVIEW_INSTANCE_METRIC_ENGINES
        ),
        overview_metric_engines=tuple(
            engine for engine in present_engines if engine in OVERVIEW_METRIC_ENGINES
        ),
    )


def _index_metric_samples(
    samples: tuple[MetricSample, ...],
) -> dict[str, dict[str, tuple[MetricSample, ...]]]:
    indexed: dict[str, dict[str, list[MetricSample]]] = {}
    for sample in samples:
        instance_samples = indexed.setdefault(sample.instance_id, {})
        instance_samples.setdefault(sample.metric_name, []).append(sample)
    return {
        instance_id: {
            metric_name: tuple(sorted(metric_samples, key=lambda sample: sample.collected_at))
            for metric_name, metric_samples in instance_samples.items()
        }
        for instance_id, instance_samples in indexed.items()
    }


def _build_overview_instance_snapshot(
    *,
    instance: MonitoredInstance,
    metric_samples: dict[str, tuple[MetricSample, ...]],
) -> OverviewInstanceSnapshot:
    return OverviewInstanceSnapshot(
        environment=instance.environment,
        engine=instance.engine,
        instance_id=instance.instance_id,
        labels=instance.labels,
        name=instance.name,
        qps=_latest_metric_value(metric_samples=metric_samples, spec=OVERVIEW_CARD_SPECS[2]),
        replication_lag_seconds=_latest_metric_value(
            metric_samples=metric_samples,
            spec=OVERVIEW_CARD_SPECS[6],
        ),
        status=_resolve_status(instance=instance, metric_samples=metric_samples),
        threads_connected=_latest_metric_value(
            metric_samples=metric_samples,
            spec=OVERVIEW_CARD_SPECS[0],
        ),
        threads_running=_latest_metric_value(
            metric_samples=metric_samples,
            spec=OVERVIEW_CARD_SPECS[1],
        ),
    )


def _resolve_status(
    *,
    instance: MonitoredInstance,
    metric_samples: dict[str, tuple[MetricSample, ...]],
) -> InstanceHealthStatus:
    availability_metric = AVAILABILITY_METRIC_BY_ENGINE[instance.engine]
    availability = _latest_gauge_value(metric_samples.get(availability_metric, ()))
    if instance.validation.status is ValidationStatus.PASSED and availability >= 1.0:
        return InstanceHealthStatus.HEALTHY
    return InstanceHealthStatus.UNHEALTHY


def _build_cards(
    *,
    metric_samples_by_instance: Iterable[dict[str, tuple[MetricSample, ...]]],
    specs: tuple[MetricSpec, ...],
) -> tuple[MetricCard, ...]:
    materialized = tuple(metric_samples_by_instance)
    return tuple(
        MetricCard(
            label=spec.label,
            metric_name=spec.output_metric_name,
            unit=spec.unit,
            value=_aggregate_values(
                values=[
                    _latest_metric_value(metric_samples=metric_samples, spec=spec)
                    for metric_samples in materialized
                ],
                aggregation=spec.aggregation,
            ),
        )
        for spec in specs
    )


def _build_series(
    *,
    bucket_seconds: int,
    metric_samples_by_instance: Iterable[dict[str, tuple[MetricSample, ...]]],
    specs: tuple[MetricSpec, ...],
) -> tuple[MetricSeries, ...]:
    materialized = tuple(metric_samples_by_instance)
    return tuple(
        MetricSeries(
            label=spec.label,
            metric_name=spec.output_metric_name,
            points=_aggregate_points(
                point_groups=[
                    _build_points_for_metric(
                        bucket_seconds=bucket_seconds,
                        metric_samples=metric_samples.get(spec.source_metric_name, ()),
                        transform=spec.transform,
                    )
                    for metric_samples in materialized
                ],
                aggregation=spec.aggregation,
            ),
            unit=spec.unit,
        )
        for spec in specs
    )


def _aggregate_points(
    *,
    point_groups: list[tuple[ChartPoint, ...]],
    aggregation: MetricAggregation,
) -> tuple[ChartPoint, ...]:
    aggregated: dict[datetime, list[float]] = {}
    for point_group in point_groups:
        for point in point_group:
            aggregated.setdefault(point.timestamp, []).append(point.value)
    return tuple(
        ChartPoint(timestamp=timestamp, value=_aggregate_values(values=values, aggregation=aggregation))
        for timestamp, values in sorted(aggregated.items())
    )


def _build_points_for_metric(
    *,
    bucket_seconds: int,
    metric_samples: tuple[MetricSample, ...],
    transform: MetricTransform,
) -> tuple[ChartPoint, ...]:
    if transform is MetricTransform.GAUGE:
        return _build_gauge_points(bucket_seconds=bucket_seconds, metric_samples=metric_samples)
    return _build_rate_points(bucket_seconds=bucket_seconds, metric_samples=metric_samples)


def _build_gauge_points(
    *,
    bucket_seconds: int,
    metric_samples: tuple[MetricSample, ...],
) -> tuple[ChartPoint, ...]:
    latest_by_bucket: dict[datetime, MetricSample] = {}
    for sample in metric_samples:
        bucket = _bucket_timestamp(sample.collected_at, bucket_seconds)
        previous = latest_by_bucket.get(bucket)
        if previous is None or sample.collected_at > previous.collected_at:
            latest_by_bucket[bucket] = sample
    return tuple(
        ChartPoint(timestamp=timestamp, value=sample.metric_value)
        for timestamp, sample in sorted(latest_by_bucket.items())
    )


def _build_rate_points(
    *,
    bucket_seconds: int,
    metric_samples: tuple[MetricSample, ...],
) -> tuple[ChartPoint, ...]:
    latest_by_bucket: dict[datetime, tuple[datetime, float]] = {}
    for previous, current in zip(metric_samples, metric_samples[1:], strict=False):
        bucket = _bucket_timestamp(current.collected_at, bucket_seconds)
        rate = _rate(previous=previous, current=current)
        existing = latest_by_bucket.get(bucket)
        if existing is None or current.collected_at > existing[0]:
            latest_by_bucket[bucket] = (current.collected_at, rate)
    return tuple(
        ChartPoint(timestamp=timestamp, value=value)
        for timestamp, (_, value) in sorted(latest_by_bucket.items())
    )


def _latest_metric_value(
    *,
    metric_samples: dict[str, tuple[MetricSample, ...]],
    spec: MetricSpec,
) -> float:
    samples = metric_samples.get(spec.source_metric_name, ())
    if spec.transform is MetricTransform.GAUGE:
        return _latest_gauge_value(samples)
    return _latest_rate_value(samples)


def _latest_gauge_value(metric_samples: tuple[MetricSample, ...]) -> float:
    return 0.0 if not metric_samples else metric_samples[-1].metric_value


def _latest_rate_value(metric_samples: tuple[MetricSample, ...]) -> float:
    if len(metric_samples) < 2:
        return 0.0
    return _rate(previous=metric_samples[-2], current=metric_samples[-1])


def _rate(*, previous: MetricSample, current: MetricSample) -> float:
    elapsed_seconds = (current.collected_at - previous.collected_at).total_seconds()
    if elapsed_seconds <= 0:
        return 0.0
    delta = current.metric_value - previous.metric_value
    return 0.0 if delta < 0 else delta / elapsed_seconds


def _aggregate_values(*, values: list[float], aggregation: MetricAggregation) -> float:
    if not values:
        return 0.0
    if aggregation is MetricAggregation.MAX:
        return max(values)
    return sum(values)


def _bucket_timestamp(value: datetime, bucket_seconds: int) -> datetime:
    epoch_seconds = int(value.astimezone(UTC).timestamp())
    bucket_epoch = epoch_seconds - (epoch_seconds % bucket_seconds)
    return datetime.fromtimestamp(bucket_epoch, tz=UTC)
