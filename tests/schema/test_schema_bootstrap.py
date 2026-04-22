from urllib.parse import parse_qs, urlsplit
from urllib.request import Request
from typing import Literal

import pytest

from db_monitor_api.settings import ClickHouseSettings
from db_monitor_schema.clickhouse import bootstrap_clickhouse_schema, verify_clickhouse_schema
from db_monitor_schema.contract import CLICKHOUSE_SCHEMA_VERSION, POSTGRES_SCHEMA_VERSION
from db_monitor_schema.postgres import bootstrap_postgres_schema, verify_postgres_schema


class FakeCursor:
    def __init__(
        self,
        *,
        fetchall_results: list[list[tuple[object, ...]]] | None = None,
        fetchone_results: list[tuple[object, ...] | None] | None = None,
    ) -> None:
        self.executed: list[tuple[str, tuple[object, ...] | None]] = []
        self._fetchall_results = [] if fetchall_results is None else list(fetchall_results)
        self._fetchone_results = [] if fetchone_results is None else list(fetchone_results)

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> Literal[False]:
        del exc_type, exc, traceback
        return False

    def execute(self, query: str, params: tuple[object, ...] | None = None) -> None:
        self.executed.append((query.strip(), params))

    def fetchall(self) -> list[tuple[object, ...]]:
        return [] if not self._fetchall_results else self._fetchall_results.pop(0)

    def fetchone(self) -> tuple[object, ...] | None:
        return None if not self._fetchone_results else self._fetchone_results.pop(0)


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> Literal[False]:
        del exc_type, exc, traceback
        return False

    def cursor(self) -> FakeCursor:
        return self._cursor


class FakeResponse:
    def __init__(self, body: str) -> None:
        self._body = body.encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> Literal[False]:
        del exc_type, exc, traceback
        return False

    def read(self) -> bytes:
        return self._body


def test_postgres_bootstrap_creates_tables_and_version_row(monkeypatch: pytest.MonkeyPatch) -> None:
    cursor = FakeCursor()
    monkeypatch.setattr(
        "db_monitor_schema.postgres.psycopg.connect",
        lambda dsn: FakeConnection(cursor),
    )

    version = bootstrap_postgres_schema(postgres_dsn="postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor")

    executed_sql = "\n".join(query for query, _ in cursor.executed)
    assert version.version == POSTGRES_SCHEMA_VERSION
    assert "CREATE TABLE IF NOT EXISTS schema_version" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS organizations" in executed_sql
    assert "slug TEXT NOT NULL UNIQUE" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS organization_memberships" in executed_sql
    assert "roles_json TEXT NOT NULL" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS control_mysql_instances" in executed_sql
    assert "organization_id TEXT NOT NULL" in executed_sql
    assert "engine TEXT NOT NULL" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS control_settings" in executed_sql
    assert "PRIMARY KEY (organization_id, key)" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS alert_rules" in executed_sql
    assert executed_sql.count("organization_id TEXT NOT NULL") >= 4
    assert "CREATE TABLE IF NOT EXISTS alert_records" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS alert_history" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS audit_entries" in executed_sql
    assert "audit_id BIGSERIAL PRIMARY KEY" in executed_sql
    assert "acknowledged_at TIMESTAMPTZ NULL" in executed_sql
    assert "owner_user_id TEXT NULL" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS rule_instance_overrides" in executed_sql
    assert "REFERENCES alert_rules (rule_id) ON DELETE CASCADE" in executed_sql
    assert "REFERENCES control_mysql_instances (instance_id) ON DELETE CASCADE" in executed_sql
    assert "PRIMARY KEY (rule_id, instance_id)" in executed_sql
    assert "INSERT INTO schema_version" in executed_sql


def test_postgres_contract_requires_bootstrapped_version(monkeypatch: pytest.MonkeyPatch) -> None:
    cursor = FakeCursor(
        fetchall_results=[
            [
                ("alert_history",),
                ("alert_records",),
                ("alert_rules",),
                ("audit_entries",),
                ("control_mysql_instances",),
                ("control_settings",),
                ("instance_parameters",),
                ("organization_memberships",),
                ("organizations",),
                ("rule_instance_overrides",),
                ("schema_version",),
            ]
        ],
        fetchone_results=[None],
    )
    monkeypatch.setattr(
        "db_monitor_schema.postgres.psycopg.connect",
        lambda dsn: FakeConnection(cursor),
    )

    with pytest.raises(RuntimeError, match="bootstrap-postgres"):
        verify_postgres_schema(postgres_dsn="postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor")


def test_clickhouse_bootstrap_creates_database_tables_and_version_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    queries: list[str] = []

    def fake_urlopen(request: Request) -> FakeResponse:
        query = parse_qs(urlsplit(request.get_full_url()).query)["query"][0]
        queries.append(query)
        return FakeResponse("")

    monkeypatch.setattr("db_monitor_schema.clickhouse.urlopen", fake_urlopen)

    version = bootstrap_clickhouse_schema(
        settings=ClickHouseSettings(
            database="db_monitor",
            endpoint="http://127.0.0.1:8123",
            password="db_monitor",
            username="db_monitor",
        )
    )

    executed_sql = "\n".join(queries)
    assert version.version == CLICKHOUSE_SCHEMA_VERSION
    assert "CREATE DATABASE IF NOT EXISTS db_monitor" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS schema_version" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS metric_samples" in executed_sql
    assert "engine String" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS mysql_processlist" in executed_sql
    assert "PARTITION BY toYYYYMMDD(collected_at)" in executed_sql
    assert "ORDER BY (instance_id, collected_at, process_id)" in executed_sql
    assert "TTL toDateTime(collected_at) + INTERVAL 7 DAY" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS mysql_slow_query_events" in executed_sql
    assert "PARTITION BY toYYYYMMDD(started_at)" in executed_sql
    assert "ORDER BY (instance_id, started_at, event_id)" in executed_sql
    assert "digest_text String" in executed_sql
    assert "timer_wait_ms Float64" in executed_sql
    assert "CREATE TABLE IF NOT EXISTS oracle_tablespaces" in executed_sql
    assert "ORDER BY (instance_id, collected_at, tablespace_name)" in executed_sql
    assert "TTL toDateTime(collected_at) + INTERVAL 30 DAY" in executed_sql
    assert "autoextensible UInt8" in executed_sql
    assert "used_rate_percent Float64" in executed_sql
    assert "INSERT INTO schema_version FORMAT JSONEachRow" in executed_sql


def test_clickhouse_contract_requires_bootstrapped_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter(
        [
            '{"name":"db_monitor"}\n',
            (
                '{"name":"metric_samples"}\n'
                '{"name":"mysql_processlist"}\n'
                '{"name":"mysql_slow_query_events"}\n'
                '{"name":"oracle_tablespaces"}\n'
                '{"name":"schema_version"}\n'
            ),
            "",
        ]
    )

    def fake_urlopen(request: Request) -> FakeResponse:
        del request
        return FakeResponse(next(responses))

    monkeypatch.setattr("db_monitor_schema.clickhouse.urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="bootstrap-clickhouse"):
        verify_clickhouse_schema(
            settings=ClickHouseSettings(
                database="db_monitor",
                endpoint="http://127.0.0.1:8123",
                password="db_monitor",
                username="db_monitor",
            )
        )
