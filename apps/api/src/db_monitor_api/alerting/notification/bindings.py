from collections.abc import Iterable, Mapping, Sequence
from threading import RLock

from db_monitor_api.alerting.notification.service import (
    BindingRepository,
    ChannelBinding,
)


class InMemoryBindingRepository(BindingRepository):
    def __init__(self, bindings: Iterable[ChannelBinding] = ()) -> None:
        self._by_rule: dict[str, list[ChannelBinding]] = {}
        self._lock = RLock()
        for binding in bindings:
            self._append(binding)

    def _append(self, binding: ChannelBinding) -> None:
        self._by_rule.setdefault(binding.rule_id, []).append(binding)

    def register(
        self,
        *,
        rule_id: str,
        channel: str,
        config: Mapping[str, object] | None = None,
    ) -> ChannelBinding:
        binding = ChannelBinding(
            rule_id=rule_id,
            channel=channel,
            config=dict(config or {}),
        )
        with self._lock:
            self._append(binding)
        return binding

    def clear(self, *, rule_id: str) -> None:
        with self._lock:
            self._by_rule.pop(rule_id, None)

    def list_for_rule(
        self, *, organization_id: str, rule_id: str
    ) -> Sequence[ChannelBinding]:
        del organization_id  # single-tenant in-memory scope
        with self._lock:
            return tuple(self._by_rule.get(rule_id, ()))


__all__ = ["InMemoryBindingRepository"]
