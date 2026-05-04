"""Shared fixtures for Oracle tablespace collector/scheduler tests (child #4)."""

from datetime import datetime, timezone

from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    DatabaseEngine,
    InstanceConnectionConfig,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_pipeline.tablespace import TablespaceEntry


ANCHOR = datetime(2026, 4, 22, 12, 0, 0, tzinfo=timezone.utc)


class StaticCollector:
    def __init__(self, entries: tuple[TablespaceEntry, ...]) -> None:
        self._entries = entries

    def collect(
        self, connection: InstanceConnectionConfig
    ) -> tuple[TablespaceEntry, ...]:
        del connection
        return self._entries


class FailingCollector:
    def collect(
        self, connection: InstanceConnectionConfig
    ) -> tuple[TablespaceEntry, ...]:
        del connection
        raise RuntimeError("ORA-01034: ORACLE not available")


def oracle_instance(
    *,
    instance_id: str = "inst-oracle",
    status: ValidationStatus = ValidationStatus.PASSED,
    engine: DatabaseEngine = DatabaseEngine.ORACLE,
) -> MonitoredInstance:
    return MonitoredInstance(
        connection=InstanceConnectionConfig(
            database="XE",
            host="127.0.0.1",
            password="oracle",
            port=1521,
            username="system",
        ),
        created_at=ANCHOR,
        engine=engine,
        environment="prod",
        instance_id=instance_id,
        labels=("oracle",),
        name=instance_id,
        organization_id="org-internal",
        validation=ConnectionValidation(
            checked_at=ANCHOR,
            detail="ok",
            server_version="19c",
            status=status,
        ),
    )


def tablespace_entry(
    *,
    name: str = "SYSAUX",
    used_bytes: int = 1024,
    total_bytes: int = 4096,
    used_rate_percent: float = 25.0,
    autoextensible: bool = True,
    status: str = "ONLINE",
) -> TablespaceEntry:
    return TablespaceEntry(
        tablespace_name=name,
        status=status,
        used_bytes=used_bytes,
        total_bytes=total_bytes,
        used_rate_percent=used_rate_percent,
        autoextensible=autoextensible,
    )
