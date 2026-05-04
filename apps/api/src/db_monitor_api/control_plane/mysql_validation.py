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
MYSQL_PS_ENABLED_QUERY = "SELECT @@performance_schema"
MYSQL_PS_HISTORY_SIZE_QUERY = "SELECT @@events_statements_history_long_size"
PS_HISTORY_SIZE_MIN_HINT = 10000
PS_DISABLED_HINT = (
    "Performance Schema events_statements_history_long 未启用，请在被监控实例设置"
    " performance_schema=ON 并确保 events_statements_history_long_size >= "
    f"{PS_HISTORY_SIZE_MIN_HINT}"
)
PS_HISTORY_SIZE_HINT_PREFIX = (
    "events_statements_history_long_size 过小，建议 >= "
    f"{PS_HISTORY_SIZE_MIN_HINT}"
)
PS_PROBE_FAILED_HINT = "performance_schema 探测失败"


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
                    ps_hint = _probe_performance_schema(cursor)
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
            detail=_compose_validation_detail(ps_hint),
            server_version=server_version,
            status=ValidationStatus.PASSED,
            server_role=_resolve_mysql_server_role(role_row),
        )


def _resolve_mysql_server_role(row: tuple[object, ...] | None) -> str | None:
    if row is None or len(row) == 0:
        return None
    return "replica" if str(row[0]) == "1" else "primary"


def _probe_performance_schema(cursor: object) -> str | None:
    """Return an appended `detail` hint describing the PS state.

    `None` means PS is enabled and history size meets the hint floor;
    otherwise the string is a user-visible Chinese hint suitable for
    rendering in the Slow queries tab without gating validation PASSED.
    Driver errors during the probe surface as a generic hint rather than
    failing the validation, per ADR-0007 and the slow-query SPEC.
    """
    try:
        cursor.execute(MYSQL_PS_ENABLED_QUERY)  # type: ignore[attr-defined]
        enabled_row = cursor.fetchone()  # type: ignore[attr-defined]
        cursor.execute(MYSQL_PS_HISTORY_SIZE_QUERY)  # type: ignore[attr-defined]
        size_row = cursor.fetchone()  # type: ignore[attr-defined]
    except pymysql.MySQLError:
        return PS_PROBE_FAILED_HINT
    if not _row_truthy(enabled_row):
        return PS_DISABLED_HINT
    size = _row_int(size_row)
    if size is not None and size < PS_HISTORY_SIZE_MIN_HINT:
        return f"{PS_HISTORY_SIZE_HINT_PREFIX}（当前 {size}）"
    return None


def _row_truthy(row: object) -> bool:
    value = _row_scalar(row)
    if value is None or value == "":
        return False
    return str(value) not in {"0", "OFF", "off", "false", "False"}


def _row_int(row: object) -> int | None:
    value = _row_scalar(row)
    if value is None or value == "":
        return None
    return int(str(value))


def _row_scalar(row: object) -> object:
    if row is None:
        return None
    if isinstance(row, dict):
        values = list(row.values())
        return values[0] if values else None
    if isinstance(row, (tuple, list)):
        return row[0] if row else None
    return row


def _compose_validation_detail(ps_hint: str | None) -> str:
    base = "Connection validated successfully."
    if ps_hint is None:
        return base
    return f"{base} {ps_hint}"
