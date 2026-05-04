"""Per-instance Oracle tablespace scheduler (Epic 15 Slice 1 child #4).

Drives `TablespaceWorker.collect_once()` for every Oracle instance on
its configured cadence read from `instance_parameters.parameters->>
'tablespace_interval_seconds'` (default 300s, min 60s).

Debug-First Policy: collection failures are surfaced as
`WorkerRunResult(status="failed", error=<root cause>)` items; there is
no silent swallow, no internal retry, and no mock success. The caller
(`worker-oracle` entry point or the shared `WorkerProcess`) is
responsible for JSON-logging each result and exiting non-zero when any
instance reports failure.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    DatabaseEngine,
    MonitoredInstance,
    ValidationStatus,
)
from db_monitor_api.control_plane.repository import ControlPlaneRepository
from db_monitor_pipeline.tablespace import (
    InstanceParameterReader,
    TablespaceWorker,
    resolve_tablespace_interval_seconds,
)
from db_monitor_pipeline.worker import WorkerRunResult


@dataclass(frozen=True)
class TablespaceCycleResult:
    results: tuple[WorkerRunResult, ...]
    scanned_instances: int
    scheduled_instances: int


@dataclass
class TablespaceScheduler:
    """Tracks per-instance `next_run_at` and dispatches due collections."""

    control_plane_repository: ControlPlaneRepository
    parameter_reader: InstanceParameterReader
    worker: TablespaceWorker
    clock: Callable[[], datetime] = field(default=utc_now)
    _next_run_at: dict[str, datetime] = field(default_factory=dict)

    def run_cycle(self) -> TablespaceCycleResult:
        instances = self.control_plane_repository.list_instances(organization_id=None)
        dispatchable = tuple(
            instance for instance in instances if _is_dispatchable(instance)
        )
        now = self.clock()
        due = tuple(instance for instance in dispatchable if self._is_due(instance, now))
        results = tuple(self._run_instance(instance, now=now) for instance in due)
        return TablespaceCycleResult(
            results=results,
            scanned_instances=len(dispatchable),
            scheduled_instances=len(results),
        )

    def _is_due(self, instance: MonitoredInstance, now: datetime) -> bool:
        scheduled = self._next_run_at.get(instance.instance_id)
        return scheduled is None or scheduled <= now

    def _run_instance(
        self,
        instance: MonitoredInstance,
        *,
        now: datetime,
    ) -> WorkerRunResult:
        interval_seconds = resolve_tablespace_interval_seconds(
            instance_id=instance.instance_id,
            reader=self.parameter_reader,
        )
        try:
            snapshot = self.worker.collect_once(instance)
        except Exception as error:
            self._next_run_at[instance.instance_id] = now + timedelta(
                seconds=interval_seconds,
            )
            return WorkerRunResult(
                error=f"{instance.instance_id}: {error}",
                next_retry_at=None,
                processed_metrics=0,
                retry_attempt=None,
                status="failed",
            )
        self._next_run_at[instance.instance_id] = now + timedelta(
            seconds=interval_seconds,
        )
        return WorkerRunResult(
            error=None,
            next_retry_at=None,
            processed_metrics=len(snapshot.entries),
            retry_attempt=None,
            status="processed",
        )


def _is_dispatchable(instance: MonitoredInstance) -> bool:
    if instance.engine is not DatabaseEngine.ORACLE:
        return False
    return instance.validation.status is ValidationStatus.PASSED


def reduce_cycle_to_run_result(
    cycle: TablespaceCycleResult,
) -> WorkerRunResult:
    """Aggregate a cycle's per-instance results into a single
    `WorkerRunResult` so worker entrypoints can emit one JSON log line
    per cycle. Failures take precedence over successes.
    """

    failures: Sequence[WorkerRunResult] = tuple(
        item for item in cycle.results if item.status == "failed"
    )
    processed_total = sum(item.processed_metrics for item in cycle.results)
    if failures:
        messages = tuple(failure.error or "unknown" for failure in failures)
        return WorkerRunResult(
            error="; ".join(messages),
            next_retry_at=None,
            processed_metrics=processed_total,
            retry_attempt=None,
            status="failed",
        )
    if cycle.scheduled_instances == 0:
        return WorkerRunResult(
            error=None,
            next_retry_at=None,
            processed_metrics=0,
            retry_attempt=None,
            status="idle",
        )
    return WorkerRunResult(
        error=None,
        next_retry_at=None,
        processed_metrics=processed_total,
        retry_attempt=None,
        status="processed",
    )
