from collections.abc import Iterable
from datetime import UTC, datetime
import json
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from db_monitor_api.control_plane.domain import DatabaseEngine
from db_monitor_pipeline.domain import MetricKind, MetricSample
from db_monitor_pipeline.sink import CLICKHOUSE_METRICS_TABLE


class AnalyticsRepository(Protocol):
    def list_metric_samples(
        self,
        *,
        collected_after: datetime,
        instance_ids: tuple[str, ...],
        metric_names: tuple[str, ...],
    ) -> tuple[MetricSample, ...]:
        ...


class InMemoryAnalyticsRepository:
    def __init__(self, *, samples: Iterable[MetricSample] = ()) -> None:
        self._samples = list(samples)

    def add_samples(self, samples: Iterable[MetricSample]) -> None:
        self._samples.extend(samples)

    def list_metric_samples(
        self,
        *,
        collected_after: datetime,
        instance_ids: tuple[str, ...],
        metric_names: tuple[str, ...],
    ) -> tuple[MetricSample, ...]:
        instance_id_set = set(instance_ids)
        metric_name_set = set(metric_names)
        matched = [
            sample
            for sample in self._samples
            if sample.collected_at >= collected_after
            and sample.instance_id in instance_id_set
            and sample.metric_name in metric_name_set
        ]
        return tuple(sorted(matched, key=lambda sample: (sample.instance_id, sample.metric_name, sample.collected_at)))


class ClickHouseAnalyticsRepository:
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

    def list_metric_samples(
        self,
        *,
        collected_after: datetime,
        instance_ids: tuple[str, ...],
        metric_names: tuple[str, ...],
    ) -> tuple[MetricSample, ...]:
        if not instance_ids or not metric_names:
            return ()
        query = _build_select_query(
            collected_after=collected_after,
            instance_ids=instance_ids,
            metric_names=metric_names,
        )
        rows = _run_query(
            database=self._database,
            endpoint=self._endpoint,
            password=self._password,
            query=query,
            username=self._username,
        )
        return tuple(_row_to_metric_sample(row) for row in rows)


def _build_select_query(
    *,
    collected_after: datetime,
    instance_ids: tuple[str, ...],
    metric_names: tuple[str, ...],
) -> str:
    return (
        "SELECT collected_at, engine, environment, instance_id, labels_json, metric_kind, metric_name, metric_value "
        f"FROM {CLICKHOUSE_METRICS_TABLE} "
        f"WHERE collected_at >= '{_format_clickhouse_datetime(collected_after)}' "
        f"AND instance_id IN ({_join_string_literals(instance_ids)}) "
        f"AND metric_name IN ({_join_string_literals(metric_names)}) "
        "ORDER BY instance_id, metric_name, collected_at FORMAT JSONEachRow"
    )


def _join_string_literals(values: tuple[str, ...]) -> str:
    return ", ".join(_quote_string(value) for value in values)


def _quote_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _format_clickhouse_datetime(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _run_query(
    *,
    database: str,
    endpoint: str,
    password: str,
    query: str,
    username: str,
) -> list[dict[str, object]]:
    request = Request(
        url=f"{endpoint}/?{urlencode({'database': database, 'query': query})}",
        data=b"",
        headers={"X-ClickHouse-User": username, "X-ClickHouse-Key": password},
        method="POST",
    )
    with urlopen(request) as response:
        body = response.read().decode("utf-8")
    return [json.loads(line) for line in body.splitlines() if line]


def _row_to_metric_sample(row: dict[str, object]) -> MetricSample:
    return MetricSample(
        collected_at=_parse_clickhouse_datetime(str(row["collected_at"])),
        engine=DatabaseEngine(str(row.get("engine", DatabaseEngine.MYSQL.value))),
        environment=str(row["environment"]),
        instance_id=str(row["instance_id"]),
        labels=tuple(str(label) for label in json.loads(str(row["labels_json"]))),
        metric_kind=MetricKind(str(row["metric_kind"])),
        metric_name=str(row["metric_name"]),
        metric_value=float(str(row["metric_value"])),
    )


def _parse_clickhouse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)
