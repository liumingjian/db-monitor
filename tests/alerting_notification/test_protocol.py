from datetime import UTC, datetime

from db_monitor_api.alerting.notification.protocol import (
    Notifier,
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)


def test_notify_payload_is_frozen_and_defaults_empty_config() -> None:
    payload = NotifyPayload(
        rule_id="rule-1",
        rule_name="Too many connections",
        organization_id="org-internal",
        instance_id="mysql-1",
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity="critical",
        occurred_at=datetime(2026, 4, 22, 12, 0, tzinfo=UTC),
    )
    assert payload.binding_config == {}
    assert payload.web_link is None


def test_notify_result_captures_delivery_fields() -> None:
    result = NotifyResult(
        channel="feishu",
        status=NotifyStatus.DELIVERED,
        attempt=2,
        delivered_at=datetime(2026, 4, 22, 12, 0, 3, tzinfo=UTC),
        error=None,
    )
    assert result.status is NotifyStatus.DELIVERED
    assert result.attempt == 2
    assert result.error is None


class _StubNotifier:
    channel_name = "stub"

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        return NotifyResult(
            channel=self.channel_name,
            status=NotifyStatus.DELIVERED,
            attempt=1,
            delivered_at=payload.occurred_at,
            error=None,
        )


def test_notifier_protocol_is_runtime_checkable() -> None:
    assert isinstance(_StubNotifier(), Notifier)
