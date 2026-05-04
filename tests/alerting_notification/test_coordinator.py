import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime

import pytest

from db_monitor_api.alerting.notification import (
    ChannelBinding,
    ChannelRegistry,
    DispatchCoordinator,
    InMemoryNotifyHistoryRepository,
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
    NullRuleHitSink,
    RuleHitEvent,
)

_NOW = datetime(2026, 4, 22, 14, 0, tzinfo=UTC)


class _StaticBindings:
    def __init__(self, bindings: Sequence[ChannelBinding]) -> None:
        self._bindings = tuple(bindings)

    def list_for_rule(
        self, *, organization_id: str, rule_id: str
    ) -> Sequence[ChannelBinding]:
        return tuple(b for b in self._bindings if b.rule_id == rule_id)


class _SlowNotifier:
    def __init__(self, channel_name: str, sleep_seconds: float) -> None:
        self.channel_name = channel_name
        self._sleep = sleep_seconds
        self.calls = 0

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        self.calls += 1
        await asyncio.sleep(self._sleep)
        return NotifyResult(
            channel=self.channel_name,
            status=NotifyStatus.DELIVERED,
            attempt=1,
            delivered_at=payload.occurred_at,
            error=None,
        )


def _event(rule_id: str = "rule-1") -> RuleHitEvent:
    return RuleHitEvent(
        rule_id=rule_id,
        rule_name="Too many connections",
        organization_id="org-internal",
        instance_id="mysql-1",
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity="critical",
        occurred_at=_NOW,
    )


def test_null_sink_accepts_submits_without_side_effects() -> None:
    sink = NullRuleHitSink()
    sink.submit(_event())
    sink.submit(_event())  # no exception


def test_coordinator_submit_without_running_loop_records_skipped() -> None:
    registry = ChannelRegistry()
    registry.register("feishu", _SlowNotifier("feishu", 0.0))
    bindings = _StaticBindings([ChannelBinding("rule-1", "feishu", {})])
    history = InMemoryNotifyHistoryRepository()
    coordinator = DispatchCoordinator(
        registry=registry,
        bindings=bindings,
        history=history,
    )

    coordinator.submit(_event())

    entries = history.list_entries(organization_id="org-internal")
    assert len(entries) == 1
    assert entries[0].status == "skipped"
    assert entries[0].error == "no running event loop"


def test_coordinator_submit_returns_immediately_and_processes_async() -> None:
    registry = ChannelRegistry()
    notifier = _SlowNotifier("feishu", 0.05)
    registry.register("feishu", notifier)
    bindings = _StaticBindings([ChannelBinding("rule-1", "feishu", {})])
    history = InMemoryNotifyHistoryRepository()

    async def scenario() -> None:
        coordinator = DispatchCoordinator(
            registry=registry,
            bindings=bindings,
            history=history,
        )
        start = asyncio.get_event_loop().time()
        coordinator.submit(_event())
        coordinator.submit(_event())
        elapsed = asyncio.get_event_loop().time() - start
        assert elapsed < 0.01, f"submit took {elapsed}s; must be ~instant"
        await coordinator.wait_idle()

    asyncio.run(scenario())
    entries = history.list_entries(organization_id="org-internal")
    assert len(entries) == 2
    assert all(entry.status == "delivered" for entry in entries)
    assert notifier.calls == 2


def test_coordinator_over_capacity_records_skipped_rows() -> None:
    registry = ChannelRegistry()
    # Use a blocked notifier so the task stays pending and capacity is exercised
    blocker = asyncio.Event()

    class _Blocked:
        channel_name = "feishu"

        async def send(self, payload: NotifyPayload) -> NotifyResult:
            await blocker.wait()
            return NotifyResult(
                channel="feishu",
                status=NotifyStatus.DELIVERED,
                attempt=1,
                delivered_at=payload.occurred_at,
                error=None,
            )

    registry.register("feishu", _Blocked())
    bindings = _StaticBindings([ChannelBinding("rule-1", "feishu", {})])
    history = InMemoryNotifyHistoryRepository()

    async def scenario() -> None:
        coordinator = DispatchCoordinator(
            registry=registry,
            bindings=bindings,
            history=history,
            max_concurrent_tasks=2,
        )
        coordinator.submit(_event())
        coordinator.submit(_event())
        assert coordinator.state().pending_task_count == 2
        coordinator.submit(_event())  # third should be skipped
        coordinator.submit(_event())  # fourth should be skipped
        blocker.set()
        await coordinator.wait_idle()

    asyncio.run(scenario())

    entries = history.list_entries(organization_id="org-internal", limit=500)
    statuses = sorted(entry.status for entry in entries)
    # 2 delivered + 2 skipped
    assert statuses == ["delivered", "delivered", "skipped", "skipped"]
    skipped_reasons = {entry.error for entry in entries if entry.status == "skipped"}
    assert skipped_reasons == {"coordinator at capacity"}


def test_coordinator_swallows_dispatch_exception_but_logs() -> None:
    registry = ChannelRegistry()

    class _BadNotifier:
        channel_name = "feishu"

        async def send(self, payload: NotifyPayload) -> NotifyResult:
            raise RuntimeError("boom")

    registry.register("feishu", _BadNotifier())
    bindings = _StaticBindings([ChannelBinding("rule-1", "feishu", {})])
    history = InMemoryNotifyHistoryRepository()

    async def scenario() -> None:
        coordinator = DispatchCoordinator(
            registry=registry,
            bindings=bindings,
            history=history,
        )
        coordinator.submit(_event())
        await coordinator.wait_idle()

    asyncio.run(scenario())
    entries = history.list_entries(organization_id="org-internal")
    assert len(entries) == 1
    assert entries[0].status == "failed"
    assert "RuntimeError" in (entries[0].error or "")


def test_coordinator_rejects_non_positive_max_tasks() -> None:
    registry = ChannelRegistry()
    bindings = _StaticBindings([])
    history = InMemoryNotifyHistoryRepository()
    with pytest.raises(ValueError):
        DispatchCoordinator(
            registry=registry,
            bindings=bindings,
            history=history,
            max_concurrent_tasks=0,
        )
