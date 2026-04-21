from dataclasses import dataclass
from datetime import timedelta, datetime
from enum import StrEnum

from db_monitor_api.control_plane.domain import DatabaseEngine


class TimeWindow(StrEnum):
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    SIX_HOURS = "6h"
    TWENTY_FOUR_HOURS = "24h"

    @property
    def bucket_seconds(self) -> int:
        if self is TimeWindow.FIFTEEN_MINUTES:
            return 60
        if self is TimeWindow.ONE_HOUR:
            return 300
        if self is TimeWindow.SIX_HOURS:
            return 900
        return 3600

    @property
    def duration(self) -> timedelta:
        if self is TimeWindow.FIFTEEN_MINUTES:
            return timedelta(minutes=15)
        if self is TimeWindow.ONE_HOUR:
            return timedelta(hours=1)
        if self is TimeWindow.SIX_HOURS:
            return timedelta(hours=6)
        return timedelta(hours=24)


class InstanceHealthStatus(StrEnum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class ChartPoint:
    timestamp: datetime
    value: float


@dataclass(frozen=True)
class MetricCard:
    label: str
    metric_name: str
    unit: str
    value: float


@dataclass(frozen=True)
class MetricSeries:
    label: str
    metric_name: str
    points: tuple[ChartPoint, ...]
    unit: str


@dataclass(frozen=True)
class OverviewSummary:
    engines: tuple["OverviewEngineSummary", ...]
    total_instances: int
    healthy_instances: int
    unhealthy_instances: int


@dataclass(frozen=True)
class OverviewInstanceSnapshot:
    environment: str
    engine: DatabaseEngine
    instance_id: str
    labels: tuple[str, ...]
    name: str
    qps: float
    replication_lag_seconds: float
    status: InstanceHealthStatus
    threads_connected: float
    threads_running: float


@dataclass(frozen=True)
class OverviewEngineSummary:
    engine: DatabaseEngine
    total_instances: int
    healthy_instances: int
    unhealthy_instances: int


@dataclass(frozen=True)
class OverviewCoverage:
    detail_analytics_engines: tuple[DatabaseEngine, ...]
    fleet_health_engines: tuple[DatabaseEngine, ...]
    overview_instance_metric_engines: tuple[DatabaseEngine, ...]
    overview_metric_engines: tuple[DatabaseEngine, ...]


@dataclass(frozen=True)
class OverviewSnapshot:
    bucket_seconds: int
    cards: tuple[MetricCard, ...]
    charts: tuple[MetricSeries, ...]
    coverage: OverviewCoverage
    generated_at: datetime
    instances: tuple[OverviewInstanceSnapshot, ...]
    summary: OverviewSummary
    window: TimeWindow


@dataclass(frozen=True)
class InstanceMetadata:
    environment: str
    instance_id: str
    labels: tuple[str, ...]
    name: str
    status: InstanceHealthStatus


@dataclass(frozen=True)
class InstanceTrendSnapshot:
    bucket_seconds: int
    cards: tuple[MetricCard, ...]
    charts: tuple[MetricSeries, ...]
    generated_at: datetime
    instance: InstanceMetadata
    window: TimeWindow
