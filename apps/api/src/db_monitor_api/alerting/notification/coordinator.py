import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from db_monitor_api.alerting.notification.fallback import dispatch_with_fallback
from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)
from db_monitor_api.alerting.notification.registry import ChannelRegistry
from db_monitor_api.alerting.notification.repository import NotifyHistoryRepository
from db_monitor_api.alerting.notification.service import (
    BindingRepository,
    ChannelBinding,
    RuleHitEvent,
)

_COORDINATOR_DEFAULT_MAX_TASKS = 128
_COORDINATOR_LOGGER = logging.getLogger("db_monitor_api.alerting.notification.coordinator")


def _default_clock() -> datetime:
    return datetime.now(tz=UTC)


class RuleHitSink(Protocol):
    def submit(self, event: RuleHitEvent) -> None: ...


class NullRuleHitSink:
    def submit(self, event: RuleHitEvent) -> None:
        return None


@dataclass(frozen=True)
class CoordinatorState:
    pending_task_count: int
    max_tasks: int


class DispatchCoordinator:
    def __init__(
        self,
        *,
        registry: ChannelRegistry,
        bindings: BindingRepository,
        history: NotifyHistoryRepository,
        max_concurrent_tasks: int = _COORDINATOR_DEFAULT_MAX_TASKS,
        loop: asyncio.AbstractEventLoop | None = None,
        clock: Callable[[], datetime] = _default_clock,
    ) -> None:
        if max_concurrent_tasks <= 0:
            raise ValueError("max_concurrent_tasks must be positive")
        self._registry = registry
        self._bindings = bindings
        self._history = history
        self._max_tasks = max_concurrent_tasks
        self._loop = loop
        self._clock = clock
        self._tasks: set[asyncio.Task[None]] = set()

    def submit(self, event: RuleHitEvent) -> None:
        loop = self._resolve_loop()
        if loop is None:
            self._record_skipped(event=event, reason="no running event loop")
            return
        if len(self._tasks) >= self._max_tasks:
            self._record_skipped(event=event, reason="coordinator at capacity")
            return
        task = loop.create_task(self._run_dispatch(event))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    def state(self) -> CoordinatorState:
        return CoordinatorState(
            pending_task_count=len(self._tasks),
            max_tasks=self._max_tasks,
        )

    async def wait_idle(self) -> None:
        while self._tasks:
            pending = tuple(self._tasks)
            await asyncio.gather(*pending, return_exceptions=True)

    def _resolve_loop(self) -> asyncio.AbstractEventLoop | None:
        if self._loop is not None:
            return self._loop
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return None

    async def _run_dispatch(self, event: RuleHitEvent) -> None:
        try:
            await dispatch_with_fallback(
                event,
                registry=self._registry,
                bindings=self._bindings,
                history=self._history,
            )
        except Exception:
            _COORDINATOR_LOGGER.exception(
                "notifier.dispatch.unhandled rule_id=%s", event.rule_id
            )

    def _record_skipped(self, *, event: RuleHitEvent, reason: str) -> None:
        for binding in self._bindings.list_for_rule(
            organization_id=event.organization_id,
            rule_id=event.rule_id,
        ):
            payload = _payload_from_binding(event=event, binding=binding)
            result = NotifyResult(
                channel=binding.channel,
                status=NotifyStatus.SKIPPED,
                attempt=1,
                delivered_at=None,
                error=reason,
            )
            self._history.record(payload=payload, result=result)


def _payload_from_binding(
    *, event: RuleHitEvent, binding: ChannelBinding
) -> NotifyPayload:
    return NotifyPayload(
        rule_id=event.rule_id,
        rule_name=event.rule_name,
        organization_id=event.organization_id,
        instance_id=event.instance_id,
        engine=event.engine,
        metric_name=event.metric_name,
        metric_value=event.metric_value,
        threshold=event.threshold,
        severity=event.severity,
        occurred_at=event.occurred_at,
        web_link=event.web_link,
        binding_config=binding.config,
    )
