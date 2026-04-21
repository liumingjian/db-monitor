from dataclasses import replace
from typing import Protocol

from db_monitor_api.alerting.domain import AlertHistoryEvent, AlertRecord, AlertRule, AlertStatus


class AlertingRepository(Protocol):
    def append_history(self, event: AlertHistoryEvent) -> None:
        ...

    def create_rule(self, rule: AlertRule) -> None:
        ...

    def find_active_alert(
        self,
        *,
        instance_id: str,
        organization_id: str | None = None,
        rule_id: str,
    ) -> AlertRecord | None:
        ...

    def get_alert(
        self,
        alert_id: str,
        *,
        organization_id: str | None = None,
    ) -> AlertRecord | None:
        ...

    def list_alerts(self, *, organization_id: str | None = None) -> tuple[AlertRecord, ...]:
        ...

    def list_history(
        self,
        *,
        alert_id: str,
        organization_id: str | None = None,
    ) -> tuple[AlertHistoryEvent, ...]:
        ...

    def list_rules(self, *, organization_id: str | None = None) -> tuple[AlertRule, ...]:
        ...

    def upsert_alert(self, alert: AlertRecord) -> None:
        ...


class InMemoryAlertingRepository:
    def __init__(self) -> None:
        self._alerts: dict[str, AlertRecord] = {}
        self._history: dict[str, list[AlertHistoryEvent]] = {}
        self._rules: dict[str, AlertRule] = {}

    def append_history(self, event: AlertHistoryEvent) -> None:
        self._history.setdefault(event.alert_id, []).append(event)

    def create_rule(self, rule: AlertRule) -> None:
        self._rules[rule.rule_id] = rule

    def find_active_alert(
        self,
        *,
        instance_id: str,
        organization_id: str | None = None,
        rule_id: str,
    ) -> AlertRecord | None:
        for alert in self._alerts.values():
            if (
                alert.instance_id == instance_id
                and (organization_id is None or alert.organization_id == organization_id)
                and alert.rule_id == rule_id
                and alert.status is not AlertStatus.RESOLVED
            ):
                return replace(alert)
        return None

    def get_alert(
        self,
        alert_id: str,
        *,
        organization_id: str | None = None,
    ) -> AlertRecord | None:
        alert = self._alerts.get(alert_id)
        if organization_id is not None and alert is not None:
            if alert.organization_id != organization_id:
                return None
        return None if alert is None else replace(alert)

    def list_alerts(self, *, organization_id: str | None = None) -> tuple[AlertRecord, ...]:
        sorted_alerts = sorted(
            (
                alert
                for alert in self._alerts.values()
                if organization_id is None or alert.organization_id == organization_id
            ),
            key=lambda alert: alert.opened_at,
            reverse=True,
        )
        return tuple(replace(alert) for alert in sorted_alerts)

    def list_history(
        self,
        *,
        alert_id: str,
        organization_id: str | None = None,
    ) -> tuple[AlertHistoryEvent, ...]:
        return tuple(
            replace(event)
            for event in self._history.get(alert_id, [])
            if organization_id is None or event.organization_id == organization_id
        )

    def list_rules(self, *, organization_id: str | None = None) -> tuple[AlertRule, ...]:
        sorted_rules = sorted(
            (
                rule
                for rule in self._rules.values()
                if organization_id is None or rule.organization_id == organization_id
            ),
            key=lambda rule: rule.created_at,
        )
        return tuple(replace(rule) for rule in sorted_rules)

    def upsert_alert(self, alert: AlertRecord) -> None:
        self._alerts[alert.alert_id] = alert
