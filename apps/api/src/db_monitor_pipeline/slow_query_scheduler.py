"""Per-instance MySQL slow query scheduler (ADR-0007 / ADR-0011 D3).

Drives `SlowQueryWorker.collect_once()` on a fixed 60s cadence across
every PASSED MySQL instance. Threshold is read per-instance from
`instance_parameters.parameters->>'slow_threshold_seconds'`.

Debug-First Policy: collection failures are surfaced as
`WorkerRunResult(status="failed", error=<root cause>)` items; there is
no silent swallow, no internal retry, no mock success.
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
from db_monitor_pipeline.slow_query import (
    InstanceParameterReader,
    SLOW_QUERY_COLLECT_INTERVAL_SECONDS,
    SlowQueryWorker,
    resolve_slow_threshold_seconds,
)
from db_monitor_pipeline.worker import WorkerRunResult


@dataclass(frozen=True)
class SlowQueryCycleResult:
    results: tuple[WorkerRunResult, ...]
    scanned_instances: int
    scheduled_instances: int


@dataclass
class SlowQueryScheduler:
    """Fixed 60s cadence dispatcher for slow query collection."""

    control_plane_repository: ControlPlaneRepository
    parameter_reader: InstanceParameterReader
    worker: SlowQueryWorker
    clock: Callable[[], datetime] = field(default=utc_now)
    interval_seconds: int = SLOW_QUERY_COLLECT_INTERVAL_SECONDS
    _next_run_at: dict[str, datetime] = field(default_factory=dict)

    def run_cycle(self) -> SlowQueryCycleResult:
        instances = self.control_plane_repository.list_instances(organization_id=None)
        dispatchable = tuple(
            instance for instance in instances if _is_dispatchable(instance)
        )
        now = self.clock()
        due = tuple(instance for instance in dispatchable if self._is_due(instance, now))
        results = tuple(self._run_instance(instance, now=now) for instance in due)
        return SlowQueryCycleResult(
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
        threshold = resolve_slow_threshold_seconds(
            instance_id=instance.instance_id,
            reader=self.parameter_reader,
        )
        try:
            snapshot = self.worker.collect_once(
                instance=instance,
                slow_threshold_seconds=threshold,
            )
        except Exception as error:
            self._next_run_at[instance.instance_id] = now + timedelta(
                seconds=self.interval_seconds,
            )
            return WorkerRunResult(
                error=f"{instance.instance_id}: {error}",
                next_retry_at=None,
                processed_metrics=0,
                retry_attempt=None,
                status="failed",
            )
        self._next_run_at[instance.instance_id] = now + timedelta(
            seconds=self.interval_seconds,
        )
        return WorkerRunResult(
            error=None,
            next_retry_at=None,
            processed_metrics=len(snapshot.events),
            retry_attempt=None,
            status="processed",
        )


def _is_dispatchable(instance: MonitoredInstance) -> bool:
    if instance.engine is not DatabaseEngine.MYSQL:
        return False
    return instance.validation.status is ValidationStatus.PASSED


def reduce_slow_query_cycle_to_run_result(
    cycle: SlowQueryCycleResult,
) -> WorkerRunResult:
    """Aggregate a cycle's per-instance results into a single
    `WorkerRunResult`. Failures take precedence over successes so the
    supervisor can trip on any instance regression.
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
