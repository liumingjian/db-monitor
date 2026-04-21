import json
from datetime import datetime
from typing import cast

import psycopg

from db_monitor_api.alerting.domain import (
    AlertEventType,
    AlertHistoryEvent,
    AlertRecord,
    AlertRule,
    AlertStatus,
    RuleOperator,
    RuleSeverity,
)
from db_monitor_api.control_plane.domain import DatabaseEngine

_RULE_SELECT_SQL = """
SELECT
    rule_id,
    organization_id,
    engine,
    name,
    metric_name,
    operator,
    threshold,
    severity,
    enabled,
    instance_ids_json,
    created_at
FROM alert_rules
"""
_ALERT_SELECT_SQL = """
SELECT
    alert_id,
    organization_id,
    rule_id,
    rule_name,
    engine,
    instance_id,
    metric_name,
    severity,
    status,
    current_value,
    threshold,
    opened_at,
    last_evaluated_at,
    acknowledged_at,
    acknowledged_by_user_id,
    owner_user_id,
    owner_assigned_at,
    resolved_at
FROM alert_records
"""
_HISTORY_SELECT_SQL = """
SELECT
    alert_id,
    organization_id,
    event_type,
    detail,
    occurred_at
FROM alert_history
"""


class PostgresAlertingRepository:
    def __init__(self, *, postgres_dsn: str) -> None:
        self._postgres_dsn = postgres_dsn

    def append_history(self, event: AlertHistoryEvent) -> None:
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO alert_history (
                        alert_id,
                        organization_id,
                        event_type,
                        detail,
                        occurred_at
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        event.alert_id,
                        event.organization_id,
                        event.event_type.value,
                        event.detail,
                        event.occurred_at,
                    ),
                )

    def create_rule(self, rule: AlertRule) -> None:
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO alert_rules (
                        rule_id,
                        organization_id,
                        engine,
                        name,
                        metric_name,
                        operator,
                        threshold,
                        severity,
                        enabled,
                        instance_ids_json,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    _rule_values(rule),
                )

    def find_active_alert(
        self,
        *,
        instance_id: str,
        organization_id: str | None = None,
        rule_id: str,
    ) -> AlertRecord | None:
        query = f"{_ALERT_SELECT_SQL} WHERE rule_id = %s AND instance_id = %s AND status <> %s"
        params: list[object] = [rule_id, instance_id, AlertStatus.RESOLVED.value]
        if organization_id is not None:
            query += " AND organization_id = %s"
            params.append(organization_id)
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                row = cursor.fetchone()
        return None if row is None else _row_to_alert(row)

    def get_alert(
        self,
        alert_id: str,
        *,
        organization_id: str | None = None,
    ) -> AlertRecord | None:
        query = f"{_ALERT_SELECT_SQL} WHERE alert_id = %s"
        params: list[object] = [alert_id]
        if organization_id is not None:
            query += " AND organization_id = %s"
            params.append(organization_id)
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                row = cursor.fetchone()
        return None if row is None else _row_to_alert(row)

    def list_alerts(self, *, organization_id: str | None = None) -> tuple[AlertRecord, ...]:
        query = _ALERT_SELECT_SQL
        params: tuple[object, ...] = ()
        if organization_id is not None:
            query += " WHERE organization_id = %s"
            params = (organization_id,)
        query += " ORDER BY opened_at DESC"
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
        return tuple(_row_to_alert(row) for row in rows)

    def list_history(
        self,
        *,
        alert_id: str,
        organization_id: str | None = None,
    ) -> tuple[AlertHistoryEvent, ...]:
        query = f"{_HISTORY_SELECT_SQL} WHERE alert_id = %s"
        params: list[object] = [alert_id]
        if organization_id is not None:
            query += " AND organization_id = %s"
            params.append(organization_id)
        query += " ORDER BY occurred_at ASC"
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
        return tuple(_row_to_history(row) for row in rows)

    def list_rules(self, *, organization_id: str | None = None) -> tuple[AlertRule, ...]:
        query = _RULE_SELECT_SQL
        params: tuple[object, ...] = ()
        if organization_id is not None:
            query += " WHERE organization_id = %s"
            params = (organization_id,)
        query += " ORDER BY created_at ASC"
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
        return tuple(_row_to_rule(row) for row in rows)

    def upsert_alert(self, alert: AlertRecord) -> None:
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO alert_records (
                        alert_id,
                        organization_id,
                        rule_id,
                        rule_name,
                        engine,
                        instance_id,
                        metric_name,
                        severity,
                        status,
                        current_value,
                        threshold,
                        opened_at,
                        last_evaluated_at,
                        acknowledged_at,
                        acknowledged_by_user_id,
                        owner_user_id,
                        owner_assigned_at,
                        resolved_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (alert_id) DO UPDATE SET
                        organization_id = EXCLUDED.organization_id,
                        engine = EXCLUDED.engine,
                        status = EXCLUDED.status,
                        current_value = EXCLUDED.current_value,
                        last_evaluated_at = EXCLUDED.last_evaluated_at,
                        acknowledged_at = EXCLUDED.acknowledged_at,
                        acknowledged_by_user_id = EXCLUDED.acknowledged_by_user_id,
                        owner_user_id = EXCLUDED.owner_user_id,
                        owner_assigned_at = EXCLUDED.owner_assigned_at,
                        resolved_at = EXCLUDED.resolved_at
                    """,
                    _alert_values(alert),
                )


def _rule_values(rule: AlertRule) -> tuple[object, ...]:
    return (
        rule.rule_id,
        rule.organization_id,
        rule.engine.value,
        rule.name,
        rule.metric_name,
        rule.operator.value,
        rule.threshold,
        rule.severity.value,
        rule.enabled,
        json.dumps(rule.instance_ids),
        rule.created_at,
    )


def _alert_values(alert: AlertRecord) -> tuple[object, ...]:
    return (
        alert.alert_id,
        alert.organization_id,
        alert.rule_id,
        alert.rule_name,
        alert.engine.value,
        alert.instance_id,
        alert.metric_name,
        alert.severity.value,
        alert.status.value,
        alert.current_value,
        alert.threshold,
        alert.opened_at,
        alert.last_evaluated_at,
        alert.acknowledged_at,
        alert.acknowledged_by_user_id,
        alert.owner_user_id,
        alert.owner_assigned_at,
        alert.resolved_at,
    )


def _row_to_rule(row: tuple[object, ...]) -> AlertRule:
    return AlertRule(
        created_at=cast(datetime, row[10]),
        enabled=bool(row[8]),
        engine=DatabaseEngine(str(row[2])),
        instance_ids=tuple(json.loads(str(row[9]))),
        metric_name=str(row[4]),
        name=str(row[3]),
        organization_id=str(row[1]),
        operator=RuleOperator(str(row[5])),
        rule_id=str(row[0]),
        severity=RuleSeverity(str(row[7])),
        threshold=float(cast(float | str, row[6])),
    )


def _row_to_alert(row: tuple[object, ...]) -> AlertRecord:
    return AlertRecord(
        alert_id=str(row[0]),
        acknowledged_at=None if row[13] is None else cast(datetime, row[13]),
        acknowledged_by_user_id=None if row[14] is None else str(row[14]),
        current_value=float(cast(float | str, row[9])),
        engine=DatabaseEngine(str(row[4])),
        instance_id=str(row[5]),
        last_evaluated_at=cast(datetime, row[12]),
        metric_name=str(row[6]),
        opened_at=cast(datetime, row[11]),
        owner_assigned_at=None if row[16] is None else cast(datetime, row[16]),
        owner_user_id=None if row[15] is None else str(row[15]),
        organization_id=str(row[1]),
        resolved_at=None if row[17] is None else cast(datetime, row[17]),
        rule_id=str(row[2]),
        rule_name=str(row[3]),
        severity=RuleSeverity(str(row[7])),
        status=AlertStatus(str(row[8])),
        threshold=float(cast(float | str, row[10])),
    )


def _row_to_history(row: tuple[object, ...]) -> AlertHistoryEvent:
    return AlertHistoryEvent(
        alert_id=str(row[0]),
        detail=str(row[3]),
        event_type=AlertEventType(str(row[2])),
        organization_id=str(row[1]),
        occurred_at=cast(datetime, row[4]),
    )
