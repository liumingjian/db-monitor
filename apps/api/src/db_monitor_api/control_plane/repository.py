from collections.abc import Sequence
from dataclasses import replace
from typing import Protocol

from db_monitor_api.control_plane.domain import MonitoredInstance, SystemSetting


class ControlPlaneRepository(Protocol):
    def create_instance(self, instance: MonitoredInstance) -> None:
        ...

    def get_instance(
        self,
        instance_id: str,
        *,
        organization_id: str | None = None,
    ) -> MonitoredInstance | None:
        ...

    def list_instances(
        self,
        *,
        organization_id: str | None = None,
    ) -> tuple[MonitoredInstance, ...]:
        ...

    def upsert_instance(self, instance: MonitoredInstance) -> None:
        ...

    def list_settings(
        self,
        *,
        organization_id: str | None = None,
    ) -> tuple[SystemSetting, ...]:
        ...

    def upsert_setting(self, setting: SystemSetting) -> None:
        ...


class InMemoryControlPlaneRepository:
    def __init__(self) -> None:
        self._instances: dict[str, MonitoredInstance] = {}
        self._settings: dict[tuple[str, str], SystemSetting] = {}

    def create_instance(self, instance: MonitoredInstance) -> None:
        self._instances[instance.instance_id] = instance

    def get_instance(
        self,
        instance_id: str,
        *,
        organization_id: str | None = None,
    ) -> MonitoredInstance | None:
        instance = self._instances.get(instance_id)
        if organization_id is not None and instance is not None:
            if instance.organization_id != organization_id:
                return None
        return None if instance is None else replace(instance)

    def list_instances(
        self,
        *,
        organization_id: str | None = None,
    ) -> tuple[MonitoredInstance, ...]:
        sorted_instances: Sequence[MonitoredInstance] = sorted(
            (
                instance
                for instance in self._instances.values()
                if organization_id is None or instance.organization_id == organization_id
            ),
            key=lambda instance: instance.created_at,
        )
        return tuple(replace(instance) for instance in sorted_instances)

    def upsert_instance(self, instance: MonitoredInstance) -> None:
        self._instances[instance.instance_id] = instance

    def list_settings(
        self,
        *,
        organization_id: str | None = None,
    ) -> tuple[SystemSetting, ...]:
        sorted_settings: Sequence[SystemSetting] = sorted(
            (
                setting
                for setting in self._settings.values()
                if organization_id is None or setting.organization_id == organization_id
            ),
            key=lambda setting: (setting.organization_id, setting.key),
        )
        return tuple(replace(setting) for setting in sorted_settings)

    def upsert_setting(self, setting: SystemSetting) -> None:
        self._settings[(setting.organization_id, setting.key)] = setting
