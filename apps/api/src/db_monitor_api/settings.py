from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
import os


class RuntimeMode(StrEnum):
    LOCAL = "local"
    POSTGRES = "postgres"


@dataclass(frozen=True)
class ClickHouseSettings:
    database: str
    endpoint: str
    password: str
    username: str


@dataclass(frozen=True)
class ApiSettings:
    clickhouse: ClickHouseSettings | None
    postgres_dsn: str | None
    runtime_mode: RuntimeMode


def load_api_settings(
    environ: Mapping[str, str] | None = None,
) -> ApiSettings:
    values = os.environ if environ is None else environ
    runtime_mode = _runtime_mode_from(values)
    if runtime_mode is RuntimeMode.LOCAL:
        return ApiSettings(
            clickhouse=None,
            postgres_dsn=None,
            runtime_mode=runtime_mode,
        )
    return ApiSettings(
        clickhouse=ClickHouseSettings(
            database=_required(values, "DB_MONITOR_CLICKHOUSE_DATABASE"),
            endpoint=_required(values, "DB_MONITOR_CLICKHOUSE_ENDPOINT"),
            password=_required(values, "DB_MONITOR_CLICKHOUSE_PASSWORD"),
            username=_required(values, "DB_MONITOR_CLICKHOUSE_USERNAME"),
        ),
        postgres_dsn=_required(values, "DB_MONITOR_POSTGRES_DSN"),
        runtime_mode=runtime_mode,
    )


def _required(values: Mapping[str, str], name: str) -> str:
    value = values.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _runtime_mode_from(values: Mapping[str, str]) -> RuntimeMode:
    raw_value = values.get("DB_MONITOR_RUNTIME", RuntimeMode.LOCAL.value)
    try:
        return RuntimeMode(raw_value)
    except ValueError as error:
        raise RuntimeError(f"Unsupported DB_MONITOR_RUNTIME: {raw_value}") from error
