from collections.abc import Mapping
import subprocess

from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import DatabaseEngine, InstanceConnectionConfig
from db_monitor_pipeline.collector import OracleMetricsCollector, PythonOracleMetricsCollector
from db_monitor_pipeline.domain import CollectionJob, INITIAL_COLLECTION_ATTEMPT
from db_monitor_pipeline.queue import InMemoryCollectionTaskQueue
from db_monitor_pipeline.sink import InMemoryMetricSink
from db_monitor_pipeline.worker import OracleMetricsWorker, RetryPolicy


class StaticCollector(OracleMetricsCollector):
    def collect(self, connection: InstanceConnectionConfig) -> Mapping[str, str]:
        del connection
        return {
            "SessionsActive": "3",
            "SessionsTotal": "12",
            "SessionWaits": "1",
            "PhysicalReads": "55",
            "UptimeSeconds": "3600",
            "UserCalls": "120",
        }


class FailingCollector(OracleMetricsCollector):
    def collect(self, connection: InstanceConnectionConfig) -> Mapping[str, str]:
        del connection
        raise RuntimeError("ORA-12541: TNS:no listener")


def test_worker_writes_oracle_metrics_to_sink() -> None:
    queue = InMemoryCollectionTaskQueue()
    queue.enqueue(_build_job())
    sink = InMemoryMetricSink()

    result = OracleMetricsWorker(
        collector=StaticCollector(),
        queue=queue,
        sink=sink,
    ).process_next()

    assert result.status == "processed"
    assert result.processed_metrics == 7
    assert len(sink.samples) == 7
    assert sink.samples[0].metric_name == "oracle_server_available"


def test_worker_exposes_oracle_collection_failures_without_fake_success() -> None:
    queue = InMemoryCollectionTaskQueue()
    queue.enqueue(_build_job())
    sink = InMemoryMetricSink()

    result = OracleMetricsWorker(
        collector=FailingCollector(),
        queue=queue,
        retry_policy=RetryPolicy(backoff_seconds=1, max_attempts=1),
        sink=sink,
    ).process_next()

    assert result.status == "failed"
    assert result.error == "ORA-12541: TNS:no listener"
    assert sink.samples == []


def test_oracle_collector_uses_sqlplus_fallback_for_localhost(monkeypatch) -> None:
    config = InstanceConnectionConfig(
        database="XE",
        host="127.0.0.1",
        password="oracle",
        port=15211,
        username="system",
    )
    captured: dict[str, object] = {}

    monkeypatch.setenv("DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER", "oracle-xe-local")
    monkeypatch.setattr(
        "db_monitor_pipeline.collector._load_oracle_driver",
        lambda: None,
    )

    def fake_run(
        cmd: list[str],
        *,
        capture_output: bool,
        check: bool,
        env: dict[str, str],
        text: bool,
    ) -> subprocess.CompletedProcess[str]:
        del capture_output, check, text
        captured["cmd"] = cmd
        captured["env"] = env
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=(
                "SessionsTotal=12\n"
                "SessionsActive=3\n"
                "SessionWaits=1\n"
                "UserCalls=120\n"
                "PhysicalReads=55\n"
                "UptimeSeconds=3600\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(
        "db_monitor_pipeline.collector.subprocess.run",
        fake_run,
    )

    metrics = PythonOracleMetricsCollector().collect(config)

    assert metrics["SessionsTotal"] == "12"
    assert metrics["UserCalls"] == "120"
    env = captured["env"]
    assert isinstance(env, dict)
    assert env["ORACLE_HOST"] == "host.docker.internal"


def _build_job() -> CollectionJob:
    queued_at = utc_now()
    return CollectionJob(
        attempt=INITIAL_COLLECTION_ATTEMPT,
        available_at=queued_at,
        connection=InstanceConnectionConfig(
            database="XE",
            host="127.0.0.1",
            password="oracle",
            port=15211,
            username="system",
        ),
        engine=DatabaseEngine.ORACLE,
        environment="prod",
        instance_id="inst-oracle-123",
        labels=("oracle",),
        name="prod-oracle-primary",
        queued_at=queued_at,
    )
