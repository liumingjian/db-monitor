from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ValidationStatus(StrEnum):
    FAILED = "failed"
    PASSED = "passed"


class DatabaseEngine(StrEnum):
    MYSQL = "mysql"
    ORACLE = "oracle"


@dataclass(frozen=True)
class InstanceConnectionConfig:
    database: str
    host: str
    password: str
    port: int
    username: str


@dataclass(frozen=True)
class ConnectionValidation:
    checked_at: datetime
    detail: str
    server_version: str | None
    status: ValidationStatus
    server_role: str | None = None


@dataclass(frozen=True)
class MonitoredInstance:
    connection: InstanceConnectionConfig
    created_at: datetime
    environment: str
    instance_id: str
    labels: tuple[str, ...]
    name: str
    organization_id: str
    validation: ConnectionValidation
    engine: DatabaseEngine = DatabaseEngine.MYSQL


@dataclass(frozen=True)
class SystemSetting:
    key: str
    organization_id: str
    updated_at: datetime
    value: str


MySQLConnectionConfig = InstanceConnectionConfig
MySQLInstance = MonitoredInstance
