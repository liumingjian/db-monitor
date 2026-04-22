from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
import os

from db_monitor_api.settings import ClickHouseSettings
from db_monitor_pipeline.collector import MYSQL_TIMEOUT_SECONDS

DEFAULT_PROCESS_POLL_SECONDS = 5.0
DEFAULT_RETRY_BACKOFF_SECONDS = 30
DEFAULT_RETRY_MAX_ATTEMPTS = 3


class ProcessMode(StrEnum):
    LOOP = "loop"
    ONESHOT = "oneshot"


@dataclass(frozen=True)
class SchedulerProcessSettings:
    max_cycles: int | None
    mode: ProcessMode
    poll_seconds: float
    postgres_dsn: str
    redis_url: str


@dataclass(frozen=True)
class WorkerProcessSettings:
    clickhouse: ClickHouseSettings
    max_cycles: int | None
    mode: ProcessMode
    mysql_timeout_seconds: int
    poll_seconds: float
    postgres_dsn: str
    redis_url: str
    retry_backoff_seconds: int
    retry_max_attempts: int


def load_scheduler_process_settings(
    environ: Mapping[str, str] | None = None,
) -> SchedulerProcessSettings:
    values = os.environ if environ is None else environ
    return SchedulerProcessSettings(
        max_cycles=_load_optional_positive_int(values, "DB_MONITOR_SCHEDULER_MAX_CYCLES"),
        mode=_load_process_mode(values, "DB_MONITOR_SCHEDULER_MODE"),
        poll_seconds=_load_positive_float(
            values,
            "DB_MONITOR_SCHEDULER_POLL_SECONDS",
            DEFAULT_PROCESS_POLL_SECONDS,
        ),
        postgres_dsn=_required(values, "DB_MONITOR_POSTGRES_DSN"),
        redis_url=_required(values, "DB_MONITOR_REDIS_URL"),
    )


def load_worker_process_settings(
    environ: Mapping[str, str] | None = None,
) -> WorkerProcessSettings:
    values = os.environ if environ is None else environ
    return WorkerProcessSettings(
        clickhouse=ClickHouseSettings(
            database=_required(values, "DB_MONITOR_CLICKHOUSE_DATABASE"),
            endpoint=_required(values, "DB_MONITOR_CLICKHOUSE_ENDPOINT"),
            password=_required(values, "DB_MONITOR_CLICKHOUSE_PASSWORD"),
            username=_required(values, "DB_MONITOR_CLICKHOUSE_USERNAME"),
        ),
        max_cycles=_load_optional_positive_int(values, "DB_MONITOR_WORKER_MYSQL_MAX_CYCLES"),
        mode=_load_process_mode(values, "DB_MONITOR_WORKER_MYSQL_MODE"),
        mysql_timeout_seconds=_load_positive_int(
            values,
            "DB_MONITOR_WORKER_MYSQL_TIMEOUT_SECONDS",
            MYSQL_TIMEOUT_SECONDS,
        ),
        poll_seconds=_load_positive_float(
            values,
            "DB_MONITOR_WORKER_MYSQL_POLL_SECONDS",
            DEFAULT_PROCESS_POLL_SECONDS,
        ),
        postgres_dsn=_required(values, "DB_MONITOR_POSTGRES_DSN"),
        redis_url=_required(values, "DB_MONITOR_REDIS_URL"),
        retry_backoff_seconds=_load_positive_int(
            values,
            "DB_MONITOR_WORKER_MYSQL_BACKOFF_SECONDS",
            DEFAULT_RETRY_BACKOFF_SECONDS,
        ),
        retry_max_attempts=_load_positive_int(
            values,
            "DB_MONITOR_WORKER_MYSQL_MAX_ATTEMPTS",
            DEFAULT_RETRY_MAX_ATTEMPTS,
        ),
    )


def _load_optional_positive_int(values: Mapping[str, str], name: str) -> int | None:
    raw_value = values.get(name)
    if raw_value is None or raw_value == "":
        return None
    parsed = int(raw_value)
    if parsed < 1:
        raise RuntimeError(f"{name} must be >= 1.")
    return parsed


def _load_positive_float(values: Mapping[str, str], name: str, default: float) -> float:
    raw_value = values.get(name)
    parsed = default if raw_value is None or raw_value == "" else float(raw_value)
    if parsed <= 0:
        raise RuntimeError(f"{name} must be > 0.")
    return parsed


def _load_positive_int(values: Mapping[str, str], name: str, default: int) -> int:
    raw_value = values.get(name)
    parsed = default if raw_value is None or raw_value == "" else int(raw_value)
    if parsed < 1:
        raise RuntimeError(f"{name} must be >= 1.")
    return parsed


def _load_process_mode(values: Mapping[str, str], name: str) -> ProcessMode:
    raw_value = values.get(name, ProcessMode.ONESHOT.value)
    try:
        return ProcessMode(raw_value)
    except ValueError as error:
        raise RuntimeError(f"Unsupported {name}: {raw_value}") from error


def _required(values: Mapping[str, str], name: str) -> str:
    value = values.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
