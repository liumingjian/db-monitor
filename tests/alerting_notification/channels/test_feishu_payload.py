import base64
import hashlib
import hmac
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from db_monitor_api.alerting.notification.channels.feishu import (
    _apply_signature,
    _build_card,
    _sign,
)
from db_monitor_api.alerting.notification.protocol import NotifyPayload


_OCCURRED_AT = datetime(2026, 4, 22, 12, 0, tzinfo=UTC)


def _payload(
    *,
    severity: str = "critical",
    web_link: str | None = None,
    binding_config: Mapping[str, object] | None = None,
) -> NotifyPayload:
    return NotifyPayload(
        rule_id="rule-1",
        rule_name="Rule Name",
        organization_id="org-internal",
        instance_id="mysql-1",
        engine="mysql",
        metric_name="connections.used_rate",
        metric_value=0.95,
        threshold=0.8,
        severity=severity,
        occurred_at=_OCCURRED_AT,
        web_link=web_link,
        binding_config=binding_config or {},
    )


def _expected_sign(timestamp: int, secret: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def test_sign_matches_feishu_open_platform_formula() -> None:
    timestamp = 1_700_000_000
    secret = "xxx"
    assert _sign(timestamp, secret) == _expected_sign(timestamp, secret)


def test_apply_signature_includes_timestamp_and_sign_when_secret_set() -> None:
    body: dict[str, Any] = {"msg_type": "interactive", "card": {}}
    signed = _apply_signature(body, "xxx")
    assert "timestamp" in signed
    assert "sign" in signed
    timestamp = int(signed["timestamp"])
    assert signed["sign"] == _expected_sign(timestamp, "xxx")


def test_apply_signature_omits_fields_without_secret() -> None:
    body: dict[str, Any] = {"msg_type": "interactive", "card": {}}
    assert _apply_signature(body, None) == body
    assert _apply_signature(body, "") == body


def test_card_header_title_and_color_for_critical() -> None:
    card = _build_card(_payload(severity="critical"))
    header = card["card"]["header"]
    assert header["title"]["content"] == "[CRITICAL] Rule Name"
    assert header["template"] == "red"


def test_card_header_color_for_warning_and_default() -> None:
    warning_card = _build_card(_payload(severity="warning"))
    assert warning_card["card"]["header"]["template"] == "yellow"
    info_card = _build_card(_payload(severity="info"))
    assert info_card["card"]["header"]["template"] == "turquoise"


def test_card_fields_present() -> None:
    card = _build_card(_payload())
    fields_element = card["card"]["elements"][0]
    contents = [field["text"]["content"] for field in fields_element["fields"]]
    expected_labels = ["Instance", "Engine", "Metric", "Value", "Threshold", "Severity", "Time"]
    for label in expected_labels:
        assert any(f"**{label}:**" in content for content in contents), label
    time_entry = next(c for c in contents if c.startswith("**Time:**"))
    assert _OCCURRED_AT.isoformat() in time_entry


def test_card_includes_action_button_only_when_web_link_set() -> None:
    without = _build_card(_payload(web_link=None))
    tags_without = [element["tag"] for element in without["card"]["elements"]]
    assert "action" not in tags_without

    with_link = _build_card(_payload(web_link="https://console.example/alert/1"))
    elements = with_link["card"]["elements"]
    action_elements = [e for e in elements if e["tag"] == "action"]
    assert len(action_elements) == 1
    assert action_elements[0]["actions"][0]["url"] == "https://console.example/alert/1"
