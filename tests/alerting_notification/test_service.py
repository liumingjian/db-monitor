import asyncio
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime

from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)
from db_monitor_api.alerting.notification.registry import ChannelRegistry
from db_monitor_api.alerting.notification.service import (
    ChannelBinding,
    RuleHitEvent,
    dispatch,
)


_NOW = datetime(2026, 4, 22, 12, 0, tzinfo=UTC)


class _StaticBindings:
    def __init__(self, bindings: Sequence[ChannelBinding]) -> None:
        self._bindings = tuple(bindings)

    def list_for_rule(
        self, *, organization_id: str, rule_id: str
    ) -> Sequence[ChannelBinding]:
        return tuple(
            binding
            for binding in self._bindings
            if binding.rule_id == rule_id
        )


class _InMemoryHistory:
    def __init__(self) -> None:
        self.records: list[tuple[NotifyPayload, NotifyResult]] = []

    def record(self, *, payload: NotifyPayload, result: NotifyResult) -> None:
        self.records.append((payload, result))


class _SuccessNotifier:
    channel_name = "feishu"

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        return NotifyResult(
            channel=self.channel_name,
            status=NotifyStatus.DELIVERED,
            attempt=1,
            delivered_at=payload.occurred_at,
            error=None,
        )


class _RaisingNotifier:
    channel_name = "smtp"

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        raise RuntimeError("smtp host unreachable")


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


def _binding(channel: str, config: Mapping[str, object] | None = None) -> ChannelBinding:
    return ChannelBinding(rule_id="rule-1", channel=channel, config=config or {})


def test_dispatch_writes_history_for_unknown_channel_and_returns_failed() -> None:
    registry = ChannelRegistry()
    bindings = _StaticBindings([_binding("feishu")])
    history = _InMemoryHistory()

    results = asyncio.run(
        dispatch(_event(), registry=registry, bindings=bindings, history=history)
    )

    assert len(results) == 1
    assert results[0].status is NotifyStatus.FAILED
    assert results[0].channel == "feishu"
    assert "feishu" in (results[0].error or "")
    assert len(history.records) == 1
    assert history.records[0][1].status is NotifyStatus.FAILED


def test_dispatch_uses_registered_notifier_and_propagates_config() -> None:
    registry = ChannelRegistry()
    registry.register("feishu", _SuccessNotifier())
    bindings = _StaticBindings([_binding("feishu", {"at_user_ids": ["u1"]})])
    history = _InMemoryHistory()

    results = asyncio.run(
        dispatch(_event(), registry=registry, bindings=bindings, history=history)
    )

    assert results[0].status is NotifyStatus.DELIVERED
    delivered_payload = history.records[0][0]
    assert delivered_payload.binding_config == {"at_user_ids": ["u1"]}


def test_dispatch_captures_channel_exception_as_failed_result() -> None:
    registry = ChannelRegistry()
    registry.register("smtp", _RaisingNotifier())
    bindings = _StaticBindings([_binding("smtp")])
    history = _InMemoryHistory()

    results = asyncio.run(
        dispatch(_event(), registry=registry, bindings=bindings, history=history)
    )

    assert results[0].status is NotifyStatus.FAILED
    assert "smtp host unreachable" in (results[0].error or "")
    assert history.records[0][1].status is NotifyStatus.FAILED


def test_dispatch_preserves_binding_order() -> None:
    registry = ChannelRegistry()
    registry.register("feishu", _SuccessNotifier())
    bindings = _StaticBindings([_binding("feishu"), _binding("smtp")])
    history = _InMemoryHistory()

    results = asyncio.run(
        dispatch(_event(), registry=registry, bindings=bindings, history=history)
    )

    channels = [result.channel for result in results]
    assert channels == ["feishu", "smtp"]
    assert [result.status for result in results] == [
        NotifyStatus.DELIVERED,
        NotifyStatus.FAILED,
    ]
