"""Feishu (Lark) webhook notifier.

Implements the ``Notifier`` protocol using Feishu's interactive card webhook.
Handles signing, @-mentions, and retry-with-backoff for transient failures.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)

_DEFAULT_MAX_ATTEMPTS = 3
_DEFAULT_BACKOFF: tuple[float, ...] = (1.0, 2.0, 4.0)
_DEFAULT_TIMEOUT_SECONDS = 5.0
_RETRY_STATUS_TOO_MANY = 429
_SERVER_ERROR_FLOOR = 500

_HEADER_COLORS: Mapping[str, str] = {
    "critical": "red",
    "major": "orange",
    "warning": "yellow",
}
_DEFAULT_HEADER_COLOR = "turquoise"


def _header_color(severity: str) -> str:
    return _HEADER_COLORS.get(severity.lower(), _DEFAULT_HEADER_COLOR)


def _format_instance(payload: NotifyPayload) -> str:
    return payload.instance_id if payload.instance_id else "(unbound)"


def _build_fields(payload: NotifyPayload) -> list[dict[str, Any]]:
    entries: list[tuple[str, str]] = [
        ("Instance", _format_instance(payload)),
        ("Engine", payload.engine),
        ("Metric", payload.metric_name),
        ("Value", f"{payload.metric_value}"),
        ("Threshold", f"{payload.threshold}"),
        ("Severity", payload.severity),
        ("Time", payload.occurred_at.isoformat()),
    ]
    return [
        {
            "is_short": True,
            "text": {"tag": "lark_md", "content": f"**{label}:** {value}"},
        }
        for label, value in entries
    ]


def _build_at_element(binding_config: Mapping[str, object]) -> dict[str, Any] | None:
    if bool(binding_config.get("at_all")):
        return {"tag": "div", "text": {"tag": "lark_md", "content": "<at id=all></at>"}}
    user_ids = binding_config.get("at_user_ids")
    if isinstance(user_ids, Sequence) and not isinstance(user_ids, (str, bytes)):
        ids = [str(uid) for uid in user_ids if str(uid)]
        if ids:
            content = " ".join(f"<at id={uid}></at>" for uid in ids)
            return {"tag": "div", "text": {"tag": "lark_md", "content": content}}
    return None


def _build_action(web_link: str | None) -> dict[str, Any] | None:
    if not web_link:
        return None
    return {
        "tag": "action",
        "actions": [
            {
                "tag": "button",
                "text": {"tag": "plain_text", "content": "View in Console"},
                "type": "primary",
                "url": web_link,
            }
        ],
    }


def _build_card(payload: NotifyPayload) -> dict[str, Any]:
    elements: list[dict[str, Any]] = [
        {"tag": "div", "fields": _build_fields(payload)},
    ]
    at_element = _build_at_element(payload.binding_config)
    if at_element is not None:
        elements.append(at_element)
    action = _build_action(payload.web_link)
    if action is not None:
        elements.append(action)
    title = f"[{payload.severity.upper()}] {payload.rule_name}"
    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "template": _header_color(payload.severity),
                "title": {"tag": "plain_text", "content": title},
            },
            "elements": elements,
        },
    }


def _sign(timestamp: int, secret: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def _apply_signature(body: dict[str, Any], secret: str | None) -> dict[str, Any]:
    if not secret:
        return body
    timestamp = int(time.time())
    signed = dict(body)
    signed["timestamp"] = str(timestamp)
    signed["sign"] = _sign(timestamp, secret)
    return signed


def _should_retry_status(status_code: int) -> bool:
    return status_code == _RETRY_STATUS_TOO_MANY or status_code >= _SERVER_ERROR_FLOOR


def _extract_webhook(binding_config: Mapping[str, object]) -> str:
    webhook = binding_config.get("webhook_url")
    if isinstance(webhook, str) and webhook:
        return webhook
    return ""


def _extract_secret(binding_config: Mapping[str, object]) -> str | None:
    secret = binding_config.get("secret")
    if isinstance(secret, str) and secret:
        return secret
    return None


class FeishuNotifier:
    """Primary channel for Slice 1: Feishu interactive card webhook."""

    channel_name = "feishu"

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient | None = None,
        max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
        backoff_seconds: tuple[float, ...] = _DEFAULT_BACKOFF,
        request_timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._http_client = http_client
        self._max_attempts = max_attempts
        self._backoff_seconds = backoff_seconds
        self._timeout = request_timeout_seconds

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        webhook_url = _extract_webhook(payload.binding_config)
        if not webhook_url:
            return self._failure(attempt=1, error="feishu webhook_url not configured")
        secret = _extract_secret(payload.binding_config)
        card = _build_card(payload)
        if self._http_client is not None:
            return await self._send_with_retry(
                client=self._http_client, url=webhook_url, card=card, secret=secret
            )
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            return await self._send_with_retry(
                client=client, url=webhook_url, card=card, secret=secret
            )

    async def _send_with_retry(
        self,
        *,
        client: httpx.AsyncClient,
        url: str,
        card: dict[str, Any],
        secret: str | None,
    ) -> NotifyResult:
        last_error = "unknown error"
        for attempt_index in range(self._max_attempts):
            attempt_number = attempt_index + 1
            body = _apply_signature(card, secret)
            outcome = await self._attempt_once(client=client, url=url, body=body)
            if outcome.success:
                return NotifyResult(
                    channel=self.channel_name,
                    status=NotifyStatus.DELIVERED,
                    attempt=attempt_number,
                    delivered_at=datetime.now(tz=UTC),
                    error=None,
                )
            last_error = outcome.error
            if not outcome.retryable or attempt_number >= self._max_attempts:
                return self._failure(attempt=attempt_number, error=last_error)
            await asyncio.sleep(self._backoff_seconds[attempt_index])
        return self._failure(attempt=self._max_attempts, error=last_error)

    async def _attempt_once(
        self, *, client: httpx.AsyncClient, url: str, body: dict[str, Any]
    ) -> _AttemptOutcome:
        try:
            response = await client.post(url, json=body, timeout=self._timeout)
        except httpx.TimeoutException as exc:
            return _AttemptOutcome(
                success=False, retryable=True, error=f"timeout: {exc}"
            )
        except httpx.TransportError as exc:
            return _AttemptOutcome(
                success=False, retryable=True, error=f"transport error: {exc}"
            )
        return _classify_response(response)

    def _failure(self, *, attempt: int, error: str) -> NotifyResult:
        return NotifyResult(
            channel=self.channel_name,
            status=NotifyStatus.FAILED,
            attempt=attempt,
            delivered_at=None,
            error=error,
        )


class _AttemptOutcome:
    __slots__ = ("success", "retryable", "error")

    def __init__(self, *, success: bool, retryable: bool, error: str) -> None:
        self.success = success
        self.retryable = retryable
        self.error = error


def _classify_response(response: httpx.Response) -> _AttemptOutcome:
    status_code = response.status_code
    if status_code >= 400:
        return _AttemptOutcome(
            success=False,
            retryable=_should_retry_status(status_code),
            error=f"feishu http {status_code}",
        )
    try:
        data = response.json()
    except ValueError:
        return _AttemptOutcome(
            success=False, retryable=False, error="feishu invalid json response"
        )
    code = data.get("code") if isinstance(data, dict) else None
    if code == 0:
        return _AttemptOutcome(success=True, retryable=False, error="")
    message = data.get("msg") if isinstance(data, dict) else None
    return _AttemptOutcome(
        success=False,
        retryable=False,
        error=f"feishu api code={code} msg={message}",
    )


__all__ = ["FeishuNotifier"]
