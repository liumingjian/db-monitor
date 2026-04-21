from db_monitor_api.settings import ApiSettings, ClickHouseSettings, RuntimeMode
from db_monitor_pipeline.process_settings import SchedulerProcessSettings, WorkerProcessSettings
from db_monitor_schema.clickhouse import bootstrap_clickhouse_schema, verify_clickhouse_schema
from db_monitor_schema.contract import SchemaVersion
from db_monitor_schema.postgres import bootstrap_postgres_schema, verify_postgres_schema


def bootstrap_api_runtime_schema(settings: ApiSettings) -> tuple[SchemaVersion, ...]:
    if settings.runtime_mode is RuntimeMode.LOCAL:
        raise RuntimeError("Local runtime does not use persistent schema bootstrap.")
    if settings.postgres_dsn is None or settings.clickhouse is None:
        raise RuntimeError("Postgres runtime requires PostgreSQL and ClickHouse settings.")
    return (
        bootstrap_postgres_schema(postgres_dsn=settings.postgres_dsn),
        bootstrap_clickhouse_schema(settings=settings.clickhouse),
    )


def verify_api_runtime_schema(
    *,
    analytics_repository: object | None,
    clickhouse: ClickHouseSettings | None,
    postgres_dsn: str,
) -> tuple[SchemaVersion, ...]:
    results = [verify_postgres_schema(postgres_dsn=postgres_dsn)]
    if analytics_repository is None:
        if clickhouse is None:
            raise RuntimeError(
                "ClickHouse settings are required when no analytics repository is injected."
            )
        results.append(verify_clickhouse_schema(settings=clickhouse))
    return tuple(results)


def verify_scheduler_process_schema(settings: SchedulerProcessSettings) -> SchemaVersion:
    return verify_postgres_schema(postgres_dsn=settings.postgres_dsn)


def verify_worker_process_schema(settings: WorkerProcessSettings) -> SchemaVersion:
    return verify_clickhouse_schema(settings=settings.clickhouse)
