from datetime import UTC, datetime
import json
import re
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from db_monitor_api.settings import ClickHouseSettings
from db_monitor_pipeline.sink import (
    CLICKHOUSE_METRICS_TABLE,
    CLICKHOUSE_MYSQL_PROCESSLIST_TABLE,
    CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE,
    CLICKHOUSE_ORACLE_TABLESPACES_TABLE,
)
from db_monitor_schema.contract import (
    CLICKHOUSE_SCHEMA_SCOPE,
    CLICKHOUSE_SCHEMA_VERSION,
    CLICKHOUSE_SCHEMA_VERSION_TABLE,
    SchemaVersion,
)

CLICKHOUSE_REQUIRED_TABLES = (
    CLICKHOUSE_METRICS_TABLE,
    CLICKHOUSE_MYSQL_PROCESSLIST_TABLE,
    CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE,
    CLICKHOUSE_ORACLE_TABLESPACES_TABLE,
    CLICKHOUSE_SCHEMA_VERSION_TABLE,
)
CLICKHOUSE_BOOTSTRAP_COMMAND = "uv run python -m db_monitor_schema bootstrap-clickhouse"
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_CREATE_DATABASE_SQL = "CREATE DATABASE IF NOT EXISTS {database}"
_CREATE_METRICS_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {CLICKHOUSE_METRICS_TABLE} (
    engine String,
    instance_id String,
    environment String,
    labels_json String,
    metric_name String,
    metric_kind String,
    metric_value Float64,
    collected_at DateTime64(3, 'UTC')
) ENGINE = MergeTree
ORDER BY (engine, instance_id, metric_name, collected_at)
"""
_CREATE_VERSION_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {CLICKHOUSE_SCHEMA_VERSION_TABLE} (
    scope String,
    version UInt32,
    updated_at DateTime64(3, 'UTC')
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY scope
"""
_CREATE_MYSQL_PROCESSLIST_SQL = f"""
CREATE TABLE IF NOT EXISTS {CLICKHOUSE_MYSQL_PROCESSLIST_TABLE} (
    organization_id String,
    instance_id String,
    collected_at DateTime64(3, 'UTC'),
    process_id UInt64,
    user String,
    host String,
    db String,
    command LowCardinality(String),
    time_seconds UInt32,
    state LowCardinality(String),
    info String,
    trx_started_at Nullable(DateTime64(3, 'UTC'))
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(collected_at)
ORDER BY (instance_id, collected_at, process_id)
TTL toDateTime(collected_at) + INTERVAL 7 DAY
"""
_CREATE_MYSQL_SLOW_QUERY_EVENTS_SQL = f"""
CREATE TABLE IF NOT EXISTS {CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE} (
    organization_id String,
    instance_id String,
    collected_at DateTime64(3, 'UTC'),
    event_id UInt64,
    thread_id UInt64,
    user String,
    host String,
    schema_name String,
    digest String,
    digest_text String,
    sql_text String,
    timer_wait_ms Float64,
    rows_examined UInt64,
    rows_sent UInt64,
    rows_affected UInt64,
    errors UInt32,
    started_at DateTime64(3, 'UTC')
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(started_at)
ORDER BY (instance_id, started_at, event_id)
TTL toDateTime(collected_at) + INTERVAL 7 DAY
"""
_CREATE_ORACLE_TABLESPACES_SQL = f"""
CREATE TABLE IF NOT EXISTS {CLICKHOUSE_ORACLE_TABLESPACES_TABLE} (
    organization_id String,
    instance_id String,
    collected_at DateTime64(3, 'UTC'),
    tablespace_name String,
    status LowCardinality(String),
    used_bytes UInt64,
    total_bytes UInt64,
    used_rate_percent Float64,
    autoextensible UInt8
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(collected_at)
ORDER BY (instance_id, collected_at, tablespace_name)
TTL toDateTime(collected_at) + INTERVAL 30 DAY
"""


def bootstrap_clickhouse_schema(*, settings: ClickHouseSettings) -> SchemaVersion:
    database = _validated_database_name(settings.database)
    _execute_clickhouse_query(query=_CREATE_DATABASE_SQL.format(database=database), settings=settings)
    _execute_clickhouse_query(
        database=database,
        query=_CREATE_VERSION_TABLE_SQL,
        settings=settings,
    )
    _execute_clickhouse_query(
        database=database,
        query=_CREATE_METRICS_TABLE_SQL,
        settings=settings,
    )
    _execute_clickhouse_query(
        database=database,
        query=_CREATE_MYSQL_PROCESSLIST_SQL,
        settings=settings,
    )
    _execute_clickhouse_query(
        database=database,
        query=_CREATE_MYSQL_SLOW_QUERY_EVENTS_SQL,
        settings=settings,
    )
    _execute_clickhouse_query(
        database=database,
        query=_CREATE_ORACLE_TABLESPACES_SQL,
        settings=settings,
    )
    _execute_clickhouse_query(
        database=database,
        payload=json.dumps(
            {
                "scope": CLICKHOUSE_SCHEMA_SCOPE,
                "updated_at": _format_clickhouse_datetime(datetime.now(tz=UTC)),
                "version": CLICKHOUSE_SCHEMA_VERSION,
            }
        ).encode("utf-8"),
        query=f"INSERT INTO {CLICKHOUSE_SCHEMA_VERSION_TABLE} FORMAT JSONEachRow",
        settings=settings,
    )
    return SchemaVersion(
        backend="clickhouse",
        scope=CLICKHOUSE_SCHEMA_SCOPE,
        version=CLICKHOUSE_SCHEMA_VERSION,
    )


def read_clickhouse_schema_version(*, settings: ClickHouseSettings) -> SchemaVersion | None:
    database = _validated_database_name(settings.database)
    if not _clickhouse_database_exists(settings=settings):
        return None
    if _missing_clickhouse_tables(settings=settings):
        return None
    rows = _execute_clickhouse_query(
        database=database,
        query=(
            f"SELECT version FROM {CLICKHOUSE_SCHEMA_VERSION_TABLE} "
            f"WHERE scope = {_quote_string(CLICKHOUSE_SCHEMA_SCOPE)} "
            "ORDER BY updated_at DESC LIMIT 1 FORMAT JSONEachRow"
        ),
        settings=settings,
    )
    if not rows:
        return None
    return SchemaVersion(
        backend="clickhouse",
        scope=CLICKHOUSE_SCHEMA_SCOPE,
        version=int(str(rows[0]["version"])),
    )


def verify_clickhouse_schema(*, settings: ClickHouseSettings) -> SchemaVersion:
    database = _validated_database_name(settings.database)
    if not _clickhouse_database_exists(settings=settings):
        raise RuntimeError(
            "ClickHouse database is not bootstrapped. "
            f"Missing database: {database}. Run `{CLICKHOUSE_BOOTSTRAP_COMMAND}`."
        )
    missing_tables = _missing_clickhouse_tables(settings=settings)
    if missing_tables:
        missing_table_names = ", ".join(missing_tables)
        raise RuntimeError(
            "ClickHouse schema is not bootstrapped. "
            f"Missing tables: {missing_table_names}. "
            f"Run `{CLICKHOUSE_BOOTSTRAP_COMMAND}`."
        )
    version = read_clickhouse_schema_version(settings=settings)
    if version is None:
        raise RuntimeError(
            "ClickHouse schema version row is missing. "
            f"Run `{CLICKHOUSE_BOOTSTRAP_COMMAND}`."
        )
    if version.version != CLICKHOUSE_SCHEMA_VERSION:
        raise RuntimeError(
            "Unsupported ClickHouse schema version "
            f"{version.version}. Expected {CLICKHOUSE_SCHEMA_VERSION}."
        )
    return version


def _clickhouse_database_exists(*, settings: ClickHouseSettings) -> bool:
    rows = _execute_clickhouse_query(
        query=(
            "SELECT name FROM system.databases "
            f"WHERE name = {_quote_string(_validated_database_name(settings.database))} "
            "FORMAT JSONEachRow"
        ),
        settings=settings,
    )
    return len(rows) == 1


def _missing_clickhouse_tables(*, settings: ClickHouseSettings) -> tuple[str, ...]:
    database = _validated_database_name(settings.database)
    rows = _execute_clickhouse_query(
        database=database,
        query=(
            "SELECT name FROM system.tables "
            f"WHERE database = {_quote_string(database)} "
            f"AND name IN ({_join_string_literals(CLICKHOUSE_REQUIRED_TABLES)}) "
            "FORMAT JSONEachRow"
        ),
        settings=settings,
    )
    existing_tables = {str(row["name"]) for row in rows}
    return tuple(
        table_name for table_name in CLICKHOUSE_REQUIRED_TABLES if table_name not in existing_tables
    )


def _execute_clickhouse_query(
    *,
    database: str | None = None,
    payload: bytes = b"",
    query: str,
    settings: ClickHouseSettings,
) -> list[dict[str, object]]:
    params = {"query": query}
    if database is not None:
        params["database"] = database
    request = Request(
        url=f"{settings.endpoint.rstrip('/')}/?{urlencode(params)}",
        data=payload,
        headers={
            "X-ClickHouse-Key": settings.password,
            "X-ClickHouse-User": settings.username,
        },
        method="POST",
    )
    try:
        with urlopen(request) as response:
            body = response.read().decode("utf-8")
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"ClickHouse request failed with status {error.code}: {detail}"
        ) from error
    return [json.loads(line) for line in body.splitlines() if line]


def _format_clickhouse_datetime(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _join_string_literals(values: tuple[str, ...]) -> str:
    return ", ".join(_quote_string(value) for value in values)


def _quote_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _validated_database_name(value: str) -> str:
    if not _IDENTIFIER_PATTERN.fullmatch(value):
        raise RuntimeError(f"Unsupported ClickHouse database identifier: {value}")
    return value
