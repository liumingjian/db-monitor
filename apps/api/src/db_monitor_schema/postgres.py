from datetime import UTC, datetime
from typing import Final, cast

import psycopg

from db_monitor_schema.contract import (
    POSTGRES_SCHEMA_SCOPE,
    POSTGRES_SCHEMA_VERSION,
    POSTGRES_SCHEMA_VERSION_TABLE,
    SchemaVersion,
)

DEFAULT_ORGANIZATION_ID = "org-internal"
DEFAULT_ORGANIZATION_NAME = "Internal Operations"
DEFAULT_ORGANIZATION_SLUG = "internal-ops"
POSTGRES_REQUIRED_TABLES: Final[tuple[str, ...]] = (
    POSTGRES_SCHEMA_VERSION_TABLE,
    "alert_history",
    "alert_records",
    "alert_rules",
    "control_mysql_instances",
    "control_settings",
    "organization_memberships",
    "organizations",
)
POSTGRES_BOOTSTRAP_COMMAND = "uv run python -m db_monitor_schema bootstrap-postgres"
_POSTGRES_REQUIRED_TABLE_NAMES = ", ".join(f"'{table_name}'" for table_name in POSTGRES_REQUIRED_TABLES)
_CREATE_ORGANIZATIONS_SQL = """
CREATE TABLE IF NOT EXISTS organizations (
    organization_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL
)
"""
_CREATE_ORGANIZATION_MEMBERSHIPS_SQL = """
CREATE TABLE IF NOT EXISTS organization_memberships (
    organization_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    roles_json TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (organization_id, user_id),
    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
)
"""
_CREATE_CONTROL_MYSQL_INSTANCES_SQL = """
CREATE TABLE IF NOT EXISTS control_mysql_instances (
    instance_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    engine TEXT NOT NULL,
    name TEXT NOT NULL,
    environment TEXT NOT NULL,
    labels_json TEXT NOT NULL,
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    database_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    validation_status TEXT NOT NULL,
    validation_detail TEXT NOT NULL,
    validation_checked_at TIMESTAMPTZ NOT NULL,
    validation_server_version TEXT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
)
"""
_CREATE_CONTROL_SETTINGS_SQL = """
CREATE TABLE IF NOT EXISTS control_settings (
    organization_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (organization_id, key),
    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
)
"""
_CREATE_ALERT_RULES_SQL = """
CREATE TABLE IF NOT EXISTS alert_rules (
    rule_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    engine TEXT NOT NULL,
    name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    operator TEXT NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    severity TEXT NOT NULL,
    enabled BOOLEAN NOT NULL,
    instance_ids_json TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
)
"""
_CREATE_ALERT_RECORDS_SQL = """
CREATE TABLE IF NOT EXISTS alert_records (
    alert_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    engine TEXT NOT NULL,
    instance_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    current_value DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    opened_at TIMESTAMPTZ NOT NULL,
    last_evaluated_at TIMESTAMPTZ NOT NULL,
    acknowledged_at TIMESTAMPTZ NULL,
    acknowledged_by_user_id TEXT NULL,
    owner_user_id TEXT NULL,
    owner_assigned_at TIMESTAMPTZ NULL,
    resolved_at TIMESTAMPTZ NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
)
"""
_CREATE_ALERT_HISTORY_SQL = """
CREATE TABLE IF NOT EXISTS alert_history (
    history_id BIGSERIAL PRIMARY KEY,
    alert_id TEXT NOT NULL,
    organization_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    detail TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
)
"""
_CREATE_VERSION_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {POSTGRES_SCHEMA_VERSION_TABLE} (
    scope TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
)
"""
_UPSERT_VERSION_SQL = f"""
INSERT INTO {POSTGRES_SCHEMA_VERSION_TABLE} (scope, version, updated_at)
VALUES (%s, %s, %s)
ON CONFLICT (scope) DO UPDATE SET
    version = EXCLUDED.version,
    updated_at = EXCLUDED.updated_at
"""
_SELECT_VERSION_SQL = f"SELECT version FROM {POSTGRES_SCHEMA_VERSION_TABLE} WHERE scope = %s"
_SELECT_TABLES_SQL = f"""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ({_POSTGRES_REQUIRED_TABLE_NAMES})
"""
_SEED_DEFAULT_ORGANIZATION_SQL = """
INSERT INTO organizations (organization_id, name, slug, created_at)
VALUES (%s, %s, %s, %s)
ON CONFLICT (organization_id) DO NOTHING
"""
_MIGRATE_CONTROL_MYSQL_INSTANCES_ORGANIZATION_COLUMN_SQL = """
ALTER TABLE control_mysql_instances
ADD COLUMN IF NOT EXISTS organization_id TEXT
"""
_BACKFILL_CONTROL_MYSQL_INSTANCES_ORGANIZATION_SQL = """
UPDATE control_mysql_instances
SET organization_id = %s
WHERE organization_id IS NULL
"""
_SET_CONTROL_MYSQL_INSTANCES_ORGANIZATION_NOT_NULL_SQL = """
ALTER TABLE control_mysql_instances
ALTER COLUMN organization_id SET NOT NULL
"""
_ENSURE_CONTROL_MYSQL_INSTANCES_ORGANIZATION_FK_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'control_mysql_instances'::regclass
          AND conname = 'control_mysql_instances_organization_id_fkey'
    ) THEN
        ALTER TABLE control_mysql_instances
            ADD CONSTRAINT control_mysql_instances_organization_id_fkey
            FOREIGN KEY (organization_id) REFERENCES organizations (organization_id);
    END IF;
END $$;
"""
_MIGRATE_CONTROL_SETTINGS_ORGANIZATION_COLUMN_SQL = """
ALTER TABLE control_settings
ADD COLUMN IF NOT EXISTS organization_id TEXT
"""
_BACKFILL_CONTROL_SETTINGS_ORGANIZATION_SQL = """
UPDATE control_settings
SET organization_id = %s
WHERE organization_id IS NULL
"""
_SET_CONTROL_SETTINGS_ORGANIZATION_NOT_NULL_SQL = """
ALTER TABLE control_settings
ALTER COLUMN organization_id SET NOT NULL
"""
_ENSURE_CONTROL_SETTINGS_PRIMARY_KEY_SQL = """
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'control_settings'::regclass
          AND conname = 'control_settings_pkey'
          AND pg_get_constraintdef(oid) <> 'PRIMARY KEY (organization_id, key)'
    ) THEN
        ALTER TABLE control_settings DROP CONSTRAINT control_settings_pkey;
    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'control_settings'::regclass
          AND conname = 'control_settings_pkey'
          AND pg_get_constraintdef(oid) = 'PRIMARY KEY (organization_id, key)'
    ) THEN
        ALTER TABLE control_settings
            ADD CONSTRAINT control_settings_pkey PRIMARY KEY (organization_id, key);
    END IF;
END $$;
"""
_ENSURE_CONTROL_SETTINGS_ORGANIZATION_FK_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'control_settings'::regclass
          AND conname = 'control_settings_organization_id_fkey'
    ) THEN
        ALTER TABLE control_settings
            ADD CONSTRAINT control_settings_organization_id_fkey
            FOREIGN KEY (organization_id) REFERENCES organizations (organization_id);
    END IF;
END $$;
"""
_MIGRATE_ALERT_RULES_ORGANIZATION_COLUMN_SQL = """
ALTER TABLE alert_rules
ADD COLUMN IF NOT EXISTS organization_id TEXT
"""
_BACKFILL_ALERT_RULES_ORGANIZATION_SQL = """
UPDATE alert_rules
SET organization_id = %s
WHERE organization_id IS NULL
"""
_SET_ALERT_RULES_ORGANIZATION_NOT_NULL_SQL = """
ALTER TABLE alert_rules
ALTER COLUMN organization_id SET NOT NULL
"""
_ENSURE_ALERT_RULES_ORGANIZATION_FK_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'alert_rules'::regclass
          AND conname = 'alert_rules_organization_id_fkey'
    ) THEN
        ALTER TABLE alert_rules
            ADD CONSTRAINT alert_rules_organization_id_fkey
            FOREIGN KEY (organization_id) REFERENCES organizations (organization_id);
    END IF;
END $$;
"""
_MIGRATE_ALERT_RULES_ENGINE_COLUMN_SQL = """
ALTER TABLE alert_rules
ADD COLUMN IF NOT EXISTS engine TEXT
"""
_BACKFILL_ALERT_RULES_ENGINE_SQL = """
UPDATE alert_rules
SET engine = %s
WHERE engine IS NULL
"""
_SET_ALERT_RULES_ENGINE_NOT_NULL_SQL = """
ALTER TABLE alert_rules
ALTER COLUMN engine SET NOT NULL
"""
_MIGRATE_ALERT_RECORDS_ORGANIZATION_COLUMN_SQL = """
ALTER TABLE alert_records
ADD COLUMN IF NOT EXISTS organization_id TEXT
"""
_BACKFILL_ALERT_RECORDS_ORGANIZATION_SQL = """
UPDATE alert_records
SET organization_id = %s
WHERE organization_id IS NULL
"""
_SET_ALERT_RECORDS_ORGANIZATION_NOT_NULL_SQL = """
ALTER TABLE alert_records
ALTER COLUMN organization_id SET NOT NULL
"""
_ENSURE_ALERT_RECORDS_ORGANIZATION_FK_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'alert_records'::regclass
          AND conname = 'alert_records_organization_id_fkey'
    ) THEN
        ALTER TABLE alert_records
            ADD CONSTRAINT alert_records_organization_id_fkey
            FOREIGN KEY (organization_id) REFERENCES organizations (organization_id);
    END IF;
END $$;
"""
_MIGRATE_ALERT_RECORDS_ENGINE_COLUMN_SQL = """
ALTER TABLE alert_records
ADD COLUMN IF NOT EXISTS engine TEXT
"""
_BACKFILL_ALERT_RECORDS_ENGINE_SQL = """
UPDATE alert_records
SET engine = %s
WHERE engine IS NULL
"""
_SET_ALERT_RECORDS_ENGINE_NOT_NULL_SQL = """
ALTER TABLE alert_records
ALTER COLUMN engine SET NOT NULL
"""
_MIGRATE_ALERT_HISTORY_ORGANIZATION_COLUMN_SQL = """
ALTER TABLE alert_history
ADD COLUMN IF NOT EXISTS organization_id TEXT
"""
_BACKFILL_ALERT_HISTORY_ORGANIZATION_SQL = """
UPDATE alert_history
SET organization_id = %s
WHERE organization_id IS NULL
"""
_SET_ALERT_HISTORY_ORGANIZATION_NOT_NULL_SQL = """
ALTER TABLE alert_history
ALTER COLUMN organization_id SET NOT NULL
"""
_ENSURE_ALERT_HISTORY_ORGANIZATION_FK_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'alert_history'::regclass
          AND conname = 'alert_history_organization_id_fkey'
    ) THEN
        ALTER TABLE alert_history
            ADD CONSTRAINT alert_history_organization_id_fkey
            FOREIGN KEY (organization_id) REFERENCES organizations (organization_id);
    END IF;
END $$;
"""


def bootstrap_postgres_schema(*, postgres_dsn: str) -> SchemaVersion:
    updated_at = datetime.now(tz=UTC)
    with psycopg.connect(postgres_dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute(_CREATE_VERSION_TABLE_SQL)
            cursor.execute(_CREATE_ORGANIZATIONS_SQL)
            cursor.execute(_CREATE_ORGANIZATION_MEMBERSHIPS_SQL)
            cursor.execute(
                _SEED_DEFAULT_ORGANIZATION_SQL,
                (
                    DEFAULT_ORGANIZATION_ID,
                    DEFAULT_ORGANIZATION_NAME,
                    DEFAULT_ORGANIZATION_SLUG,
                    updated_at,
                ),
            )
            cursor.execute(_CREATE_CONTROL_MYSQL_INSTANCES_SQL)
            cursor.execute(_MIGRATE_CONTROL_MYSQL_INSTANCES_ORGANIZATION_COLUMN_SQL)
            cursor.execute(
                _BACKFILL_CONTROL_MYSQL_INSTANCES_ORGANIZATION_SQL,
                (DEFAULT_ORGANIZATION_ID,),
            )
            cursor.execute(_SET_CONTROL_MYSQL_INSTANCES_ORGANIZATION_NOT_NULL_SQL)
            cursor.execute(_ENSURE_CONTROL_MYSQL_INSTANCES_ORGANIZATION_FK_SQL)
            cursor.execute(_CREATE_CONTROL_SETTINGS_SQL)
            cursor.execute(_MIGRATE_CONTROL_SETTINGS_ORGANIZATION_COLUMN_SQL)
            cursor.execute(
                _BACKFILL_CONTROL_SETTINGS_ORGANIZATION_SQL,
                (DEFAULT_ORGANIZATION_ID,),
            )
            cursor.execute(_SET_CONTROL_SETTINGS_ORGANIZATION_NOT_NULL_SQL)
            cursor.execute(_ENSURE_CONTROL_SETTINGS_PRIMARY_KEY_SQL)
            cursor.execute(_ENSURE_CONTROL_SETTINGS_ORGANIZATION_FK_SQL)
            cursor.execute(_CREATE_ALERT_RULES_SQL)
            cursor.execute(_MIGRATE_ALERT_RULES_ORGANIZATION_COLUMN_SQL)
            cursor.execute(
                _BACKFILL_ALERT_RULES_ORGANIZATION_SQL,
                (DEFAULT_ORGANIZATION_ID,),
            )
            cursor.execute(_SET_ALERT_RULES_ORGANIZATION_NOT_NULL_SQL)
            cursor.execute(_ENSURE_ALERT_RULES_ORGANIZATION_FK_SQL)
            cursor.execute(_MIGRATE_ALERT_RULES_ENGINE_COLUMN_SQL)
            cursor.execute(_BACKFILL_ALERT_RULES_ENGINE_SQL, ("mysql",))
            cursor.execute(_SET_ALERT_RULES_ENGINE_NOT_NULL_SQL)
            cursor.execute(_CREATE_ALERT_RECORDS_SQL)
            cursor.execute(_MIGRATE_ALERT_RECORDS_ORGANIZATION_COLUMN_SQL)
            cursor.execute(
                _BACKFILL_ALERT_RECORDS_ORGANIZATION_SQL,
                (DEFAULT_ORGANIZATION_ID,),
            )
            cursor.execute(_SET_ALERT_RECORDS_ORGANIZATION_NOT_NULL_SQL)
            cursor.execute(_ENSURE_ALERT_RECORDS_ORGANIZATION_FK_SQL)
            cursor.execute(_MIGRATE_ALERT_RECORDS_ENGINE_COLUMN_SQL)
            cursor.execute(_BACKFILL_ALERT_RECORDS_ENGINE_SQL, ("mysql",))
            cursor.execute(_SET_ALERT_RECORDS_ENGINE_NOT_NULL_SQL)
            cursor.execute(_CREATE_ALERT_HISTORY_SQL)
            cursor.execute(_MIGRATE_ALERT_HISTORY_ORGANIZATION_COLUMN_SQL)
            cursor.execute(
                _BACKFILL_ALERT_HISTORY_ORGANIZATION_SQL,
                (DEFAULT_ORGANIZATION_ID,),
            )
            cursor.execute(_SET_ALERT_HISTORY_ORGANIZATION_NOT_NULL_SQL)
            cursor.execute(_ENSURE_ALERT_HISTORY_ORGANIZATION_FK_SQL)
            cursor.execute(
                _UPSERT_VERSION_SQL,
                (POSTGRES_SCHEMA_SCOPE, POSTGRES_SCHEMA_VERSION, updated_at),
            )
    return SchemaVersion(
        backend="postgresql",
        scope=POSTGRES_SCHEMA_SCOPE,
        version=POSTGRES_SCHEMA_VERSION,
    )


def read_postgres_schema_version(*, postgres_dsn: str) -> SchemaVersion | None:
    with psycopg.connect(postgres_dsn) as connection:
        with connection.cursor() as cursor:
            if _missing_postgres_tables(cursor):
                return None
            cursor.execute(_SELECT_VERSION_SQL, (POSTGRES_SCHEMA_SCOPE,))
            row = cast(tuple[object, ...] | None, cursor.fetchone())
    if row is None:
        return None
    return SchemaVersion(
        backend="postgresql",
        scope=POSTGRES_SCHEMA_SCOPE,
        version=int(str(row[0])),
    )


def verify_postgres_schema(*, postgres_dsn: str) -> SchemaVersion:
    with psycopg.connect(postgres_dsn) as connection:
        with connection.cursor() as cursor:
            missing_tables = _missing_postgres_tables(cursor)
            if missing_tables:
                missing_table_names = ", ".join(missing_tables)
                raise RuntimeError(
                    "PostgreSQL schema is not bootstrapped. "
                    f"Missing tables: {missing_table_names}. "
                    f"Run `{POSTGRES_BOOTSTRAP_COMMAND}`."
                )
            cursor.execute(_SELECT_VERSION_SQL, (POSTGRES_SCHEMA_SCOPE,))
            row = cast(tuple[object, ...] | None, cursor.fetchone())
    if row is None:
        raise RuntimeError(
            "PostgreSQL schema version row is missing. "
            f"Run `{POSTGRES_BOOTSTRAP_COMMAND}`."
        )
    version = int(str(row[0]))
    if version != POSTGRES_SCHEMA_VERSION:
        raise RuntimeError(
            "Unsupported PostgreSQL schema version "
            f"{version}. Expected {POSTGRES_SCHEMA_VERSION}."
        )
    return SchemaVersion(
        backend="postgresql",
        scope=POSTGRES_SCHEMA_SCOPE,
        version=version,
    )


def _missing_postgres_tables(cursor: psycopg.Cursor[object]) -> tuple[str, ...]:
    cursor.execute(_SELECT_TABLES_SQL)
    rows = cast(list[tuple[object, ...]], cursor.fetchall())
    existing_tables = {str(row[0]) for row in rows}
    return tuple(
        table_name for table_name in POSTGRES_REQUIRED_TABLES if table_name not in existing_tables
    )
