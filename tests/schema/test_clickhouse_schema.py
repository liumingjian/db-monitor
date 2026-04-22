from typing import Literal
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request

import pytest

from db_monitor_api.settings import ClickHouseSettings
from db_monitor_pipeline.sink import CLICKHOUSE_MYSQL_PROCESSLIST_TABLE
from db_monitor_schema.clickhouse import (
    CLICKHOUSE_REQUIRED_TABLES,
    bootstrap_clickhouse_schema,
)
from db_monitor_schema.contract import CLICKHOUSE_SCHEMA_VERSION


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


def _settings() -> ClickHouseSettings:
    return ClickHouseSettings(
        database="db_monitor",
        endpoint="http://127.0.0.1:8123",
        password="db_monitor",
        username="db_monitor",
    )


def test_required_tables_include_mysql_processlist() -> None:
    assert CLICKHOUSE_MYSQL_PROCESSLIST_TABLE == "mysql_processlist"
    assert CLICKHOUSE_MYSQL_PROCESSLIST_TABLE in CLICKHOUSE_REQUIRED_TABLES


def test_bootstrap_creates_mysql_processlist_with_adr_0005_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    queries: list[str] = []

    def fake_urlopen(request: Request) -> FakeResponse:
        query = parse_qs(urlsplit(request.get_full_url()).query)["query"][0]
        queries.append(query)
        return FakeResponse("")

    monkeypatch.setattr("db_monitor_schema.clickhouse.urlopen", fake_urlopen)

    version = bootstrap_clickhouse_schema(settings=_settings())

    executed = "\n".join(queries)
    assert version.version == CLICKHOUSE_SCHEMA_VERSION
    assert "CREATE TABLE IF NOT EXISTS mysql_processlist" in executed
    for column in (
        "organization_id String",
        "instance_id String",
        "collected_at DateTime64(3, 'UTC')",
        "process_id UInt64",
        "user String",
        "host String",
        "db String",
        "command LowCardinality(String)",
        "time_seconds UInt32",
        "state LowCardinality(String)",
        "info String",
        "trx_started_at Nullable(DateTime64(3, 'UTC'))",
    ):
        assert column in executed, f"missing column definition: {column}"
    assert "ENGINE = MergeTree()" in executed
    assert "PARTITION BY toYYYYMMDD(collected_at)" in executed
    assert "ORDER BY (instance_id, collected_at, process_id)" in executed
    assert "TTL toDateTime(collected_at) + INTERVAL 7 DAY" in executed
