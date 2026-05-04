from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from db_monitor_api.analytics.domain import (
    InstanceTrendSnapshot,
    MetricCard,
    MetricSeries,
    OverviewCoverage,
    OverviewEngineSummary,
    OverviewSnapshot,
    TimeWindow,
)
from db_monitor_api.analytics.service import AnalyticsInstanceNotFoundError
from db_monitor_api.auth.domain import AuthContext, Permission
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_api.dependencies import get_runtime, require_permission_dependency
from db_monitor_api.runtime import AppRuntime

router = APIRouter()


class ChartPointResponse(BaseModel):
    timestamp: str
    value: float


class MetricCardResponse(BaseModel):
    label: str
    metric_name: str
    unit: str
    value: float


class MetricSeriesResponse(BaseModel):
    label: str
    metric_name: str
    points: list[ChartPointResponse]
    unit: str


class OverviewSummaryResponse(BaseModel):
    engines: list["OverviewEngineSummaryResponse"]
    total_instances: int
    healthy_instances: int
    unhealthy_instances: int


class OverviewEngineSummaryResponse(BaseModel):
    engine: DatabaseEngine
    total_instances: int
    healthy_instances: int
    unhealthy_instances: int


class OverviewCoverageResponse(BaseModel):
    detail_analytics_engines: list[DatabaseEngine]
    fleet_health_engines: list[DatabaseEngine]
    overview_instance_metric_engines: list[DatabaseEngine]
    overview_metric_engines: list[DatabaseEngine]


class OverviewInstanceResponse(BaseModel):
    environment: str
    engine: DatabaseEngine
    instance_id: str
    labels: list[str]
    metrics: list[MetricCardResponse]
    name: str
    status: str


class OverviewResponse(BaseModel):
    bucket_seconds: int
    cards: list[MetricCardResponse]
    charts: list[MetricSeriesResponse]
    coverage: OverviewCoverageResponse
    generated_at: str
    instances: list[OverviewInstanceResponse]
    summary: OverviewSummaryResponse
    window: str


class InstanceMetadataResponse(BaseModel):
    environment: str
    instance_id: str
    labels: list[str]
    name: str
    server_role: str | None
    server_version: str | None
    status: str


class InstanceTrendResponse(BaseModel):
    bucket_seconds: int
    cards: list[MetricCardResponse]
    charts: list[MetricSeriesResponse]
    generated_at: str
    instance: InstanceMetadataResponse
    window: str


def build_analytics_router() -> APIRouter:
    return router


@router.get("/analytics/overview", response_model=OverviewResponse)
def get_overview(
    window: TimeWindow = TimeWindow.ONE_HOUR,
    _: AuthContext = Depends(require_permission_dependency(Permission.INSTANCES_READ, "analytics")),
    runtime: AppRuntime = Depends(get_runtime),
) -> OverviewResponse:
    return _build_overview_response(runtime.analytics_service.get_overview(window=window))


@router.get(
    "/analytics/mysql-instances/{instance_id}/trends",
    response_model=InstanceTrendResponse,
    include_in_schema=False,
)
@router.get(
    "/analytics/instances/{instance_id}/trends",
    response_model=InstanceTrendResponse,
)
def get_instance_trends(
    instance_id: str,
    window: TimeWindow = TimeWindow.ONE_HOUR,
    _: AuthContext = Depends(require_permission_dependency(Permission.INSTANCES_READ, "analytics")),
    runtime: AppRuntime = Depends(get_runtime),
) -> InstanceTrendResponse:
    try:
        snapshot = runtime.analytics_service.get_instance_trends(
            instance_id=instance_id,
            window=window,
        )
    except AnalyticsInstanceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return _build_instance_trend_response(snapshot)


def _build_overview_response(snapshot: OverviewSnapshot) -> OverviewResponse:
    return OverviewResponse(
        bucket_seconds=snapshot.bucket_seconds,
        cards=[_build_metric_card_response(card) for card in snapshot.cards],
        charts=[_build_metric_series_response(series) for series in snapshot.charts],
        coverage=_build_overview_coverage_response(snapshot.coverage),
        generated_at=snapshot.generated_at.isoformat(),
        instances=[
            OverviewInstanceResponse(
                environment=instance.environment,
                engine=instance.engine,
                instance_id=instance.instance_id,
                labels=list(instance.labels),
                metrics=[
                    _build_metric_card_response(metric)
                    for metric in instance.metrics
                ],
                name=instance.name,
                status=instance.status.value,
            )
            for instance in snapshot.instances
        ],
        summary=OverviewSummaryResponse(
            engines=[
                _build_overview_engine_summary_response(engine_summary)
                for engine_summary in snapshot.summary.engines
            ],
            total_instances=snapshot.summary.total_instances,
            healthy_instances=snapshot.summary.healthy_instances,
            unhealthy_instances=snapshot.summary.unhealthy_instances,
        ),
        window=snapshot.window.value,
    )


def _build_overview_engine_summary_response(
    engine_summary: OverviewEngineSummary,
) -> OverviewEngineSummaryResponse:
    return OverviewEngineSummaryResponse(
        engine=engine_summary.engine,
        total_instances=engine_summary.total_instances,
        healthy_instances=engine_summary.healthy_instances,
        unhealthy_instances=engine_summary.unhealthy_instances,
    )


def _build_overview_coverage_response(
    coverage: OverviewCoverage,
) -> OverviewCoverageResponse:
    return OverviewCoverageResponse(
        detail_analytics_engines=list(coverage.detail_analytics_engines),
        fleet_health_engines=list(coverage.fleet_health_engines),
        overview_instance_metric_engines=list(coverage.overview_instance_metric_engines),
        overview_metric_engines=list(coverage.overview_metric_engines),
    )


def _build_instance_trend_response(snapshot: InstanceTrendSnapshot) -> InstanceTrendResponse:
    return InstanceTrendResponse(
        bucket_seconds=snapshot.bucket_seconds,
        cards=[_build_metric_card_response(card) for card in snapshot.cards],
        charts=[_build_metric_series_response(series) for series in snapshot.charts],
        generated_at=snapshot.generated_at.isoformat(),
        instance=InstanceMetadataResponse(
            environment=snapshot.instance.environment,
            instance_id=snapshot.instance.instance_id,
            labels=list(snapshot.instance.labels),
            name=snapshot.instance.name,
            server_role=snapshot.instance.server_role,
            server_version=snapshot.instance.server_version,
            status=snapshot.instance.status.value,
        ),
        window=snapshot.window.value,
    )


def _build_metric_card_response(card: MetricCard) -> MetricCardResponse:
    return MetricCardResponse(
        label=card.label,
        metric_name=card.metric_name,
        unit=card.unit,
        value=card.value,
    )


def _build_metric_series_response(series: MetricSeries) -> MetricSeriesResponse:
    return MetricSeriesResponse(
        label=series.label,
        metric_name=series.metric_name,
        points=[
            ChartPointResponse(timestamp=point.timestamp.isoformat(), value=point.value)
            for point in series.points
        ],
        unit=series.unit,
    )
