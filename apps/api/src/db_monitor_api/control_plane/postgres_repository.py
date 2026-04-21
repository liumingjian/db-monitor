import json
from datetime import datetime
from typing import cast

import psycopg

from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    InstanceConnectionConfig,
    MonitoredInstance,
    SystemSetting,
    ValidationStatus,
)

_INSTANCE_SELECT_SQL = """
SELECT
    instance_id,
    organization_id,
    engine,
    name,
    environment,
    labels_json,
    host,
    port,
    username,
    password,
    database_name,
    created_at,
    validation_status,
    validation_detail,
    validation_checked_at,
    validation_server_version
FROM control_mysql_instances
"""
_SETTING_SELECT_SQL = """
SELECT
    organization_id,
    key,
    value,
    updated_at
FROM control_settings
"""


class PostgresControlPlaneRepository:
    def __init__(self, *, postgres_dsn: str) -> None:
        self._postgres_dsn = postgres_dsn

    def create_instance(self, instance: MonitoredInstance) -> None:
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO control_mysql_instances (
                        instance_id,
                        organization_id,
                        engine,
                        name,
                        environment,
                        labels_json,
                        host,
                        port,
                        username,
                        password,
                        database_name,
                        created_at,
                        validation_status,
                        validation_detail,
                        validation_checked_at,
                        validation_server_version
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    _instance_values(instance),
                )

    def get_instance(
        self,
        instance_id: str,
        *,
        organization_id: str | None = None,
    ) -> MonitoredInstance | None:
        query = f"{_INSTANCE_SELECT_SQL} WHERE instance_id = %s"
        params: list[object] = [instance_id]
        if organization_id is not None:
            query += " AND organization_id = %s"
            params.append(organization_id)
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                row = cursor.fetchone()
        return None if row is None else _row_to_instance(row)

    def list_instances(
        self,
        *,
        organization_id: str | None = None,
    ) -> tuple[MonitoredInstance, ...]:
        query = _INSTANCE_SELECT_SQL
        params: tuple[object, ...] = ()
        if organization_id is not None:
            query += " WHERE organization_id = %s"
            params = (organization_id,)
        query += " ORDER BY created_at ASC"
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
        return tuple(_row_to_instance(row) for row in rows)

    def upsert_instance(self, instance: MonitoredInstance) -> None:
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO control_mysql_instances (
                        instance_id,
                        organization_id,
                        engine,
                        name,
                        environment,
                        labels_json,
                        host,
                        port,
                        username,
                        password,
                        database_name,
                        created_at,
                        validation_status,
                        validation_detail,
                        validation_checked_at,
                        validation_server_version
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (instance_id) DO UPDATE SET
                        organization_id = EXCLUDED.organization_id,
                        engine = EXCLUDED.engine,
                        name = EXCLUDED.name,
                        environment = EXCLUDED.environment,
                        labels_json = EXCLUDED.labels_json,
                        host = EXCLUDED.host,
                        port = EXCLUDED.port,
                        username = EXCLUDED.username,
                        password = EXCLUDED.password,
                        database_name = EXCLUDED.database_name,
                        validation_status = EXCLUDED.validation_status,
                        validation_detail = EXCLUDED.validation_detail,
                        validation_checked_at = EXCLUDED.validation_checked_at,
                        validation_server_version = EXCLUDED.validation_server_version
                    """,
                    _instance_values(instance),
                )

    def list_settings(
        self,
        *,
        organization_id: str | None = None,
    ) -> tuple[SystemSetting, ...]:
        query = _SETTING_SELECT_SQL
        params: tuple[object, ...] = ()
        if organization_id is not None:
            query += " WHERE organization_id = %s"
            params = (organization_id,)
        query += " ORDER BY organization_id ASC, key ASC"
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
        return tuple(
            SystemSetting(
                key=str(row[1]),
                organization_id=str(row[0]),
                updated_at=cast(datetime, row[3]),
                value=str(row[2]),
            )
            for row in rows
        )

    def upsert_setting(self, setting: SystemSetting) -> None:
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO control_settings (organization_id, key, value, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (organization_id, key) DO UPDATE SET
                        value = EXCLUDED.value,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        setting.organization_id,
                        setting.key,
                        setting.value,
                        setting.updated_at,
                    ),
                )


def _instance_values(instance: MonitoredInstance) -> tuple[object, ...]:
    return (
        instance.instance_id,
        instance.organization_id,
        instance.engine.value,
        instance.name,
        instance.environment,
        json.dumps(instance.labels),
        instance.connection.host,
        instance.connection.port,
        instance.connection.username,
        instance.connection.password,
        instance.connection.database,
        instance.created_at,
        instance.validation.status.value,
        instance.validation.detail,
        instance.validation.checked_at,
        instance.validation.server_version,
    )


def _row_to_instance(row: tuple[object, ...]) -> MonitoredInstance:
    return MonitoredInstance(
        connection=InstanceConnectionConfig(
            host=str(row[6]),
            port=int(cast(int | str, row[7])),
            username=str(row[8]),
            password=str(row[9]),
            database=str(row[10]),
        ),
        created_at=cast(datetime, row[11]),
        engine=DatabaseEngine(str(row[2])),
        environment=str(row[4]),
        instance_id=str(row[0]),
        labels=tuple(json.loads(str(row[5]))),
        name=str(row[3]),
        organization_id=str(row[1]),
        validation=ConnectionValidation(
            checked_at=cast(datetime, row[14]),
            detail=str(row[13]),
            server_version=None if row[15] is None else str(row[15]),
            status=ValidationStatus(str(row[12])),
        ),
    )
