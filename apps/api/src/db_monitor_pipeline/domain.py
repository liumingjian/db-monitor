from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
import json

from db_monitor_api.control_plane.domain import DatabaseEngine, InstanceConnectionConfig

INITIAL_COLLECTION_ATTEMPT = 1


class MetricKind(StrEnum):
    COUNTER = "counter"
    GAUGE = "gauge"


@dataclass(frozen=True)
class CollectionJob:
    attempt: int
    available_at: datetime
    connection: InstanceConnectionConfig
    engine: DatabaseEngine
    environment: str
    instance_id: str
    labels: tuple[str, ...]
    name: str
    queued_at: datetime

    @property
    def dedupe_key(self) -> str:
        return self.instance_id

    def schedule_retry(self, *, available_at: datetime) -> "CollectionJob":
        return replace(
            self,
            attempt=self.attempt + 1,
            available_at=available_at,
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "attempt": self.attempt,
                "available_at": self.available_at.isoformat(),
                "connection": {
                    "database": self.connection.database,
                    "host": self.connection.host,
                    "password": self.connection.password,
                    "port": self.connection.port,
                    "username": self.connection.username,
                },
                "engine": self.engine.value,
                "environment": self.environment,
                "instance_id": self.instance_id,
                "labels": list(self.labels),
                "name": self.name,
                "queued_at": self.queued_at.isoformat(),
            }
        )

    @classmethod
    def from_json(cls, payload: str) -> "CollectionJob":
        raw = json.loads(payload)
        return cls(
            attempt=int(raw["attempt"]),
            available_at=datetime.fromisoformat(str(raw["available_at"])),
            connection=InstanceConnectionConfig(**raw["connection"]),
            engine=DatabaseEngine(str(raw.get("engine", DatabaseEngine.MYSQL.value))),
            environment=str(raw["environment"]),
            instance_id=str(raw["instance_id"]),
            labels=tuple(str(label) for label in raw["labels"]),
            name=str(raw["name"]),
            queued_at=datetime.fromisoformat(str(raw["queued_at"])),
        )


@dataclass(frozen=True)
class MetricSample:
    collected_at: datetime
    environment: str
    instance_id: str
    labels: tuple[str, ...]
    metric_kind: MetricKind
    metric_name: str
    metric_value: float
    engine: DatabaseEngine = DatabaseEngine.MYSQL
