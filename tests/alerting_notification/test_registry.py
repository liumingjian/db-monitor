from datetime import UTC, datetime

import pytest

from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)
from db_monitor_api.alerting.notification.registry import (
    ChannelAlreadyRegisteredError,
    ChannelRegistry,
    UnknownChannelError,
)


class _StubNotifier:
    def __init__(self, name: str) -> None:
        self.channel_name = name

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        return NotifyResult(
            channel=self.channel_name,
            status=NotifyStatus.DELIVERED,
            attempt=1,
            delivered_at=datetime.now(tz=UTC),
            error=None,
        )


def test_register_and_get_channel() -> None:
    registry = ChannelRegistry()
    stub = _StubNotifier("feishu")
    registry.register("feishu", stub)
    assert registry.has("feishu") is True
    assert registry.get("feishu") is stub


def test_register_twice_raises() -> None:
    registry = ChannelRegistry()
    registry.register("smtp", _StubNotifier("smtp"))
    with pytest.raises(ChannelAlreadyRegisteredError) as excinfo:
        registry.register("smtp", _StubNotifier("smtp"))
    assert excinfo.value.channel == "smtp"


def test_replace_allows_override_without_error() -> None:
    registry = ChannelRegistry()
    first = _StubNotifier("feishu")
    second = _StubNotifier("feishu")
    registry.register("feishu", first)
    registry.replace("feishu", second)
    assert registry.get("feishu") is second


def test_get_unknown_channel_raises() -> None:
    registry = ChannelRegistry()
    with pytest.raises(UnknownChannelError) as excinfo:
        registry.get("wecom")
    assert excinfo.value.channel == "wecom"


def test_names_returns_sorted_tuple() -> None:
    registry = ChannelRegistry()
    registry.register("smtp", _StubNotifier("smtp"))
    registry.register("feishu", _StubNotifier("feishu"))
    assert registry.names() == ("feishu", "smtp")
