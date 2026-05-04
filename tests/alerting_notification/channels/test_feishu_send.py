import asyncio
import json
from collections.abc import Mapping
from datetime import UTC, datetime

import httpx
import pytest

from db_monitor_api.alerting.notification.channels.feishu import FeishuNotifier
from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)


_OCCURRED_AT = datetime(2026, 4, 22, 12, 0, tzinfo=UTC)
_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/test"


class _FakeTransport(httpx.MockTransport):
    def __init__(self, responses: list[httpx.Response]) -> None:
        self._responses = iter(responses)
        self.requests: list[httpx.Request] = []
        super().__init__(self._handler)

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return next(self._responses)


class _RaisingTransport(httpx.MockTransport):
    def __init__(self, exc_factory: type[Exception]) -> None:
        self._exc_factory = exc_factory
        self.requests: list[httpx.Request] = []
        super().__init__(self._handler)

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        raise self._exc_factory("boom")


def _payload(binding_config: Mapping[str, object]) -> NotifyPayload:
    return NotifyPayload(
        rule_id="rule-1",
        rule_name="Rule Name",
        organization_id="org-internal",
        instance_id="mysql-1",
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity="critical",
        occurred_at=_OCCURRED_AT,
        web_link=None,
        binding_config=binding_config,
    )


def _json_response(status: int, body: dict[str, object]) -> httpx.Response:
    return httpx.Response(status, content=json.dumps(body).encode("utf-8"))


def _run_send(
    notifier: FeishuNotifier, payload: NotifyPayload, monkeypatch: pytest.MonkeyPatch
) -> NotifyResult:
    async def _noop_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)
    return asyncio.run(notifier.send(payload))


def test_success_on_first_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport([_json_response(200, {"code": 0})])
    client = httpx.AsyncClient(transport=transport)
    notifier = FeishuNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.DELIVERED
    assert result.attempt == 1
    assert result.delivered_at is not None
    assert len(transport.requests) == 1


def test_retry_on_429_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport(
        [_json_response(429, {"code": 99991400}), _json_response(200, {"code": 0})]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = FeishuNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.DELIVERED
    assert result.attempt == 2
    assert len(transport.requests) == 2


def test_exhausts_attempts_on_500s(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport(
        [
            _json_response(500, {}),
            _json_response(500, {}),
            _json_response(500, {}),
        ]
    )
    client = httpx.AsyncClient(transport=transport)
    notifier = FeishuNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 3
    assert len(transport.requests) == 3
    assert "500" in (result.error or "")


def test_non_retryable_400_fails_immediately(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _FakeTransport([_json_response(400, {"code": 1, "msg": "bad"})])
    client = httpx.AsyncClient(transport=transport)
    notifier = FeishuNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 1
    assert len(transport.requests) == 1
    assert "400" in (result.error or "")


def test_timeout_exhausts_attempts(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _RaisingTransport(httpx.ConnectTimeout)
    client = httpx.AsyncClient(transport=transport)
    notifier = FeishuNotifier(http_client=client)
    payload = _payload({"webhook_url": _WEBHOOK})

    result = _run_send(notifier, payload, monkeypatch)

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 3
    assert len(transport.requests) == 3
    assert "timeout" in (result.error or "").lower()


def test_missing_webhook_url_returns_failed_without_http() -> None:
    transport = _FakeTransport([])
    client = httpx.AsyncClient(transport=transport)
    notifier = FeishuNotifier(http_client=client)
    payload = _payload({})

    result = asyncio.run(notifier.send(payload))

    assert result.status is NotifyStatus.FAILED
    assert result.attempt == 1
    assert len(transport.requests) == 0
    assert "webhook_url" in (result.error or "")
