from dataclasses import dataclass, replace
import secrets

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    InstanceConnectionConfig,
    MonitoredInstance,
    SystemSetting,
    ValidationStatus,
)
from db_monitor_api.control_plane.mysql_validation import MySQLConnectionValidator
from db_monitor_api.control_plane.oracle_validation import OracleConnectionValidator
from db_monitor_api.control_plane.repository import ControlPlaneRepository


class AssetNotFoundError(Exception):
    pass


class AssetValidationError(Exception):
    pass


@dataclass(frozen=True)
class AssetService:
    audit_service: AuditService
    mysql_validator: MySQLConnectionValidator
    oracle_validator: OracleConnectionValidator
    repository: ControlPlaneRepository

    def create_instance(
        self,
        *,
        actor_user_id: str,
        engine: DatabaseEngine,
        connection: InstanceConnectionConfig,
        environment: str,
        labels: tuple[str, ...],
        name: str,
        organization_id: str,
    ) -> MonitoredInstance:
        validation = self._validate_connection(engine=engine, connection=connection)
        if validation.status is ValidationStatus.FAILED:
            self._record_asset_audit(actor_user_id=actor_user_id, outcome="failed")
            raise AssetValidationError(validation.detail)
        instance = MonitoredInstance(
            connection=connection,
            created_at=utc_now(),
            engine=engine,
            environment=environment,
            instance_id=f"inst-{secrets.token_hex(6)}",
            labels=labels,
            name=name,
            organization_id=organization_id,
            validation=validation,
        )
        self.repository.create_instance(instance)
        self._record_asset_audit(actor_user_id=actor_user_id, outcome="allowed")
        return instance

    def get_instance(self, *, instance_id: str, organization_id: str) -> MonitoredInstance:
        instance = self.repository.get_instance(
            instance_id,
            organization_id=organization_id,
        )
        if instance is None:
            raise AssetNotFoundError(f"Unknown instance: {instance_id}")
        return instance

    def list_instances(self, *, organization_id: str) -> tuple[MonitoredInstance, ...]:
        return self.repository.list_instances(organization_id=organization_id)

    def validate_instance(
        self,
        *,
        actor_user_id: str,
        instance_id: str,
        organization_id: str,
    ) -> MonitoredInstance:
        instance = self.get_instance(
            instance_id=instance_id,
            organization_id=organization_id,
        )
        validation = self._validate_connection(
            engine=instance.engine,
            connection=instance.connection,
        )
        updated_instance = replace(instance, validation=validation)
        self.repository.upsert_instance(updated_instance)
        self.audit_service.record(
            action="instances.validate",
            actor_user_id=actor_user_id,
            outcome="allowed" if validation.status is ValidationStatus.PASSED else "failed",
            resource="instance",
        )
        return updated_instance

    def _record_asset_audit(self, *, actor_user_id: str, outcome: str) -> None:
        self.audit_service.record(
            action="instances.create",
            actor_user_id=actor_user_id,
            outcome=outcome,
            resource="instance",
        )

    def _validate_connection(
        self,
        *,
        engine: DatabaseEngine,
        connection: InstanceConnectionConfig,
    ) -> ConnectionValidation:
        if engine is DatabaseEngine.MYSQL:
            return self.mysql_validator.validate(connection)
        if engine is DatabaseEngine.ORACLE:
            return self.oracle_validator.validate(connection)
        raise AssetValidationError(f"Unsupported engine for validation: {engine.value}")


@dataclass(frozen=True)
class SettingsService:
    audit_service: AuditService
    repository: ControlPlaneRepository

    def list_settings(self, *, organization_id: str) -> tuple[SystemSetting, ...]:
        return self.repository.list_settings(organization_id=organization_id)

    def upsert_setting(
        self,
        *,
        actor_user_id: str,
        key: str,
        organization_id: str,
        value: str,
    ) -> SystemSetting:
        setting = SystemSetting(
            key=key,
            organization_id=organization_id,
            updated_at=utc_now(),
            value=value,
        )
        self.repository.upsert_setting(setting)
        self.audit_service.record(
            action="settings.write",
            actor_user_id=actor_user_id,
            outcome="allowed",
            resource="settings",
        )
        return setting
