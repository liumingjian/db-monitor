from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.message import EmailMessage

from db_monitor_api.alerting.notification.channels.smtp import SMTPNotifier
from db_monitor_api.alerting.notification.channels.smtp_settings import (
    SMTPSettings,
)
from db_monitor_api.alerting.notification.protocol import NotifyPayload


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


def _payload(
    *,
    rule_name: str = "Too many connections",
    instance_id: str | None = "mysql-1",
    web_link: str | None = None,
    binding_config: Mapping[str, object] | None = None,
) -> NotifyPayload:
    return NotifyPayload(
        rule_id="rule-1",
        rule_name=rule_name,
        organization_id="org-internal",
        instance_id=instance_id,
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity="critical",
        occurred_at=_NOW,
        web_link=web_link,
        binding_config=binding_config or {"to_addrs": ["ops@example.com"]},
    )


@dataclass
class _CapturingSender:
    messages: list[EmailMessage] = field(default_factory=list)
    from_addrs: list[str] = field(default_factory=list)
    to_addrs: list[Sequence[str]] = field(default_factory=list)
    cc_addrs: list[Sequence[str]] = field(default_factory=list)

    def send(
        self,
        *,
        from_addr: str,
        to_addrs: Sequence[str],
        cc_addrs: Sequence[str],
        message: EmailMessage,
    ) -> None:
        self.from_addrs.append(from_addr)
        self.to_addrs.append(tuple(to_addrs))
        self.cc_addrs.append(tuple(cc_addrs))
        self.messages.append(message)


def _capture(payload: NotifyPayload) -> _CapturingSender:
    sender = _CapturingSender()
    notifier = SMTPNotifier(settings=_settings(), sender=sender)
    asyncio.run(notifier.send(payload))
    return sender


def _bodies(message: EmailMessage) -> tuple[str, str]:
    plain_part = message.get_body(preferencelist=("plain",))
    html_part = message.get_body(preferencelist=("html",))
    assert plain_part is not None
    assert html_part is not None
    return plain_part.get_content(), html_part.get_content()


def test_subject_includes_severity_rule_engine_instance() -> None:
    sender = _capture(_payload())
    subject = sender.messages[0]["Subject"]

    assert "[CRITICAL]" in subject
    assert "Too many connections" in subject
    assert "mysql" in subject
    assert "mysql-1" in subject


def test_subject_prefix_prepended_when_present() -> None:
    sender = _capture(
        _payload(
            binding_config={
                "to_addrs": ["ops@example.com"],
                "subject_prefix": "[PROD]",
            }
        )
    )
    subject = sender.messages[0]["Subject"]

    assert subject.startswith("[PROD] ")
    assert "[CRITICAL]" in subject


def test_html_body_escapes_rule_name_with_script_tag() -> None:
    sender = _capture(_payload(rule_name="<script>alert(1)</script>"))
    _, html_body = _bodies(sender.messages[0])

    assert "<script>alert(1)</script>" not in html_body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_body


def test_html_body_is_valid_structure_with_table() -> None:
    sender = _capture(_payload())
    _, html_body = _bodies(sender.messages[0])

    assert html_body.startswith("<html>")
    assert html_body.rstrip().endswith("</html>")
    assert "<table" in html_body


def test_plaintext_body_contains_named_fields() -> None:
    sender = _capture(_payload())
    plain_body, _ = _bodies(sender.messages[0])

    assert "Rule: Too many connections" in plain_body
    assert "Severity: critical" in plain_body
    assert "Threshold: 0.8" in plain_body


def test_html_omits_link_anchor_when_web_link_absent() -> None:
    sender = _capture(_payload(web_link=None))
    _, html_body = _bodies(sender.messages[0])

    assert "<a href" not in html_body


def test_html_includes_escaped_anchor_when_web_link_present() -> None:
    link = "https://alerts.example.com/rule?x=1&y=2"
    sender = _capture(_payload(web_link=link))
    _, html_body = _bodies(sender.messages[0])

    assert '<a href="https://alerts.example.com/rule?x=1&amp;y=2"' in html_body
