"""Backpressure guard: slow sink must not inflate evaluate_samples latency.

Epic 16 child #4 accepts the end-to-end dispatch coordinator if the rule engine
stays free of backpressure (p95 within 25% of baseline, or baseline + 50 ms).
"""

import asyncio
import time

from db_monitor_api.alerting.domain import RuleOperator, RuleSeverity
from db_monitor_api.alerting.notification import (
    ChannelRegistry,
    DispatchCoordinator,
    InMemoryBindingRepository,
    InMemoryNotifyHistoryRepository,
    NotifyPayload,
    NotifyResult,
    NotifyStatus,
    RuleHitSink,
)
from db_monitor_api.alerting.notifier import InMemoryNotifier
from db_monitor_api.alerting.repository import InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertingService
from db_monitor_api.auth.repository import InMemoryAuditRepository
from db_monitor_api.auth.service import AuditService
from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind, MetricSample
from tests.analytics_support import build_sample, sample_anchor


_SLOW_CHANNEL_SLEEP = 0.5
_SAMPLE_ITERATIONS = 10


class _SlowNotifier:
    channel_name = "feishu"

    def __init__(self, sleep_seconds: float = _SLOW_CHANNEL_SLEEP) -> None:
        self._sleep = sleep_seconds
        self.calls = 0

    async def send(self, payload: NotifyPayload) -> NotifyResult:
        self.calls += 1
        await asyncio.sleep(self._sleep)
        return NotifyResult(
            channel="feishu",
            status=NotifyStatus.DELIVERED,
            attempt=1,
            delivered_at=payload.occurred_at,
            error=None,
        )


def _make_service(*, rule_hit_sink: RuleHitSink | None = None) -> AlertingService:
    if rule_hit_sink is None:
        service = AlertingService(
            audit_service=AuditService(InMemoryAuditRepository()),
            notifier=InMemoryNotifier(),
            repository=InMemoryAlertingRepository(),
        )
    else:
        service = AlertingService(
            audit_service=AuditService(InMemoryAuditRepository()),
            notifier=InMemoryNotifier(),
            repository=InMemoryAlertingRepository(),
            rule_hit_sink=rule_hit_sink,
        )
    service.create_rule(
        actor_user_id="user-admin",
        enabled=True,
        engine=DatabaseEngine.MYSQL,
        instance_ids=("inst-bp",),
        metric_name="mysql_threads_running",
        name="Threads Running Backpressure",
        operator=RuleOperator.GREATER_THAN_OR_EQUAL,
        severity=RuleSeverity.WARNING,
        threshold=4.0,
    )
    return service


def _samples(metric_value: float) -> tuple[MetricSample, ...]:
    anchor = sample_anchor()
    return (
        build_sample(
            anchor=anchor,
            instance_id="inst-bp",
            metric_kind=MetricKind.GAUGE,
            metric_name="mysql_threads_running",
            metric_value=metric_value,
            minutes_ago=1,
        ),
    )


async def _measure_avg_ms(service: AlertingService) -> float:
    samples_high = _samples(10.0)
    samples_low = _samples(0.0)
    elapsed_ms: list[float] = []
    for i in range(_SAMPLE_ITERATIONS):
        payload = samples_high if i % 2 == 0 else samples_low
        start = time.perf_counter()
        service.evaluate_samples(samples=payload)
        elapsed_ms.append((time.perf_counter() - start) * 1000.0)
    return sum(elapsed_ms) / len(elapsed_ms)


async def _scenario() -> tuple[float, float, int]:
    baseline_service = _make_service()
    baseline_ms = await _measure_avg_ms(baseline_service)

    registry = ChannelRegistry()
    slow = _SlowNotifier()
    registry.register("feishu", slow)
    bindings = InMemoryBindingRepository()
    history = InMemoryNotifyHistoryRepository()
    coordinator = DispatchCoordinator(
        registry=registry,
        bindings=bindings,
        history=history,
        max_concurrent_tasks=256,
    )

    slow_service = _make_service(rule_hit_sink=coordinator)
    rule = slow_service.list_rules()[0]
    bindings.register(rule_id=rule.rule_id, channel="feishu")

    slow_ms = await _measure_avg_ms(slow_service)

    await coordinator.wait_idle()
    return baseline_ms, slow_ms, slow.calls


def test_dispatch_coordinator_does_not_backpressure_rule_engine() -> None:
    baseline_ms, slow_ms, slow_calls = asyncio.run(_scenario())
    ceiling_ms = max(baseline_ms * 1.25, baseline_ms + 50.0)
    assert slow_ms <= ceiling_ms, (
        f"rule engine backpressure: baseline={baseline_ms:.2f}ms "
        f"slow_sink={slow_ms:.2f}ms ceiling={ceiling_ms:.2f}ms"
    )
    assert slow_calls >= 1, "slow notifier should have been scheduled"
