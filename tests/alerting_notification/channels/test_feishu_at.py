from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from db_monitor_api.alerting.notification.channels.feishu import _build_card
from db_monitor_api.alerting.notification.protocol import NotifyPayload


_OCCURRED_AT = datetime(2026, 4, 22, 12, 0, tzinfo=UTC)


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
        binding_config=binding_config,
    )


def _at_text_elements(card: dict[str, Any]) -> list[str]:
    contents: list[str] = []
    for element in card["card"]["elements"]:
        if element.get("tag") != "div":
            continue
        text = element.get("text")
        if isinstance(text, dict) and "content" in text:
            contents.append(str(text["content"]))
    return contents


def test_at_all_renders_all_marker() -> None:
    card = _build_card(_payload({"at_all": True}))
    contents = _at_text_elements(card)
    assert any("<at id=all></at>" in content for content in contents)


def test_at_user_ids_renders_each_user() -> None:
    card = _build_card(_payload({"at_user_ids": ["u1", "u2"]}))
    contents = _at_text_elements(card)
    combined = " ".join(contents)
    assert "<at id=u1></at>" in combined
    assert "<at id=u2></at>" in combined


def test_no_at_config_emits_no_at_element() -> None:
    card = _build_card(_payload({}))
    contents = _at_text_elements(card)
    assert not any("<at id=" in content for content in contents)


def test_empty_at_user_ids_emits_no_at_element() -> None:
    card = _build_card(_payload({"at_user_ids": []}))
    contents = _at_text_elements(card)
    assert not any("<at id=" in content for content in contents)


def test_at_all_takes_precedence_over_user_ids() -> None:
    card = _build_card(_payload({"at_all": True, "at_user_ids": ["u1"]}))
    contents = _at_text_elements(card)
    assert any("<at id=all></at>" in content for content in contents)
    assert not any("<at id=u1></at>" in content for content in contents)
