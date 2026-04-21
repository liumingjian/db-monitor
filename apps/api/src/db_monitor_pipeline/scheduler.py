from dataclasses import dataclass

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import DatabaseEngine, MonitoredInstance, ValidationStatus
from db_monitor_api.control_plane.repository import ControlPlaneRepository
from db_monitor_pipeline.domain import CollectionJob, INITIAL_COLLECTION_ATTEMPT
from db_monitor_pipeline.queue import CollectionTaskQueue

SUPPORTED_COLLECTION_ENGINES = frozenset({DatabaseEngine.MYSQL, DatabaseEngine.ORACLE})


@dataclass(frozen=True)
class MetricsDispatchService:
    control_plane_repository: ControlPlaneRepository
    queue: CollectionTaskQueue

    def dispatch_collection_jobs(self) -> int:
        dispatched = 0
        for instance in self.control_plane_repository.list_instances(organization_id=None):
            if not _is_dispatchable_instance(instance):
                continue
            if self.queue.enqueue(_build_job(instance)):
                dispatched += 1
        return dispatched


def _build_job(instance: MonitoredInstance) -> CollectionJob:
    queued_at = utc_now()
    return CollectionJob(
        attempt=INITIAL_COLLECTION_ATTEMPT,
        available_at=queued_at,
        connection=instance.connection,
        engine=instance.engine,
        environment=instance.environment,
        instance_id=instance.instance_id,
        labels=instance.labels,
        name=instance.name,
        queued_at=queued_at,
    )


def _is_dispatchable_instance(instance: MonitoredInstance) -> bool:
    if instance.validation.status is not ValidationStatus.PASSED:
        return False
    return instance.engine in SUPPORTED_COLLECTION_ENGINES
