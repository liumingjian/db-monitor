from collections.abc import Sequence
from datetime import UTC, datetime

from db_monitor_api.alerting.notification.protocol import (
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
)
from db_monitor_api.alerting.notification.registry import (
    ChannelRegistry,
    UnknownChannelError,
)
from db_monitor_api.alerting.notification.service import (
    BindingRepository,
    ChannelBinding,
    NotifyHistoryWriter,
    RuleHitEvent,
)

DEFAULT_PRIMARY_CHANNEL = "feishu"
DEFAULT_FALLBACK_CHANNEL = "smtp"


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


async def _send_one(
    *,
    event: RuleHitEvent,
    binding: ChannelBinding,
    registry: ChannelRegistry,
    history: NotifyHistoryWriter,
) -> NotifyResult:
    payload = _build_payload(event=event, binding=binding)
    try:
        notifier = registry.get(binding.channel)
    except UnknownChannelError as error:
        result = NotifyResult(
            channel=binding.channel,
            status=NotifyStatus.FAILED,
            attempt=1,
            delivered_at=None,
            error=str(error),
        )
    else:
        try:
            result = await notifier.send(payload)
        except Exception as error:  # noqa: BLE001 — channel boundary
            result = NotifyResult(
                channel=binding.channel,
                status=NotifyStatus.FAILED,
                attempt=1,
                delivered_at=datetime.now(tz=UTC),
                error=f"{type(error).__name__}: {error}",
            )
    history.record(payload=payload, result=result)
    return result


def _split_bindings(
    *,
    all_bindings: Sequence[ChannelBinding],
    primary_channel: str,
    fallback_channel: str,
) -> tuple[ChannelBinding | None, ChannelBinding | None, tuple[ChannelBinding, ...]]:
    primary: ChannelBinding | None = None
    fallback: ChannelBinding | None = None
    others: list[ChannelBinding] = []
    for binding in all_bindings:
        if binding.channel == primary_channel and primary is None:
            primary = binding
        elif binding.channel == fallback_channel and fallback is None:
            fallback = binding
        else:
            others.append(binding)
    return primary, fallback, tuple(others)


async def dispatch_with_fallback(
    event: RuleHitEvent,
    *,
    registry: ChannelRegistry,
    bindings: BindingRepository,
    history: NotifyHistoryWriter,
    primary_channel: str = DEFAULT_PRIMARY_CHANNEL,
    fallback_channel: str = DEFAULT_FALLBACK_CHANNEL,
) -> list[NotifyResult]:
    all_bindings = tuple(
        bindings.list_for_rule(
            organization_id=event.organization_id,
            rule_id=event.rule_id,
        )
    )
    primary, fallback, others = _split_bindings(
        all_bindings=all_bindings,
        primary_channel=primary_channel,
        fallback_channel=fallback_channel,
    )
    results: list[NotifyResult] = []
    primary_failed = False
    if primary is not None:
        primary_result = await _send_one(
            event=event,
            binding=primary,
            registry=registry,
            history=history,
        )
        results.append(primary_result)
        primary_failed = primary_result.status is NotifyStatus.FAILED
    if fallback is not None and (primary is None or primary_failed):
        fallback_result = await _send_one(
            event=event,
            binding=fallback,
            registry=registry,
            history=history,
        )
        results.append(fallback_result)
    for binding in others:
        results.append(
            await _send_one(
                event=event,
                binding=binding,
                registry=registry,
                history=history,
            )
        )
    return results
