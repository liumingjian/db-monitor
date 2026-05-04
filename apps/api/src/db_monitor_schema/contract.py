from dataclasses import dataclass

CLICKHOUSE_SCHEMA_SCOPE = "clickhouse"
CLICKHOUSE_SCHEMA_VERSION = 4
CLICKHOUSE_SCHEMA_VERSION_TABLE = "schema_version"
POSTGRES_SCHEMA_SCOPE = "postgres"
POSTGRES_SCHEMA_VERSION = 11
POSTGRES_SCHEMA_VERSION_TABLE = "schema_version"


@dataclass(frozen=True)
class SchemaVersion:
    backend: str
    scope: str
    version: int
