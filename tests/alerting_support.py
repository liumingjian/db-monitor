from fastapi import FastAPI

from db_monitor_api.alerting.notifier import InMemoryNotifier, Notifier
from db_monitor_api.alerting.repository import AlertingRepository, InMemoryAlertingRepository
from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_local_runtime
from db_monitor_api.control_plane.domain import MonitoredInstance
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from tests.analytics_support import build_instance
from tests.support import StaticMySQLConnectionValidator


def build_app(
    *,
    alerting_repository: AlertingRepository | None = None,
    instances: tuple[MonitoredInstance, ...] = (),
    instance_ids: tuple[str, ...] = (),
    notifier: Notifier | None = None,
) -> FastAPI:
    control_plane_repository = InMemoryControlPlaneRepository()
    for instance in instances:
        control_plane_repository.create_instance(instance)
    for instance_id in instance_ids:
        control_plane_repository.create_instance(
            build_instance(
                created_at=StaticMySQLConnectionValidator().next_result.checked_at,
                instance_id=instance_id,
                name=instance_id,
            )
        )
    return create_app(
        runtime=build_local_runtime(
            alerting_repository=alerting_repository or InMemoryAlertingRepository(),
            control_plane_repository=control_plane_repository,
            mysql_validator=StaticMySQLConnectionValidator(),
            notifier=notifier or InMemoryNotifier(),
        )
    )
