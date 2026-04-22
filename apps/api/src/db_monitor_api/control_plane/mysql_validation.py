from typing import Protocol

import pymysql

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    MySQLConnectionConfig,
    ValidationStatus,
)

DEFAULT_MYSQL_TIMEOUT_SECONDS = 5
MYSQL_ROLE_QUERY = "SELECT @@global.read_only"


class MySQLConnectionValidator(Protocol):
    def validate(self, config: MySQLConnectionConfig) -> ConnectionValidation:
        ...


class PyMySQLConnectionValidator:
    def __init__(self, timeout_seconds: int = DEFAULT_MYSQL_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def validate(self, config: MySQLConnectionConfig) -> ConnectionValidation:
        try:
            with pymysql.connect(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database,
                connect_timeout=self._timeout_seconds,
                read_timeout=self._timeout_seconds,
                write_timeout=self._timeout_seconds,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT VERSION()")
                    version_row = cursor.fetchone()
                    cursor.execute(MYSQL_ROLE_QUERY)
                    role_row = cursor.fetchone()
        except (OSError, pymysql.MySQLError) as error:
            return ConnectionValidation(
                checked_at=utc_now(),
                detail=str(error),
                server_version=None,
                status=ValidationStatus.FAILED,
            )

        server_version = None if version_row is None else str(version_row[0])
        return ConnectionValidation(
            checked_at=utc_now(),
            detail="Connection validated successfully.",
            server_version=server_version,
            status=ValidationStatus.PASSED,
            server_role=_resolve_mysql_server_role(role_row),
        )


def _resolve_mysql_server_role(row: tuple[object, ...] | None) -> str | None:
    if row is None or len(row) == 0:
        return None
    return "replica" if str(row[0]) == "1" else "primary"
