from __future__ import annotations

import asyncio
import smtplib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.message import EmailMessage

from db_monitor_api.alerting.notification.channels.smtp import SMTPNotifier
from db_monitor_api.alerting.notification.channels.smtp_settings import (
    SMTPSettings,
)
from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyStatus,
)


_NOW = datetime(2026, 4, 22, 12, 0, tzinfo=UTC)


def _settings() -> SMTPSettings:
    return SMTPSettings(
        host="mail.example.com",
        port=465,
        username=None,
        password=None,
        from_addr="alerts@example.com",
        use_tls=True,
    )


def _payload(binding_config: Mapping[str, object]) -> NotifyPayload:
    return NotifyPayload(
        rule_id="rule-1",
        rule_name="Too many connections",
        organization_id="org-internal",
        instance_id="mysql-1",
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity="critical",
        occurred_at=_NOW,
        binding_config=binding_config,
    )


@dataclass
class _RecordingSender:
    calls: int = 0
    last_from: str | None = None
    last_to: tuple[str, ...] = ()
    last_cc: tuple[str, ...] = ()

    def send(
        self,
        *,
        from_addr: str,
        to_addrs: Sequence[str],
        cc_addrs: Sequence[str],
        message: EmailMessage,
    ) -> None:
        self.calls += 1
        self.last_from = from_addr
        self.last_to = tuple(to_addrs)
        self.last_cc = tuple(cc_addrs)


@dataclass
class _RaisingSender:
    exc: BaseException
    calls: int = 0

    def send(
        self,
        *,
        from_addr: str,
        to_addrs: Sequence[str],
        cc_addrs: Sequence[str],
        message: EmailMessage,
    ) -> None:
        self.calls += 1
        raise self.exc


@dataclass
class _NeverCalledSender:
    calls: int = 0
    invocations: list[object] = field(default_factory=list)

    def send(
        self,
        *,
        from_addr: str,
        to_addrs: Sequence[str],
        cc_addrs: Sequence[str],
        message: EmailMessage,
    ) -> None:
        self.calls += 1
        self.invocations.append(message)


def test_send_returns_delivered_and_invokes_sender_once() -> None:
    sender = _RecordingSender()
    notifier = SMTPNotifier(settings=_settings(), sender=sender)

    result = asyncio.run(
        notifier.send(_payload({"to_addrs": ["ops@example.com"]}))
    )

    assert result.status is NotifyStatus.DELIVERED
    assert result.channel == "smtp"
    assert result.attempt == 1
    assert result.delivered_at is not None
    assert result.error is None
    assert sender.calls == 1
    assert sender.last_from == "alerts@example.com"
    assert sender.last_to == ("ops@example.com",)


def test_send_returns_failed_when_sender_raises_smtp_exception() -> None:
    sender = _RaisingSender(smtplib.SMTPException("boom"))
    notifier = SMTPNotifier(settings=_settings(), sender=sender)

    result = asyncio.run(
        notifier.send(_payload({"to_addrs": ["ops@example.com"]}))
    )

    assert result.status is NotifyStatus.FAILED
    assert result.delivered_at is None
    assert "SMTPException" in (result.error or "")
    assert "boom" in (result.error or "")
    assert sender.calls == 1


def test_send_returns_failed_without_calling_sender_when_to_addrs_missing() -> None:
    sender = _NeverCalledSender()
    notifier = SMTPNotifier(settings=_settings(), sender=sender)

    result = asyncio.run(notifier.send(_payload({})))

    assert result.status is NotifyStatus.FAILED
    assert result.error == "smtp to_addrs not configured"
    assert sender.calls == 0


def test_send_forwards_cc_addrs_when_present() -> None:
    sender = _RecordingSender()
    notifier = SMTPNotifier(settings=_settings(), sender=sender)

    result = asyncio.run(
        notifier.send(
            _payload(
                {
                    "to_addrs": ["ops@example.com"],
                    "cc_addrs": ["lead@example.com", "audit@example.com"],
                }
            )
        )
    )

    assert result.status is NotifyStatus.DELIVERED
    assert sender.last_to == ("ops@example.com",)
    assert sender.last_cc == ("lead@example.com", "audit@example.com")
