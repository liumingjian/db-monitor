from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import subprocess
from types import ModuleType
from typing import Protocol

import pymysql

from db_monitor_api.control_plane.domain import InstanceConnectionConfig, MySQLConnectionConfig
from db_monitor_api.control_plane.oracle_validation import (
    DEFAULT_ORACLE_TIMEOUT_SECONDS,
    _build_oracle_dsn,
    _load_oracle_driver,
    _resolve_sqlplus_host,
    _sqlplus_probe_settings_from_env,
)

MYSQL_TIMEOUT_SECONDS = 5
REPLICA_STATUS_QUERY = "SHOW REPLICA STATUS"
SLAVE_STATUS_QUERY = "SHOW SLAVE STATUS"
STATUS_QUERY = "SHOW GLOBAL STATUS"
MYSQL_TRANSACTION_KEYS = ("Com_commit", "Com_rollback")


class MySQLMetricsCollector(Protocol):
    def collect(self, connection: MySQLConnectionConfig) -> Mapping[str, str]:
        ...


class OracleMetricsCollector(Protocol):
    def collect(self, connection: InstanceConnectionConfig) -> Mapping[str, str]:
        ...


class PyMySQLMetricsCollector:
    def __init__(self, timeout_seconds: int = MYSQL_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def collect(self, connection: MySQLConnectionConfig) -> Mapping[str, str]:
        with pymysql.connect(
            host=connection.host,
            port=connection.port,
            user=connection.username,
            password=connection.password,
            database=connection.database,
            connect_timeout=self._timeout_seconds,
            read_timeout=self._timeout_seconds,
            write_timeout=self._timeout_seconds,
            cursorclass=pymysql.cursors.DictCursor,
        ) as mysql_connection:
            with mysql_connection.cursor() as cursor:
                status_rows = cursor.execute(STATUS_QUERY)
                del status_rows
                status_map = _rows_to_status_map(cursor.fetchall())
                status_map.update(_build_transaction_status(status_map))
                status_map.update(_load_replica_status(cursor))
                return status_map


def _rows_to_status_map(rows: Sequence[Mapping[str, object]]) -> dict[str, str]:
    return {str(row["Variable_name"]): str(row["Value"]) for row in rows}


def _load_replica_status(cursor: pymysql.cursors.DictCursor) -> dict[str, str]:
    replica_row = _fetch_replica_row(cursor, REPLICA_STATUS_QUERY)
    if replica_row is None:
        replica_row = _fetch_replica_row(cursor, SLAVE_STATUS_QUERY)
    if replica_row is None:
        return {}

    lag_value = replica_row.get("Seconds_Behind_Source") or replica_row.get(
        "Seconds_Behind_Master"
    )
    return {} if lag_value is None else {"Seconds_Behind_Source": str(lag_value)}


def _build_transaction_status(status_map: Mapping[str, str]) -> dict[str, str]:
    total = 0.0
    seen = False
    for key in MYSQL_TRANSACTION_KEYS:
        value = status_map.get(key)
        if value is None:
            continue
        total += float(value)
        seen = True
    return {"Transactions": str(total)} if seen else {}


def _fetch_replica_row(
    cursor: pymysql.cursors.DictCursor,
    query: str,
) -> dict[str, str] | None:
    try:
        cursor.execute(query)
    except pymysql.MySQLError:
        return None

    row = cursor.fetchone()
    return None if row is None else {str(key): str(value) for key, value in row.items()}


@dataclass(frozen=True)
class OracleMetricQuery:
    key: str
    driver_query: str
    sqlplus_query: str


ORACLE_METRIC_QUERIES: tuple[OracleMetricQuery, ...] = (
    OracleMetricQuery(
        key="SessionsTotal",
        driver_query="SELECT COUNT(*) FROM v$session",
        sqlplus_query="SELECT 'SessionsTotal=' || COUNT(*) FROM v$session;",
    ),
    OracleMetricQuery(
        key="SessionsActive",
        driver_query=(
            "SELECT COUNT(*) FROM v$session "
            "WHERE username NOT IN ('SYS', 'SYSTEM') "
            "AND username IS NOT NULL "
            "AND status = 'ACTIVE'"
        ),
        sqlplus_query=(
            "SELECT 'SessionsActive=' || COUNT(*) FROM v$session "
            "WHERE username NOT IN ('SYS', 'SYSTEM') "
            "AND username IS NOT NULL "
            "AND status = 'ACTIVE';"
        ),
    ),
    OracleMetricQuery(
        key="SessionWaits",
        driver_query=(
            "SELECT COUNT(*) FROM v$session "
            "WHERE event LIKE 'library%' "
            "OR event LIKE 'cursor%' "
            "OR event LIKE 'latch%' "
            "OR event LIKE 'enq%' "
            "OR event LIKE 'log file%'"
        ),
        sqlplus_query=(
            "SELECT 'SessionWaits=' || COUNT(*) FROM v$session "
            "WHERE event LIKE 'library%' "
            "OR event LIKE 'cursor%' "
            "OR event LIKE 'latch%' "
            "OR event LIKE 'enq%' "
            "OR event LIKE 'log file%';"
        ),
    ),
    OracleMetricQuery(
        key="UserCalls",
        driver_query="SELECT NVL(MAX(value), 0) FROM v$sysstat WHERE name = 'user calls'",
        sqlplus_query=(
            "SELECT 'UserCalls=' || NVL(MAX(value), 0) "
            "FROM v$sysstat WHERE name = 'user calls';"
        ),
    ),
    OracleMetricQuery(
        key="PhysicalReads",
        driver_query="SELECT NVL(MAX(value), 0) FROM v$sysstat WHERE name = 'physical reads'",
        sqlplus_query=(
            "SELECT 'PhysicalReads=' || NVL(MAX(value), 0) "
            "FROM v$sysstat WHERE name = 'physical reads';"
        ),
    ),
    OracleMetricQuery(
        key="UptimeSeconds",
        driver_query="SELECT FLOOR((SYSDATE - startup_time) * 86400) FROM v$instance",
        sqlplus_query=(
            "SELECT 'UptimeSeconds=' || FLOOR((SYSDATE - startup_time) * 86400) "
            "FROM v$instance;"
        ),
    ),
)
_SQLPLUS_ORACLE_METRICS_SCRIPT = """\
export ORACLE_HOME=/u01/app/oracle/product/11.2.0/xe
export PATH="$ORACLE_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$ORACLE_HOME/lib"
sqlplus -s -L "$ORACLE_USERNAME/$ORACLE_PASSWORD@//$ORACLE_HOST:$ORACLE_PORT/$ORACLE_SERVICE" <<'SQL'
WHENEVER SQLERROR EXIT SQL.SQLCODE;
set heading off feedback off pagesize 0 verify off echo off trimspool on
{queries}
exit;
SQL
""".format(queries="\n".join(query.sqlplus_query for query in ORACLE_METRIC_QUERIES))


class PythonOracleMetricsCollector:
    def __init__(self, timeout_seconds: int = DEFAULT_ORACLE_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def collect(self, connection: InstanceConnectionConfig) -> Mapping[str, str]:
        driver = _load_oracle_driver()
        primary_error: Exception
        if driver is not None:
            try:
                return _collect_oracle_metrics_with_driver(
                    connection=connection,
                    driver=driver,
                    timeout_seconds=self._timeout_seconds,
                )
            except Exception as error:
                primary_error = error
        else:
            primary_error = RuntimeError(
                "Oracle metrics collection requires the python-oracledb or cx_Oracle package "
                "plus a reachable DSN/service name."
            )

        sqlplus_settings = _sqlplus_probe_settings_from_env()
        if sqlplus_settings is None:
            raise RuntimeError(str(primary_error)) from primary_error

        try:
            return _collect_oracle_metrics_with_sqlplus(
                connection=connection,
                container_name=sqlplus_settings.container_name,
                localhost_alias=sqlplus_settings.localhost_alias,
            )
        except Exception as sqlplus_error:
            raise RuntimeError(
                f"Python driver collection failed: {primary_error} "
                f"sqlplus fallback failed: {sqlplus_error}"
            ) from sqlplus_error


def _collect_oracle_metrics_with_driver(
    *,
    connection: InstanceConnectionConfig,
    driver: ModuleType,
    timeout_seconds: int,
) -> dict[str, str]:
    connect_kwargs: dict[str, object] = {
        "user": connection.username,
        "password": connection.password,
        "dsn": _build_oracle_dsn(driver, connection),
    }
    if getattr(driver, "__name__", "") == "oracledb":
        connect_kwargs["tcp_connect_timeout"] = timeout_seconds

    db_connection = None
    cursor = None
    metrics: dict[str, str] = {}
    try:
        db_connection = driver.connect(**connect_kwargs)
        cursor = db_connection.cursor()
        for query in ORACLE_METRIC_QUERIES:
            cursor.execute(query.driver_query)
            row = cursor.fetchone()
            value = 0 if row is None else row[0]
            metrics[query.key] = _coerce_oracle_metric_value(value)
    finally:
        if cursor is not None:
            cursor.close()
        if db_connection is not None:
            db_connection.close()
    return metrics


def _collect_oracle_metrics_with_sqlplus(
    *,
    connection: InstanceConnectionConfig,
    container_name: str,
    localhost_alias: str,
) -> dict[str, str]:
    env = {
        "ORACLE_HOST": _resolve_sqlplus_host(
            connection.host,
            localhost_alias=localhost_alias,
        ),
        "ORACLE_PASSWORD": connection.password,
        "ORACLE_PORT": str(connection.port),
        "ORACLE_SERVICE": connection.database,
        "ORACLE_USERNAME": connection.username,
    }
    completed = subprocess.run(
        [
            "docker",
            "exec",
            "-e",
            "ORACLE_HOST",
            "-e",
            "ORACLE_PASSWORD",
            "-e",
            "ORACLE_PORT",
            "-e",
            "ORACLE_SERVICE",
            "-e",
            "ORACLE_USERNAME",
            container_name,
            "bash",
            "--noprofile",
            "--norc",
            "-lc",
            _SQLPLUS_ORACLE_METRICS_SCRIPT,
        ],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "sqlplus metrics probe failed without output."
        raise RuntimeError(detail)
    return _parse_sqlplus_oracle_metrics(completed.stdout)


def _parse_sqlplus_oracle_metrics(output: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    expected_keys = {query.key for query in ORACLE_METRIC_QUERIES}
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        if key in expected_keys:
            metrics[key] = value.strip()
    missing = expected_keys.difference(metrics)
    if missing:
        raise RuntimeError(
            "Missing Oracle metrics from sqlplus output: " + ", ".join(sorted(missing))
        )
    return metrics


def _coerce_oracle_metric_value(value: object) -> str:
    if value is None:
        return "0"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
