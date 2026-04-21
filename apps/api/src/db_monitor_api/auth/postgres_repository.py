from datetime import datetime
from typing import cast

import psycopg

from db_monitor_api.auth.domain import AuditEntry

_AUDIT_SELECT_SQL = """
SELECT
    organization_id,
    action,
    actor_user_id,
    occurred_at,
    outcome,
    resource
FROM audit_entries
"""


class PostgresAuditRepository:
    def __init__(self, *, postgres_dsn: str) -> None:
        self._postgres_dsn = postgres_dsn

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return self.list_entries()

    def append(self, entry: AuditEntry) -> None:
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO audit_entries (
                        organization_id,
                        action,
                        actor_user_id,
                        occurred_at,
                        outcome,
                        resource
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        entry.organization_id,
                        entry.action,
                        entry.actor_user_id,
                        entry.occurred_at,
                        entry.outcome,
                        entry.resource,
                    ),
                )

    def list_entries(
        self,
        *,
        descending: bool = False,
        limit: int | None = None,
        organization_id: str | None = None,
    ) -> tuple[AuditEntry, ...]:
        query = _AUDIT_SELECT_SQL
        params: list[object] = []
        if organization_id is not None:
            query += " WHERE organization_id = %s"
            params.append(organization_id)
        direction = "DESC" if descending else "ASC"
        query += f" ORDER BY occurred_at {direction}, audit_id {direction}"
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
        return tuple(_row_to_audit_entry(row) for row in rows)


def _row_to_audit_entry(row: tuple[object, ...]) -> AuditEntry:
    return AuditEntry(
        action=str(row[1]),
        actor_user_id=str(row[2]),
        occurred_at=cast(datetime, row[3]),
        organization_id=str(row[0]),
        outcome=str(row[4]),
        resource=str(row[5]),
    )
