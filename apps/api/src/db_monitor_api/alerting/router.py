from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from db_monitor_api.alerting.domain import (
    AlertDetail,
    AlertHistoryEvent,
    AlertRecord,
    AlertRule,
    RuleOperator,
    RuleSeverity,
)
from db_monitor_api.alerting.catalog import (
    AlertEngineCatalog,
    AlertMetricCatalogEntry,
    list_alert_metric_catalog,
)
from db_monitor_api.alerting.service import AlertNotFoundError, AlertWorkflowValidationError
from db_monitor_api.auth.domain import AuthContext, Permission
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_api.dependencies import get_runtime, require_permission_dependency
from db_monitor_api.runtime import AppRuntime

router = APIRouter()


class CreateRuleRequest(BaseModel):
    enabled: bool = True
    engine: DatabaseEngine
    instance_ids: list[str] = Field(default_factory=list)
    metric_name: str
    name: str
    operator: RuleOperator
    severity: RuleSeverity
    threshold: float


class AddAlertNoteRequest(BaseModel):
    note: str = Field(min_length=1)


class AssignAlertOwnerRequest(BaseModel):
    owner_user_id: str


class AlertRuleResponse(BaseModel):
    created_at: str
    enabled: bool
    engine: DatabaseEngine
    instance_ids: list[str]
    metric_name: str
    name: str
    operator: str
    rule_id: str
    severity: str
    threshold: float


class AlertRecordResponse(BaseModel):
    alert_id: str
    acknowledged_at: str | None
    acknowledged_by_user_id: str | None
    current_value: float
    engine: DatabaseEngine
    instance_id: str
    last_evaluated_at: str
    metric_name: str
    opened_at: str
    owner_assigned_at: str | None
    owner_user_id: str | None
    resolved_at: str | None
    rule_id: str
    rule_name: str
    severity: str
    status: str
    threshold: float


class AlertHistoryResponse(BaseModel):
    alert_id: str
    detail: str
    event_type: str
    occurred_at: str


class AlertMetricCatalogEntryResponse(BaseModel):
    label: str
    metric_name: str
    unit: str


class AlertEngineCatalogResponse(BaseModel):
    engine: DatabaseEngine
    metrics: list[AlertMetricCatalogEntryResponse]


class AlertDetailResponse(BaseModel):
    history: list[AlertHistoryResponse]
    record: AlertRecordResponse


def build_alerting_router() -> APIRouter:
    return router


@router.post("/alerts/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    payload: CreateRuleRequest,
    context: AuthContext = Depends(require_permission_dependency(Permission.RULES_WRITE, "rules")),
    runtime: AppRuntime = Depends(get_runtime),
) -> AlertRuleResponse:
    try:
        rule = runtime.alerting_service.create_rule(
            actor_user_id=context.user.user_id,
            enabled=payload.enabled,
            engine=payload.engine,
            instance_ids=tuple(payload.instance_ids),
            metric_name=payload.metric_name,
            name=payload.name,
            operator=payload.operator,
            organization_id=context.active_organization.organization_id,
            severity=payload.severity,
            threshold=payload.threshold,
        )
    except AlertWorkflowValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return _build_rule_response(rule)


@router.get("/alerts/rules", response_model=list[AlertRuleResponse])
def list_rules(
    context: AuthContext = Depends(require_permission_dependency(Permission.RULES_READ, "rules")),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[AlertRuleResponse]:
    return [
        _build_rule_response(rule)
        for rule in runtime.alerting_service.list_rules(
            organization_id=context.active_organization.organization_id
        )
    ]


@router.get("/alerts/rule-catalog", response_model=list[AlertEngineCatalogResponse])
def list_rule_catalog(
    context: AuthContext = Depends(require_permission_dependency(Permission.RULES_READ, "rules")),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[AlertEngineCatalogResponse]:
    del context, runtime
    return [_build_rule_catalog_response(catalog) for catalog in list_alert_metric_catalog()]


@router.get("/alerts", response_model=list[AlertRecordResponse])
def list_alerts(
    context: AuthContext = Depends(require_permission_dependency(Permission.RULES_READ, "alerts")),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[AlertRecordResponse]:
    return [
        _build_alert_response(alert)
        for alert in runtime.alerting_service.list_alerts(
            organization_id=context.active_organization.organization_id
        )
    ]


@router.get("/alerts/{alert_id}", response_model=AlertDetailResponse)
def get_alert(
    alert_id: str,
    context: AuthContext = Depends(require_permission_dependency(Permission.RULES_READ, "alerts")),
    runtime: AppRuntime = Depends(get_runtime),
) -> AlertDetailResponse:
    try:
        detail = runtime.alerting_service.get_alert(
            alert_id=alert_id,
            organization_id=context.active_organization.organization_id,
        )
    except AlertNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return _build_alert_detail_response(detail)


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertDetailResponse)
def acknowledge_alert(
    alert_id: str,
    context: AuthContext = Depends(require_permission_dependency(Permission.RULES_WRITE, "alerts")),
    runtime: AppRuntime = Depends(get_runtime),
) -> AlertDetailResponse:
    try:
        detail = runtime.alerting_service.acknowledge_alert(
            actor_user_id=context.user.user_id,
            alert_id=alert_id,
            organization_id=context.active_organization.organization_id,
        )
    except AlertNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except AlertWorkflowValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return _build_alert_detail_response(detail)


@router.put("/alerts/{alert_id}/owner", response_model=AlertDetailResponse)
def assign_alert_owner(
    alert_id: str,
    payload: AssignAlertOwnerRequest,
    context: AuthContext = Depends(require_permission_dependency(Permission.RULES_WRITE, "alerts")),
    runtime: AppRuntime = Depends(get_runtime),
) -> AlertDetailResponse:
    try:
        detail = runtime.alerting_service.assign_alert_owner(
            actor_user_id=context.user.user_id,
            alert_id=alert_id,
            organization_id=context.active_organization.organization_id,
            owner_user_id=payload.owner_user_id,
        )
    except AlertNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except AlertWorkflowValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return _build_alert_detail_response(detail)


@router.post("/alerts/{alert_id}/notes", response_model=AlertDetailResponse)
def add_alert_note(
    alert_id: str,
    payload: AddAlertNoteRequest,
    context: AuthContext = Depends(require_permission_dependency(Permission.RULES_WRITE, "alerts")),
    runtime: AppRuntime = Depends(get_runtime),
) -> AlertDetailResponse:
    try:
        detail = runtime.alerting_service.add_alert_note(
            actor_user_id=context.user.user_id,
            alert_id=alert_id,
            note=payload.note,
            organization_id=context.active_organization.organization_id,
        )
    except AlertNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except AlertWorkflowValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return _build_alert_detail_response(detail)


def _build_rule_response(rule: AlertRule) -> AlertRuleResponse:
    return AlertRuleResponse(
        created_at=rule.created_at.isoformat(),
        enabled=rule.enabled,
        engine=rule.engine,
        instance_ids=list(rule.instance_ids),
        metric_name=rule.metric_name,
        name=rule.name,
        operator=rule.operator.value,
        rule_id=rule.rule_id,
        severity=rule.severity.value,
        threshold=rule.threshold,
    )


def _build_alert_response(alert: AlertRecord) -> AlertRecordResponse:
    return AlertRecordResponse(
        alert_id=alert.alert_id,
        acknowledged_at=None if alert.acknowledged_at is None else alert.acknowledged_at.isoformat(),
        acknowledged_by_user_id=alert.acknowledged_by_user_id,
        current_value=alert.current_value,
        engine=alert.engine,
        instance_id=alert.instance_id,
        last_evaluated_at=alert.last_evaluated_at.isoformat(),
        metric_name=alert.metric_name,
        opened_at=alert.opened_at.isoformat(),
        owner_assigned_at=None if alert.owner_assigned_at is None else alert.owner_assigned_at.isoformat(),
        owner_user_id=alert.owner_user_id,
        resolved_at=None if alert.resolved_at is None else alert.resolved_at.isoformat(),
        rule_id=alert.rule_id,
        rule_name=alert.rule_name,
        severity=alert.severity.value,
        status=alert.status.value,
        threshold=alert.threshold,
    )


def _build_history_response(event: AlertHistoryEvent) -> AlertHistoryResponse:
    return AlertHistoryResponse(
        alert_id=event.alert_id,
        detail=event.detail,
        event_type=event.event_type.value,
        occurred_at=event.occurred_at.isoformat(),
    )


def _build_alert_detail_response(detail: AlertDetail) -> AlertDetailResponse:
    return AlertDetailResponse(
        history=[_build_history_response(event) for event in detail.history],
        record=_build_alert_response(detail.record),
    )


def _build_rule_catalog_response(catalog: AlertEngineCatalog) -> AlertEngineCatalogResponse:
    return AlertEngineCatalogResponse(
        engine=catalog.engine,
        metrics=[_build_rule_catalog_metric_response(metric) for metric in catalog.metrics],
    )


def _build_rule_catalog_metric_response(
    metric: AlertMetricCatalogEntry,
) -> AlertMetricCatalogEntryResponse:
    return AlertMetricCatalogEntryResponse(
        label=metric.label,
        metric_name=metric.metric_name,
        unit=metric.unit,
    )
