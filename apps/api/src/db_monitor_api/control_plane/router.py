from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from db_monitor_api.auth.domain import AuthContext, Permission
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    InstanceConnectionConfig,
    MonitoredInstance,
    SystemSetting,
)
from db_monitor_api.control_plane.service import AssetNotFoundError, AssetValidationError
from db_monitor_api.dependencies import get_runtime, require_permission_dependency
from db_monitor_api.runtime import AppRuntime

router = APIRouter()


class InstanceConnectionPayload(BaseModel):
    database: str = Field(
        description="MySQL database name, or Oracle DSN/service name when engine=oracle."
    )
    host: str
    password: str
    port: int = Field(
        default=3306,
        description="Explicit listener port. Oracle callers should provide 1521 or the real port.",
        ge=1,
        le=65535,
    )
    username: str


class CreateInstanceRequest(BaseModel):
    connection: InstanceConnectionPayload
    engine: DatabaseEngine
    environment: str
    labels: list[str] = Field(default_factory=list)
    name: str


class CreateMySQLInstanceRequest(BaseModel):
    connection: InstanceConnectionPayload
    environment: str
    labels: list[str] = Field(default_factory=list)
    name: str


class UpdateSettingRequest(BaseModel):
    value: str


class ValidationResponse(BaseModel):
    checked_at: str
    detail: str
    server_version: str | None
    status: str


class InstanceResponse(BaseModel):
    connection: dict[str, str | int]
    created_at: str
    engine: str
    environment: str
    instance_id: str
    labels: list[str]
    name: str
    validation: ValidationResponse


class SystemSettingResponse(BaseModel):
    key: str
    updated_at: str
    value: str


def build_control_plane_router() -> APIRouter:
    return router


@router.post("/control/instances", response_model=InstanceResponse, status_code=status.HTTP_201_CREATED)
def create_instance(
    payload: CreateInstanceRequest,
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_WRITE, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> InstanceResponse:
    return _create_instance_response(
        connection=payload.connection,
        context=context,
        engine=payload.engine,
        environment=payload.environment,
        labels=payload.labels,
        name=payload.name,
        runtime=runtime,
    )


@router.post(
    "/control/mysql-instances",
    response_model=InstanceResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_mysql_instance(
    payload: CreateMySQLInstanceRequest,
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_WRITE, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> InstanceResponse:
    return _create_instance_response(
        connection=payload.connection,
        context=context,
        engine=DatabaseEngine.MYSQL,
        environment=payload.environment,
        labels=payload.labels,
        name=payload.name,
        runtime=runtime,
    )


@router.get("/control/instances", response_model=list[InstanceResponse])
@router.get("/control/mysql-instances", response_model=list[InstanceResponse], include_in_schema=False)
def list_instances(
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_READ, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[InstanceResponse]:
    return [
        _build_instance_response(instance)
        for instance in runtime.asset_service.list_instances(
            organization_id=context.active_organization.organization_id
        )
    ]


@router.get("/control/instances/{instance_id}", response_model=InstanceResponse)
@router.get(
    "/control/mysql-instances/{instance_id}",
    response_model=InstanceResponse,
    include_in_schema=False,
)
def get_instance(
    instance_id: str,
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_READ, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> InstanceResponse:
    try:
        instance = runtime.asset_service.get_instance(
            instance_id=instance_id,
            organization_id=context.active_organization.organization_id,
        )
    except AssetNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return _build_instance_response(instance)


@router.post("/control/instances/{instance_id}/validate", response_model=InstanceResponse)
@router.post(
    "/control/mysql-instances/{instance_id}/validate",
    response_model=InstanceResponse,
    include_in_schema=False,
)
def validate_instance(
    instance_id: str,
    context: AuthContext = Depends(
        require_permission_dependency(Permission.INSTANCES_WRITE, "instances")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> InstanceResponse:
    try:
        instance = runtime.asset_service.validate_instance(
            actor_user_id=context.user.user_id,
            instance_id=instance_id,
            organization_id=context.active_organization.organization_id,
        )
    except AssetNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return _build_instance_response(instance)


@router.get("/control/settings", response_model=list[SystemSettingResponse])
def list_settings(
    context: AuthContext = Depends(
        require_permission_dependency(Permission.SETTINGS_READ, "settings")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> list[SystemSettingResponse]:
    return [
        _build_setting_response(setting)
        for setting in runtime.settings_service.list_settings(
            organization_id=context.active_organization.organization_id
        )
    ]


@router.put("/control/settings/{key}", response_model=SystemSettingResponse)
def update_setting(
    key: str,
    payload: UpdateSettingRequest,
    context: AuthContext = Depends(
        require_permission_dependency(Permission.SETTINGS_WRITE, "settings")
    ),
    runtime: AppRuntime = Depends(get_runtime),
) -> SystemSettingResponse:
    setting = runtime.settings_service.upsert_setting(
        actor_user_id=context.user.user_id,
        key=key,
        organization_id=context.active_organization.organization_id,
        value=payload.value,
    )
    return _build_setting_response(setting)


def _build_connection_config(payload: InstanceConnectionPayload) -> InstanceConnectionConfig:
    return InstanceConnectionConfig(
        database=payload.database,
        host=payload.host,
        password=payload.password,
        port=payload.port,
        username=payload.username,
    )


def _create_instance_response(
    *,
    connection: InstanceConnectionPayload,
    context: AuthContext,
    engine: DatabaseEngine,
    environment: str,
    labels: list[str],
    name: str,
    runtime: AppRuntime,
) -> InstanceResponse:
    try:
        instance = runtime.asset_service.create_instance(
            actor_user_id=context.user.user_id,
            connection=_build_connection_config(connection),
            engine=engine,
            environment=environment,
            labels=tuple(labels),
            name=name,
            organization_id=context.active_organization.organization_id,
        )
    except AssetValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    return _build_instance_response(instance)


def _build_instance_response(instance: MonitoredInstance) -> InstanceResponse:
    return InstanceResponse(
        connection={
            "database": instance.connection.database,
            "host": instance.connection.host,
            "port": instance.connection.port,
            "username": instance.connection.username,
        },
        created_at=instance.created_at.isoformat(),
        engine=instance.engine.value,
        environment=instance.environment,
        instance_id=instance.instance_id,
        labels=list(instance.labels),
        name=instance.name,
        validation=_build_validation_response(instance.validation),
    )


def _build_setting_response(setting: SystemSetting) -> SystemSettingResponse:
    return SystemSettingResponse(
        key=setting.key,
        updated_at=setting.updated_at.isoformat(),
        value=setting.value,
    )


def _build_validation_response(validation: ConnectionValidation) -> ValidationResponse:
    return ValidationResponse(
        checked_at=validation.checked_at.isoformat(),
        detail=validation.detail,
        server_version=validation.server_version,
        status=validation.status.value,
    )
