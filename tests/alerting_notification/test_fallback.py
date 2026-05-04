import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime

from db_monitor_api.alerting.notification import (
    ChannelBinding,
    ChannelRegistry,
    InMemoryNotifyHistoryRepository,
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
    RuleHitEvent,
    dispatch_with_fallback,
)

_NOW = datetime(2026, 4, 22, 14, 0, tzinfo=UTC)


class _StaticBindings:
    def __init__(self, bindings: Sequence[ChannelBinding]) -> None:
        self._bindings = tuple(bindings)

    def list_for_rule(
        self, *, organization_id: str, rule_id: str
    ) -> Sequence[ChannelBinding]:
        return tuple(
            binding for binding in self._bindings if binding.rule_id == rule_id
        )


class _SuccessNotifier:
    def __init__(self, channel_name: str) -> None:
        self.channel_name = channel_name
        self.calls = 0

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        self.calls += 1
        return NotifyResult(
            channel=self.channel_name,
            status=NotifyStatus.DELIVERED,
            attempt=1,
            delivered_at=payload.occurred_at,
            error=None,
        )


class _FailNotifier:
    def __init__(self, channel_name: str) -> None:
        self.channel_name = channel_name
        self.calls = 0

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        self.calls += 1
        return NotifyResult(
            channel=self.channel_name,
            status=NotifyStatus.FAILED,
            attempt=3,
            delivered_at=None,
            error="simulated",
        )


def _event(rule_id: str = "rule-1") -> RuleHitEvent:
    return RuleHitEvent(
        rule_id=rule_id,
        rule_name="Connections saturated",
        organization_id="org-internal",
        instance_id="mysql-1",
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity="critical",
        occurred_at=_NOW,
    )


def _binding(channel: str) -> ChannelBinding:
    return ChannelBinding(rule_id="rule-1", channel=channel, config={})


def test_fallback_triggered_when_primary_fails() -> None:
    registry = ChannelRegistry()
    feishu = _FailNotifier("feishu")
    smtp = _SuccessNotifier("smtp")
    registry.register("feishu", feishu)
    registry.register("smtp", smtp)
    bindings = _StaticBindings([_binding("feishu"), _binding("smtp")])
    history = InMemoryNotifyHistoryRepository()

    results = asyncio.run(
        dispatch_with_fallback(
            _event(),
            registry=registry,
            bindings=bindings,
            history=history,
        )
    )

    assert len(results) == 2
    assert [r.channel for r in results] == ["feishu", "smtp"]
    assert results[0].status is NotifyStatus.FAILED
    assert results[1].status is NotifyStatus.DELIVERED
    entries = history.list_entries(organization_id="org-internal")
    assert {entry.channel for entry in entries} == {"feishu", "smtp"}


def test_fallback_skipped_when_primary_succeeds() -> None:
    registry = ChannelRegistry()
    feishu = _SuccessNotifier("feishu")
    smtp = _SuccessNotifier("smtp")
    registry.register("feishu", feishu)
    registry.register("smtp", smtp)
    bindings = _StaticBindings([_binding("feishu"), _binding("smtp")])
    history = InMemoryNotifyHistoryRepository()

    results = asyncio.run(
        dispatch_with_fallback(
            _event(),
            registry=registry,
            bindings=bindings,
            history=history,
        )
    )

    assert len(results) == 1
    assert results[0].channel == "feishu"
    assert smtp.calls == 0


def test_fallback_used_directly_when_no_primary_binding() -> None:
    registry = ChannelRegistry()
    smtp = _SuccessNotifier("smtp")
    registry.register("smtp", smtp)
    bindings = _StaticBindings([_binding("smtp")])
    history = InMemoryNotifyHistoryRepository()

    results = asyncio.run(
        dispatch_with_fallback(
            _event(),
            registry=registry,
            bindings=bindings,
            history=history,
        )
    )

    assert len(results) == 1
    assert results[0].channel == "smtp"
    assert results[0].status is NotifyStatus.DELIVERED


def test_fallback_other_channels_dispatched_regardless() -> None:
    registry = ChannelRegistry()
    feishu = _SuccessNotifier("feishu")
    wecom = _SuccessNotifier("wecom")
    registry.register("feishu", feishu)
    registry.register("wecom", wecom)
    bindings = _StaticBindings([_binding("feishu"), _binding("wecom")])
    history = InMemoryNotifyHistoryRepository()

    results = asyncio.run(
        dispatch_with_fallback(
            _event(),
            registry=registry,
            bindings=bindings,
            history=history,
        )
    )

    assert {r.channel for r in results} == {"feishu", "wecom"}


def test_fallback_records_two_history_rows_when_both_fail() -> None:
    registry = ChannelRegistry()
    registry.register("feishu", _FailNotifier("feishu"))
    registry.register("smtp", _FailNotifier("smtp"))
    bindings = _StaticBindings([_binding("feishu"), _binding("smtp")])
    history = InMemoryNotifyHistoryRepository()

    results = asyncio.run(
        dispatch_with_fallback(
            _event(),
            registry=registry,
            bindings=bindings,
            history=history,
        )
    )

    assert [r.status for r in results] == [NotifyStatus.FAILED, NotifyStatus.FAILED]
    entries = history.list_entries(organization_id="org-internal")
    assert len(entries) == 2
    assert {entry.status for entry in entries} == {"failed"}
