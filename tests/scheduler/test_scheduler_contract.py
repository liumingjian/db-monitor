from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    MySQLConnectionConfig,
    MySQLInstance,
    ValidationStatus,
)
from db_monitor_pipeline.domain import CollectionJob, INITIAL_COLLECTION_ATTEMPT


def test_collection_job_json_contract_round_trips() -> None:
    queued_at = utc_now()
    job = CollectionJob(
        attempt=INITIAL_COLLECTION_ATTEMPT,
        available_at=queued_at,
        connection=MySQLConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        engine=DatabaseEngine.MYSQL,
        environment="prod",
        instance_id="inst-123",
        labels=("primary", "critical"),
        name="prod-primary",
        queued_at=queued_at,
    )

    encoded = job.to_json()
    decoded = CollectionJob.from_json(encoded)

    assert decoded == job
    assert decoded.engine is DatabaseEngine.MYSQL


def test_scheduler_contract_starts_from_validated_mysql_instance() -> None:
    instance = MySQLInstance(
        connection=MySQLConnectionConfig(
            database="mysql",
            host="127.0.0.1",
            password="secret",
            port=3306,
            username="db_monitor",
        ),
        created_at=utc_now(),
        environment="prod",
        instance_id="inst-123",
        labels=("primary",),
        name="prod-primary",
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=utc_now(),
            detail="ok",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
        ),
    )

    assert instance.validation.status is ValidationStatus.PASSED
    assert instance.engine is DatabaseEngine.MYSQL
    assert instance.connection.host == "127.0.0.1"
