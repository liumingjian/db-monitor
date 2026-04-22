"""Runtime action: MySQL processlist kill (ADR-0006, ADR-0011 D2).

This module implements the runtime side-effect command used by the
`POST /instances/{instance_id}/processlist/{process_id}/kill` endpoint.

Debug-First Policy: failures surface as explicit exceptions with the
root cause preserved; there is no silent retry, no mock-success path,
and the Clickhouse read pipeline is never touched (ADR-0006).

Safety net (slice 1 minimum per ADR-0006):
- Refuse to kill the monitoring user's own connection
  (`connection.username`): kicking the collector off is always wrong.
- Refuse when the instance `validation_status != PASSED`: if we cannot
  validate the connection we must not assume a safe kill surface.
System / replication connection protection is deferred to slice 5.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import pymysql

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import (
    InstanceConnectionConfig,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import ControlPlaneRepository
from db_monitor_api.control_plane.service import AssetNotFoundError

KILL_AUDIT_ACTION = "instances.process.kill"
KILL_TIMEOUT_SECONDS = 5


class ProcesslistKillBlocked(Exception):
    """Raised when a kill request is rejected by the safety net."""


class ProcesslistKillFailed(Exception):
    """Raised when the underlying KILL command fails."""


@dataclass(frozen=True)
class ProcesslistKillResult:
    checked_at: datetime
    killed: bool
    notes: str | None


class ProcesslistKiller(Protocol):
    def kill(
        self,
        *,
        connection: InstanceConnectionConfig,
        process_id: int,
        monitor_user: str,
    ) -> None:
        ...


class PyMySQLProcesslistKiller:
    """Looks up the target thread's user in the same session that runs
    `KILL` so the `monitor_user` safety check and the kill are transactionally
    consistent. If the thread is owned by the monitoring user itself, the
    kill is refused with `ProcesslistKillBlocked`.
    """

    def __init__(self, *, timeout_seconds: int = KILL_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def kill(
        self,
        *,
        connection: InstanceConnectionConfig,
        process_id: int,
        monitor_user: str,
    ) -> None:
        try:
            with pymysql.connect(
                host=connection.host,
                port=connection.port,
                user=connection.username,
                password=connection.password,
                database=connection.database,
                connect_timeout=self._timeout_seconds,
                read_timeout=self._timeout_seconds,
                write_timeout=self._timeout_seconds,
            ) as mysql_connection:
                with mysql_connection.cursor() as cursor:
                    _verify_thread_not_monitor_user(
                        cursor=cursor,
                        monitor_user=monitor_user,
                        process_id=process_id,
                    )
                    cursor.execute("KILL %s", (process_id,))
        except pymysql.MySQLError as error:
            raise ProcesslistKillFailed(str(error)) from error


def _verify_thread_not_monitor_user(
    *,
    cursor: object,
    monitor_user: str,
    process_id: int,
) -> None:
    # Uses information_schema.processlist so the user column is authoritative
    # for the target thread at kill time (avoiding stale snapshot races).
    cursor.execute(  # type: ignore[attr-defined]
        "SELECT USER FROM information_schema.processlist WHERE ID = %s",
        (process_id,),
    )
    row = cursor.fetchone()  # type: ignore[attr-defined]
    if row is None:
        raise ProcesslistKillFailed(
            f"Process {process_id} not found on the target MySQL instance."
        )
    raw_user = row[0] if not isinstance(row, dict) else row.get("USER", row.get("user"))
    target_user = "" if raw_user is None else str(raw_user).split("@", 1)[0]
    if target_user == monitor_user:
        raise ProcesslistKillBlocked(
            "Refusing to kill the monitoring user's own connection."
        )


@dataclass(frozen=True)
class ProcesslistKillService:
    audit_service: AuditService
    control_plane_repository: ControlPlaneRepository
    killer: ProcesslistKiller

    def kill_process(
        self,
        *,
        actor_user_id: str,
        instance_id: str,
        organization_id: str,
        process_id: int,
        reason: str | None,
    ) -> ProcesslistKillResult:
        del reason  # Reserved for future audit.details; slice 1 audit has no detail column.
        instance = self._require_instance(
            instance_id=instance_id,
            organization_id=organization_id,
        )
        resource = _kill_resource(instance_id=instance_id, process_id=process_id)
        try:
            _enforce_safety_net(instance=instance)
            self.killer.kill(
                connection=instance.connection,
                process_id=process_id,
                monitor_user=instance.connection.username,
            )
        except (ProcesslistKillBlocked, ProcesslistKillFailed):
            self._record_audit(
                actor_user_id=actor_user_id,
                organization_id=organization_id,
                outcome="failure",
                resource=resource,
            )
            raise
        self._record_audit(
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            outcome="success",
            resource=resource,
        )
        return ProcesslistKillResult(checked_at=utc_now(), killed=True, notes=None)

    def _require_instance(
        self,
        *,
        instance_id: str,
        organization_id: str,
    ) -> MonitoredInstance:
        instance = self.control_plane_repository.get_instance(
            instance_id,
            organization_id=organization_id,
        )
        if instance is None:
            raise AssetNotFoundError(f"Unknown instance: {instance_id}")
        return instance

    def _record_audit(
        self,
        *,
        actor_user_id: str,
        organization_id: str,
        outcome: str,
        resource: str,
    ) -> None:
        self.audit_service.record(
            action=KILL_AUDIT_ACTION,
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            outcome=outcome,
            resource=resource,
        )


def _enforce_safety_net(*, instance: MonitoredInstance) -> None:
    if instance.validation.status is not ValidationStatus.PASSED:
        raise ProcesslistKillBlocked(
            "Instance validation is not PASSED; kill rejected by safety net."
        )


def _kill_resource(*, instance_id: str, process_id: int) -> str:
    return f"instance:{instance_id}:process:{process_id}"
