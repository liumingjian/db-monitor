from typing import Protocol

import pymysql

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    MySQLConnectionConfig,
    ValidationStatus,
)

DEFAULT_MYSQL_TIMEOUT_SECONDS = 5


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
                    row = cursor.fetchone()
        except (OSError, pymysql.MySQLError) as error:
            return ConnectionValidation(
                checked_at=utc_now(),
                detail=str(error),
                server_version=None,
                status=ValidationStatus.FAILED,
            )

        server_version = None if row is None else str(row[0])
        return ConnectionValidation(
            checked_at=utc_now(),
            detail="Connection validated successfully.",
            server_version=server_version,
            status=ValidationStatus.PASSED,
        )
