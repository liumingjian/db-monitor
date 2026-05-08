"""WeCom (企业微信) group-bot webhook notifier.

Implements the ``Notifier`` protocol against the WeCom group-bot webhook
endpoint. Primary message uses ``msgtype=markdown`` so that ``<@userid>``
mentions render inline. ``at_mobile_list`` is delivered as a separate
``msgtype=text`` follow-up because WeCom only honours
``mentioned_mobile_list`` in text messages — the mobile follow-up is
best-effort and never demotes the primary ``NotifyResult``.
"""

from __future__ import annotations

import asyncio
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


def _format_instance(payload: NotifyPayload) -> str:
    return payload.instance_id if payload.instance_id else "(unbound)"


def _string_sequence(value: object) -> tuple[str, ...]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return tuple(str(item) for item in value if str(item))
    return ()


def _at_segment(binding_config: Mapping[str, object]) -> str:
    if bool(binding_config.get("at_all")):
        return "<@all>"
    user_ids = _string_sequence(binding_config.get("at_user_ids"))
    if not user_ids:
        return ""
    return "".join(f"<@{uid}>" for uid in user_ids)


def _build_markdown_content(payload: NotifyPayload) -> str:
    title = f"**[{payload.severity.upper()}] {payload.rule_name}**"
    fields = [
        f"- 实例：{_format_instance(payload)}",
        f"- 引擎：{payload.engine}",
        f"- 指标：{payload.metric_name}",
        f"- 命中值：{payload.metric_value}",
        f"- 阈值：{payload.threshold}",
        f"- 时间：{payload.occurred_at.isoformat()}",
    ]
    lines = [title, *fields]
    if payload.web_link:
        lines.append(f"[查看详情]({payload.web_link})")
    at_segment = _at_segment(payload.binding_config)
    if at_segment:
        lines.append(at_segment)
    return "\n".join(lines)


def _build_markdown_body(payload: NotifyPayload) -> dict[str, Any]:
    return {
        "msgtype": "markdown",
        "markdown": {"content": _build_markdown_content(payload)},
    }


def _build_mobile_text_body(
    *, payload: NotifyPayload, mobile_list: tuple[str, ...]
) -> dict[str, Any]:
    short = f"[{payload.severity.upper()}] {payload.rule_name} @ {_format_instance(payload)}"
    return {
        "msgtype": "text",
        "text": {"content": short, "mentioned_mobile_list": list(mobile_list)},
    }


def _should_retry_status(status_code: int) -> bool:
    return status_code == _RETRY_STATUS_TOO_MANY or status_code >= _SERVER_ERROR_FLOOR


def _extract_webhook(binding_config: Mapping[str, object]) -> str:
    webhook = binding_config.get("webhook_url")
    if isinstance(webhook, str) and webhook:
        return webhook
    return ""


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
            error=f"wecom http {status_code}",
        )
    try:
        data = response.json()
    except ValueError:
        return _AttemptOutcome(
            success=False, retryable=False, error="wecom invalid json response"
        )
    code = data.get("errcode") if isinstance(data, dict) else None
    if code == 0:
        return _AttemptOutcome(success=True, retryable=False, error="")
    message = data.get("errmsg") if isinstance(data, dict) else None
    return _AttemptOutcome(
        success=False,
        retryable=False,
        error=f"wecom api errcode={code} errmsg={message}",
    )


class WeComNotifier:
    """Slice 2 child #1: WeCom group-bot webhook notifier."""

    channel_name = "wecom"

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
            return self._failure(attempt=1, error="wecom webhook_url not configured")
        markdown_body = _build_markdown_body(payload)
        mobile_list = _string_sequence(payload.binding_config.get("at_mobile_list"))
        if self._http_client is not None:
            return await self._send_all(
                client=self._http_client,
                url=webhook_url,
                payload=payload,
                markdown_body=markdown_body,
                mobile_list=mobile_list,
            )
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            return await self._send_all(
                client=client,
                url=webhook_url,
                payload=payload,
                markdown_body=markdown_body,
                mobile_list=mobile_list,
            )

    async def _send_all(
        self,
        *,
        client: httpx.AsyncClient,
        url: str,
        payload: NotifyPayload,
        markdown_body: dict[str, Any],
        mobile_list: tuple[str, ...],
    ) -> NotifyResult:
        primary = await self._send_with_retry(
            client=client, url=url, body=markdown_body
        )
        if primary.status is NotifyStatus.DELIVERED and mobile_list:
            mobile_body = _build_mobile_text_body(
                payload=payload, mobile_list=mobile_list
            )
            await self._send_with_retry(client=client, url=url, body=mobile_body)
        return primary

    async def _send_with_retry(
        self,
        *,
        client: httpx.AsyncClient,
        url: str,
        body: dict[str, Any],
    ) -> NotifyResult:
        last_error = "unknown error"
        for attempt_index in range(self._max_attempts):
            attempt_number = attempt_index + 1
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


__all__ = ["WeComNotifier"]
