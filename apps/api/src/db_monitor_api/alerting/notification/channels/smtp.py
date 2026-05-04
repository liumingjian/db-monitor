"""SMTP fallback notifier.

Implements the :class:`Notifier` protocol over stdlib ``smtplib``. The notifier
builds a ``multipart/alternative`` message carrying both a plaintext and an
HTML rendering of the payload and delegates the network send to a small
``_SMTPSender`` collaborator so tests can inject a fake transport.
"""

from __future__ import annotations

import asyncio
import html
import smtplib
from collections.abc import Sequence
from datetime import UTC, datetime
from email.message import EmailMessage
from typing import Protocol

from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)

from .smtp_settings import SMTPSettings

_CHANNEL_NAME = "smtp"
_NO_INSTANCE_PLACEHOLDER = "(no-instance)"
_EMPTY_FIELD_PLACEHOLDER = "—"


class _SMTPSender(Protocol):
    def send(
        self,
        *,
        from_addr: str,
        to_addrs: Sequence[str],
        cc_addrs: Sequence[str],
        message: EmailMessage,
    ) -> None: ...


class _StdlibSMTPSender:
    """Default sender using stdlib smtplib run inside ``asyncio.to_thread``."""

    def __init__(self, settings: SMTPSettings) -> None:
        self._settings = settings

    def send(
        self,
        *,
        from_addr: str,
        to_addrs: Sequence[str],
        cc_addrs: Sequence[str],
        message: EmailMessage,
    ) -> None:
        recipients = list(to_addrs) + list(cc_addrs)
        with self._open_client() as client:
            if self._settings.username and self._settings.password:
                client.login(self._settings.username, self._settings.password)
            client.send_message(message, from_addr=from_addr, to_addrs=recipients)

    def _open_client(self) -> smtplib.SMTP:
        settings = self._settings
        if settings.use_tls:
            return smtplib.SMTP_SSL(
                host=settings.host,
                port=settings.port,
                timeout=settings.timeout_seconds,
            )
        return smtplib.SMTP(
            host=settings.host,
            port=settings.port,
            timeout=settings.timeout_seconds,
        )


def _coerce_str_list(raw: object) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, Sequence):
        return [str(item) for item in raw]
    return []


def _optional_str(raw: object) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _instance_label(payload: NotifyPayload) -> str:
    return payload.instance_id or _NO_INSTANCE_PLACEHOLDER


def _build_subject(payload: NotifyPayload, prefix: str | None) -> str:
    core = (
        f"[{payload.severity.upper()}] {payload.rule_name} "
        f"— {payload.engine} {_instance_label(payload)}"
    )
    if prefix:
        return f"{prefix} {core}"
    return core


def _field_rows(payload: NotifyPayload) -> list[tuple[str, str]]:
    instance_display = payload.instance_id or _EMPTY_FIELD_PLACEHOLDER
    rows: list[tuple[str, str]] = [
        ("Rule", payload.rule_name),
        ("Rule ID", payload.rule_id),
        ("Severity", payload.severity),
        ("Engine", payload.engine),
        ("Instance", instance_display),
        ("Metric", payload.metric_name),
        ("Value", str(payload.metric_value)),
        ("Threshold", str(payload.threshold)),
        ("Time", payload.occurred_at.isoformat()),
    ]
    if payload.web_link is not None:
        rows.append(("Web Link", payload.web_link))
    return rows


def _render_plaintext(payload: NotifyPayload) -> str:
    lines = [f"{name}: {value}" for name, value in _field_rows(payload)]
    return "\n".join(lines) + "\n"


def _render_html_row(name: str, value: str, *, is_link: bool) -> str:
    escaped_name = html.escape(name)
    escaped_value = html.escape(value)
    if is_link:
        cell = f'<a href="{escaped_value}">{escaped_value}</a>'
    else:
        cell = escaped_value
    return f"<tr><th align=\"left\">{escaped_name}</th><td>{cell}</td></tr>"


def _render_html(payload: NotifyPayload) -> str:
    rows_html = "".join(
        _render_html_row(name, value, is_link=(name == "Web Link"))
        for name, value in _field_rows(payload)
    )
    return (
        "<html><body>"
        '<table border="1" cellpadding="6" cellspacing="0">'
        f"{rows_html}"
        "</table>"
        "</body></html>"
    )


def _build_message(
    *,
    from_addr: str,
    to_addrs: Sequence[str],
    cc_addrs: Sequence[str],
    subject: str,
    payload: NotifyPayload,
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = from_addr
    message["To"] = ", ".join(to_addrs)
    if cc_addrs:
        message["Cc"] = ", ".join(cc_addrs)
    message.set_content(_render_plaintext(payload))
    message.add_alternative(_render_html(payload), subtype="html")
    return message


def _failed(error: str) -> NotifyResult:
    return NotifyResult(
        channel=_CHANNEL_NAME,
        status=NotifyStatus.FAILED,
        attempt=1,
        delivered_at=None,
        error=error,
    )


def _delivered() -> NotifyResult:
    return NotifyResult(
        channel=_CHANNEL_NAME,
        status=NotifyStatus.DELIVERED,
        attempt=1,
        delivered_at=datetime.now(UTC),
        error=None,
    )


class SMTPNotifier:
    channel_name = _CHANNEL_NAME

    def __init__(
        self,
        *,
        settings: SMTPSettings,
        sender: _SMTPSender | None = None,
    ) -> None:
        self._settings = settings
        self._sender: _SMTPSender = sender or _StdlibSMTPSender(settings)

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        config = payload.binding_config
        to_addrs = _coerce_str_list(config.get("to_addrs"))
        if not to_addrs:
            return _failed("smtp to_addrs not configured")
        cc_addrs = _coerce_str_list(config.get("cc_addrs"))
        subject_prefix = _optional_str(config.get("subject_prefix"))
        subject = _build_subject(payload, subject_prefix)
        message = _build_message(
            from_addr=self._settings.from_addr,
            to_addrs=to_addrs,
            cc_addrs=cc_addrs,
            subject=subject,
            payload=payload,
        )
        try:
            await asyncio.to_thread(
                self._sender.send,
                from_addr=self._settings.from_addr,
                to_addrs=to_addrs,
                cc_addrs=cc_addrs,
                message=message,
            )
        except (smtplib.SMTPException, OSError, TimeoutError) as exc:
            return _failed(f"{type(exc).__name__}: {exc}")
        return _delivered()


__all__ = ["SMTPNotifier"]
