import json
from datetime import UTC, datetime
from typing import Protocol
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from db_monitor_pipeline.domain import MetricSample
from db_monitor_pipeline.processlist import (
    ProcesslistSnapshot,
    snapshot_to_clickhouse_rows,
)
from db_monitor_pipeline.slow_query import (
    SlowQuerySnapshot,
    slow_query_snapshot_to_clickhouse_rows,
)
from db_monitor_pipeline.tablespace import (
    TablespaceSnapshot,
    snapshot_to_clickhouse_rows as tablespace_snapshot_to_rows,
)

CLICKHOUSE_METRICS_TABLE = "metric_samples"
CLICKHOUSE_MYSQL_PROCESSLIST_TABLE = "mysql_processlist"
CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE = "mysql_slow_query_events"
CLICKHOUSE_ORACLE_TABLESPACES_TABLE = "oracle_tablespaces"


class MetricSink(Protocol):
    def write(self, samples: tuple[MetricSample, ...]) -> None:
        ...


class InMemoryMetricSink:
    def __init__(self) -> None:
        self.samples: list[MetricSample] = []
        self.processlist_snapshots: list[ProcesslistSnapshot] = []
        self.slow_query_snapshots: list[SlowQuerySnapshot] = []
        self.tablespace_snapshots: list[TablespaceSnapshot] = []

    def write(self, samples: tuple[MetricSample, ...]) -> None:
        self.samples.extend(samples)

    def write_processlist(self, snapshot: ProcesslistSnapshot) -> None:
        self.processlist_snapshots.append(snapshot)

    def write_slow_queries(self, snapshot: SlowQuerySnapshot) -> None:
        self.slow_query_snapshots.append(snapshot)

    def write_tablespaces(self, snapshot: TablespaceSnapshot) -> None:
        self.tablespace_snapshots.append(snapshot)


class ClickHouseMetricSink:
    def __init__(
        self,
        *,
        database: str,
        endpoint: str,
        password: str,
        username: str,
    ) -> None:
        self._database = database
        self._endpoint = endpoint.rstrip("/")
        self._password = password
        self._username = username

    def write(self, samples: tuple[MetricSample, ...]) -> None:
        if not samples:
            return
        payload = "\n".join(_sample_to_json(sample) for sample in samples).encode("utf-8")
        self._post(query=f"INSERT INTO {CLICKHOUSE_METRICS_TABLE} FORMAT JSONEachRow", payload=payload)

    def write_processlist(self, snapshot: ProcesslistSnapshot) -> None:
        rows = snapshot_to_clickhouse_rows(snapshot)
        if not rows:
            return
        payload = "\n".join(json.dumps(row) for row in rows).encode("utf-8")
        self._post(
            query=f"INSERT INTO {CLICKHOUSE_MYSQL_PROCESSLIST_TABLE} FORMAT JSONEachRow",
            payload=payload,
        )

    def write_slow_queries(self, snapshot: SlowQuerySnapshot) -> None:
        rows = slow_query_snapshot_to_clickhouse_rows(snapshot)
        if not rows:
            return
        payload = "\n".join(json.dumps(row) for row in rows).encode("utf-8")
        self._post(
            query=f"INSERT INTO {CLICKHOUSE_MYSQL_SLOW_QUERY_EVENTS_TABLE} FORMAT JSONEachRow",
            payload=payload,
        )

    def write_tablespaces(self, snapshot: TablespaceSnapshot) -> None:
        rows = tablespace_snapshot_to_rows(snapshot)
        if not rows:
            return
        payload = "\n".join(json.dumps(row) for row in rows).encode("utf-8")
        self._post(
            query=f"INSERT INTO {CLICKHOUSE_ORACLE_TABLESPACES_TABLE} FORMAT JSONEachRow",
            payload=payload,
        )

    def _post(self, *, payload: bytes, query: str) -> None:
        request = Request(
            url=f"{self._endpoint}/?{urlencode({'database': self._database, 'query': query})}",
            data=payload,
            headers={"X-ClickHouse-User": self._username, "X-ClickHouse-Key": self._password},
            method="POST",
        )
        try:
            with urlopen(request) as response:
                response.read()
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"ClickHouse request failed with status {error.code}: {detail}"
            ) from error


def _sample_to_json(sample: MetricSample) -> str:
    return json.dumps(
        {
            "collected_at": _format_clickhouse_datetime(sample.collected_at),
            "engine": sample.engine.value,
            "environment": sample.environment,
            "instance_id": sample.instance_id,
            "labels_json": json.dumps(sample.labels),
            "metric_kind": sample.metric_kind.value,
            "metric_name": sample.metric_name,
            "metric_value": sample.metric_value,
        }
    )


def _format_clickhouse_datetime(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
