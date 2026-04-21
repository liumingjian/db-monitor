from dataclasses import dataclass
from importlib import import_module
import os
import subprocess
from types import ModuleType
from typing import Protocol

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    InstanceConnectionConfig,
    ValidationStatus,
)

DEFAULT_ORACLE_TIMEOUT_SECONDS = 5
DEFAULT_ORACLE_SQLPLUS_LOCALHOST_ALIAS = "host.docker.internal"
ORACLE_SQLPLUS_DOCKER_CONTAINER_ENV = "DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER"
ORACLE_SQLPLUS_LOCALHOST_ALIAS_ENV = "DB_MONITOR_ORACLE_SQLPLUS_LOCALHOST_ALIAS"
_LOCAL_ORACLE_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
_SQLPLUS_SCRIPT = """\
export ORACLE_HOME=/u01/app/oracle/product/11.2.0/xe
export PATH="$ORACLE_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$ORACLE_HOME/lib"
sqlplus -s -L "$ORACLE_USERNAME/$ORACLE_PASSWORD@//$ORACLE_HOST:$ORACLE_PORT/$ORACLE_SERVICE" <<'SQL'
WHENEVER SQLERROR EXIT SQL.SQLCODE;
set heading off feedback off pagesize 0 verify off echo off
select 1 from dual;
exit;
SQL
"""


@dataclass(frozen=True)
class SqlPlusProbeSettings:
    container_name: str
    localhost_alias: str


class OracleConnectionValidator(Protocol):
    def validate(self, config: InstanceConnectionConfig) -> ConnectionValidation:
        ...


class PythonOracleConnectionValidator:
    def __init__(self, timeout_seconds: int = DEFAULT_ORACLE_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def validate(self, config: InstanceConnectionConfig) -> ConnectionValidation:
        driver = _load_oracle_driver()
        primary_validation = (
            _validate_with_python_driver(
                config=config,
                driver=driver,
                timeout_seconds=self._timeout_seconds,
            )
            if driver is not None
            else _missing_python_driver_validation()
        )
        if primary_validation.status is ValidationStatus.PASSED:
            return primary_validation

        sqlplus_settings = _sqlplus_probe_settings_from_env()
        if sqlplus_settings is None:
            return primary_validation

        sqlplus_validation = _validate_with_sqlplus_container(
            config=config,
            settings=sqlplus_settings,
        )
        if sqlplus_validation.status is ValidationStatus.PASSED:
            return sqlplus_validation
        return ConnectionValidation(
            checked_at=utc_now(),
            detail=(
                f"Python driver validation failed: {primary_validation.detail} "
                f"sqlplus fallback failed: {sqlplus_validation.detail}"
            ),
            server_version=None,
            status=ValidationStatus.FAILED,
        )


def _load_oracle_driver() -> ModuleType | None:
    for module_name in ("oracledb", "cx_Oracle"):
        try:
            return import_module(module_name)
        except ModuleNotFoundError:
            continue
    return None


def _build_oracle_dsn(driver: ModuleType, config: InstanceConnectionConfig) -> str:
    makedsn = getattr(driver, "makedsn", None)
    if callable(makedsn):
        return str(makedsn(config.host, config.port, service_name=config.database))
    return f"{config.host}:{config.port}/{config.database}"


def _missing_python_driver_validation() -> ConnectionValidation:
    return ConnectionValidation(
        checked_at=utc_now(),
        detail=(
            "Oracle validation requires the python-oracledb or cx_Oracle package "
            "plus a reachable DSN/service name."
        ),
        server_version=None,
        status=ValidationStatus.FAILED,
    )


def _validate_with_python_driver(
    *,
    config: InstanceConnectionConfig,
    driver: ModuleType,
    timeout_seconds: int,
) -> ConnectionValidation:
    connection = None
    cursor = None
    try:
        connect_kwargs: dict[str, object] = {
            "user": config.username,
            "password": config.password,
            "dsn": _build_oracle_dsn(driver, config),
        }
        if driver.__name__ == "oracledb":
            connect_kwargs["tcp_connect_timeout"] = timeout_seconds
        connection = driver.connect(**connect_kwargs)
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM dual")
        cursor.fetchone()
        server_version = getattr(connection, "version", None)
    except Exception as error:
        return ConnectionValidation(
            checked_at=utc_now(),
            detail=str(error),
            server_version=None,
            status=ValidationStatus.FAILED,
        )
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    return ConnectionValidation(
        checked_at=utc_now(),
        detail="Oracle connection validated successfully using the supplied DSN/service name.",
        server_version=None if server_version is None else str(server_version),
        status=ValidationStatus.PASSED,
    )


def _sqlplus_probe_settings_from_env() -> SqlPlusProbeSettings | None:
    container_name = os.environ.get(ORACLE_SQLPLUS_DOCKER_CONTAINER_ENV)
    if container_name is None or container_name == "":
        return None
    localhost_alias = os.environ.get(
        ORACLE_SQLPLUS_LOCALHOST_ALIAS_ENV,
        DEFAULT_ORACLE_SQLPLUS_LOCALHOST_ALIAS,
    )
    return SqlPlusProbeSettings(
        container_name=container_name,
        localhost_alias=localhost_alias,
    )


def _validate_with_sqlplus_container(
    *,
    config: InstanceConnectionConfig,
    settings: SqlPlusProbeSettings,
) -> ConnectionValidation:
    env = os.environ.copy()
    env.update(
        {
            "ORACLE_HOST": _resolve_sqlplus_host(
                config.host,
                localhost_alias=settings.localhost_alias,
            ),
            "ORACLE_PASSWORD": config.password,
            "ORACLE_PORT": str(config.port),
            "ORACLE_SERVICE": config.database,
            "ORACLE_USERNAME": config.username,
        }
    )
    try:
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
                settings.container_name,
                "bash",
                "--noprofile",
                "--norc",
                "-lc",
                _SQLPLUS_SCRIPT,
            ],
            capture_output=True,
            check=False,
            env=env,
            text=True,
        )
    except Exception as error:
        return ConnectionValidation(
            checked_at=utc_now(),
            detail=str(error),
            server_version=None,
            status=ValidationStatus.FAILED,
        )

    if completed.returncode != 0:
        return ConnectionValidation(
            checked_at=utc_now(),
            detail=_sqlplus_error_detail(completed),
            server_version=None,
            status=ValidationStatus.FAILED,
        )

    return ConnectionValidation(
        checked_at=utc_now(),
        detail=(
            "Oracle connection validated successfully using sqlplus via docker "
            f"container {settings.container_name}."
        ),
        server_version=None,
        status=ValidationStatus.PASSED,
    )


def _resolve_sqlplus_host(host: str, *, localhost_alias: str) -> str:
    if host.lower() in _LOCAL_ORACLE_HOSTS:
        return localhost_alias
    return host


def _sqlplus_error_detail(completed: subprocess.CompletedProcess[str]) -> str:
    stderr = completed.stderr.strip()
    if stderr:
        return stderr
    stdout = completed.stdout.strip()
    if stdout:
        return stdout
    return "sqlplus probe failed without output."
