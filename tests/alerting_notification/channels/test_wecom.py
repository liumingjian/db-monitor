import asyncio
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, cast

import httpx
import pytest

from db_monitor_api.alerting.notification.channels.wecom import WeComNotifier
from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)


_OCCURRED_AT = datetime(2026, 5, 4, 12, 0, tzinfo=UTC)
_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=stub"


class _FakeTransport(httpx.MockTransport):
    def __init__(self, responses: list[httpx.Response]) -> None:
        self._responses = iter(responses)
        self.requests: list[httpx.Request] = []
        super().__init__(self._handler)

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return next(self._responses)


class _ScriptedTransport(httpx.MockTransport):
    """Returns scripted responses; if a slot is an exception, raises it."""

    def __init__(self, script: list[httpx.Response | Exception]) -> None:
        self._script = iter(script)
        self.requests: list[httpx.Request] = []
        super().__init__(self._handler)

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        item = next(self._script)
        if isinstance(item, Exception):
            raise item
        return item


def _payload(
    binding_config: Mapping[str, object],
    *,
    web_link: str | None = None,
    severity: str = "critical",
) -> NotifyPayload:
    return NotifyPayload(
        rule_id="rule-1",
        rule_name="Connections saturated",
        organization_id="org-internal",
        instance_id="mysql-1",
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity=severity,
        occurred_at=_OCCURRED_AT,
        web_link=web_link,
        binding_config=binding_config,
    )


def _json_response(status: int, body: dict[str, object]) -> httpx.Response:
    return httpx.Response(status, content=json.dumps(body).encode("utf-8"))


def _ok() -> httpx.Response:
    return _json_response(200, {"errcode": 0, "errmsg": "ok"})


def _request_body(request: httpx.Request) -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(request.content.decode("utf-8")))


def _run_send(
    notifier: WeComNotifier,
    payload: NotifyPayload,
    monkeypatch: pytest.MonkeyPatch,
) -> NotifyResult:
    async def _noop_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)
    return asyncio.run(notifier.send(payload))


# ---------- payload shape ----------


def test_markdown_content_contains_required_fields() -> None:
    transport = _FakeTransport([_ok()])
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload(
        {"webhook_url": _WEBHOOK}, web_link="https://example.com/alerts/1"
    )

    asyncio.run(notifier.send(payload))

    body = _request_body(transport.requests[0])
    assert body["msgtype"] == "markdown"
    content = body["markdown"]["content"]
    assert isinstance(content, str)
    assert "[CRITICAL]" in content
    assert "Connections saturated" in content
    assert "mysql-1" in content
    assert "connections.used_rate" in content
    assert "0.95" in content
    assert "0.8" in content
    assert "https://example.com/alerts/1" in content


def test_unbound_instance_falls_back_to_placeholder() -> None:
    transport = _FakeTransport([_ok()])
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = NotifyPayload(
        rule_id="rule-1",
        rule_name="Rule",
        organization_id="org",
        instance_id=None,
        engine="mysql",
        metric_name="m",
        metric_value=1.0,
        threshold=0.5,
        severity="warning",
        occurred_at=_OCCURRED_AT,
        binding_config={"webhook_url": _WEBHOOK},
    )

    asyncio.run(notifier.send(payload))

    body = _request_body(transport.requests[0])
    assert "(unbound)" in body["markdown"]["content"]

def test_at_user_ids_renders_inline_mentions() -> None:
    transport = _FakeTransport([_ok()])
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload(
        {"webhook_url": _WEBHOOK, "at_user_ids": ["alice", "bob"]}
    )

    asyncio.run(notifier.send(payload))

    content = _request_body(transport.requests[0])["markdown"]["content"]
    assert "<@alice><@bob>" in content


def test_at_all_overrides_user_ids() -> None:
    transport = _FakeTransport([_ok()])
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload(
        {
            "webhook_url": _WEBHOOK,
            "at_all": True,
            "at_user_ids": ["alice"],
        }
    )

    asyncio.run(notifier.send(payload))

    content = _request_body(transport.requests[0])["markdown"]["content"]
    assert "<@all>" in content
    assert "<@alice>" not in content


# ---------- send + retry ----------


def test_success_on_first_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport([_ok()])
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.DELIVERED
    assert result.attempt == 1
    assert result.channel == "wecom"
    assert len(transport.requests) == 1


def test_retry_on_429_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport(
        [_json_response(429, {"errcode": 45009, "errmsg": "rate"}), _ok()]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.DELIVERED
    assert result.attempt == 2
    assert len(transport.requests) == 2


def test_exhausts_attempts_on_500s(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport(
        [_json_response(500, {}), _json_response(500, {}), _json_response(500, {})]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 3
    assert len(transport.requests) == 3
    assert "500" in (result.error or "")


def test_non_retryable_400_fails_immediately(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport(
        [_json_response(400, {"errcode": 93000, "errmsg": "invalid"})]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 1
    assert len(transport.requests) == 1


def test_invalid_errcode_is_not_retryable(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport(
        [_json_response(200, {"errcode": 93000, "errmsg": "invalid_userid"})]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 1
    assert "errcode=93000" in (result.error or "")


def test_invalid_json_response_is_not_retryable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = _FakeTransport(
        [httpx.Response(200, content=b"<html>not json</html>")]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 1
    assert "invalid json" in (result.error or "")


def test_timeout_is_retryable(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _ScriptedTransport(
        [httpx.ConnectTimeout("slow"), _ok()]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.DELIVERED
    assert result.attempt == 2
    assert len(transport.requests) == 2


def test_missing_webhook_url_returns_failed_without_http() -> None:
    transport = _FakeTransport([])
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload({})

    result = asyncio.run(notifier.send(payload))

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 1
    assert len(transport.requests) == 0
    assert "webhook_url" in (result.error or "")


# ---------- mobile follow-up ----------


def test_at_mobile_triggers_text_followup() -> None:
    transport = _FakeTransport([_ok(), _ok()])
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload(
        {"webhook_url": _WEBHOOK, "at_mobile_list": ["13800000000", "13900000000"]}
    )

    result = asyncio.run(notifier.send(payload))

    assert result.status is NotifyStatus.DELIVERED
    assert len(transport.requests) == 2
    primary = _request_body(transport.requests[0])
    follow = _request_body(transport.requests[1])
    assert primary["msgtype"] == "markdown"
    assert follow["msgtype"] == "text"
    assert follow["text"]["mentioned_mobile_list"] == [
        "13800000000",
        "13900000000",
    ]


def test_mobile_followup_failure_does_not_demote_primary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = _FakeTransport(
        [
            _ok(),
            _json_response(500, {}),
            _json_response(500, {}),
            _json_response(500, {}),
        ]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload(
        {"webhook_url": _WEBHOOK, "at_mobile_list": ["13800000000"]}
    )

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.DELIVERED
    assert result.attempt == 1
    assert len(transport.requests) == 4  # 1 primary + 3 retries on follow-up


def test_mobile_followup_skipped_when_primary_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = _FakeTransport(
        [
            _json_response(500, {}),
            _json_response(500, {}),
            _json_response(500, {}),
        ]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = WeComNotifier(http_client=client)
    payload = _payload(
        {"webhook_url": _WEBHOOK, "at_mobile_list": ["13800000000"]}
    )

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.FAILED
    assert len(transport.requests) == 3
