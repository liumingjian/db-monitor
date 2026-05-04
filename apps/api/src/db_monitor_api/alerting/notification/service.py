from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)
from db_monitor_api.alerting.notification.registry import (
    ChannelRegistry,
    UnknownChannelError,
)


@dataclass(frozen=True)
class RuleHitEvent:
    rule_id: str
    rule_name: str
    organization_id: str
    instance_id: str | None
    engine: str
    metric_name: str
    metric_value: float
    threshold: float
    severity: str
    occurred_at: datetime
    web_link: str | None = None


@dataclass(frozen=True)
class ChannelBinding:
    rule_id: str
    channel: str
    config: Mapping[str, object]


class BindingRepository(Protocol):
    def list_for_rule(
        self, *, organization_id: str, rule_id: str
    ) -> Sequence[ChannelBinding]: ...


class NotifyHistoryWriter(Protocol):
    def record(self, *, payload: NotifyPayload, result: NotifyResult) -> None: ...


def _build_payload(*, event: RuleHitEvent, binding: ChannelBinding) -> NotifyPayload:
    return NotifyPayload(
        rule_id=event.rule_id,
        rule_name=event.rule_name,
        organization_id=event.organization_id,
        instance_id=event.instance_id,
        engine=event.engine,
        metric_name=event.metric_name,
        metric_value=event.metric_value,
        threshold=event.threshold,
        severity=event.severity,
        occurred_at=event.occurred_at,
        web_link=event.web_link,
        binding_config=binding.config,
    )


def _failed_result(*, channel: str, error: str) -> NotifyResult:
    return NotifyResult(
        channel=channel,
        status=NotifyStatus.FAILED,
        attempt=1,
        delivered_at=None,
        error=error,
    )


async def dispatch(
    event: RuleHitEvent,
    *,
    registry: ChannelRegistry,
    bindings: BindingRepository,
    history: NotifyHistoryWriter,
) -> list[NotifyResult]:
    bindings_list = bindings.list_for_rule(
        organization_id=event.organization_id,
        rule_id=event.rule_id,
    )
    results: list[NotifyResult] = []
    for binding in bindings_list:
        payload = _build_payload(event=event, binding=binding)
        try:
            notifier = registry.get(binding.channel)
        except UnknownChannelError as error:
            result = _failed_result(channel=binding.channel, error=str(error))
        else:
            try:
                result = await notifier.send(payload)
            except Exception as error:  # noqa: BLE001 — channel boundary captures all failures
                result = NotifyResult(
                    channel=binding.channel,
                    status=NotifyStatus.FAILED,
                    attempt=1,
                    delivered_at=datetime.now(tz=UTC),
                    error=f"{type(error).__name__}: {error}",
                )
        history.record(payload=payload, result=result)
        results.append(result)
    return results
