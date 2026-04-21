from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    MySQLConnectionConfig,
    MySQLInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import InMemoryControlPlaneRepository
from db_monitor_pipeline.queue import InMemoryCollectionTaskQueue
from db_monitor_pipeline.scheduler import MetricsDispatchService


def test_scheduler_enqueues_only_validated_supported_instances() -> None:
    repository = InMemoryControlPlaneRepository()
    repository.create_instance(_build_instance(instance_id="inst-1", status=ValidationStatus.PASSED))
    repository.create_instance(
        _build_instance(
            engine=DatabaseEngine.ORACLE,
            instance_id="inst-2",
            status=ValidationStatus.PASSED,
        )
    )
    repository.create_instance(_build_instance(instance_id="inst-3", status=ValidationStatus.FAILED))
    queue = InMemoryCollectionTaskQueue()

    dispatched = MetricsDispatchService(
        control_plane_repository=repository,
        queue=queue,
    ).dispatch_collection_jobs()

    assert dispatched == 2
    assert queue.size() == 2
    first_job = queue.dequeue()
    second_job = queue.dequeue()

    assert first_job is not None
    assert second_job is not None
    assert (first_job.instance_id, second_job.instance_id) == ("inst-1", "inst-2")
    assert (first_job.engine, second_job.engine) == (
        DatabaseEngine.MYSQL,
        DatabaseEngine.ORACLE,
    )


def _build_instance(
    *,
    engine: DatabaseEngine = DatabaseEngine.MYSQL,
    instance_id: str,
    status: ValidationStatus,
) -> MySQLInstance:
    return MySQLInstance(
        connection=MySQLConnectionConfig(
            database="ORCLCDB" if engine is DatabaseEngine.ORACLE else "mysql",
            host="127.0.0.1",
            password="secret",
            port=1521 if engine is DatabaseEngine.ORACLE else 3306,
            username="system" if engine is DatabaseEngine.ORACLE else "db_monitor",
        ),
        created_at=utc_now(),
        engine=engine,
        environment="prod",
        instance_id=instance_id,
        labels=("primary",),
        name=instance_id,
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=utc_now(),
            detail="ok" if status is ValidationStatus.PASSED else "failed",
            server_version="8.4.0",
            status=status,
        ),
    )
