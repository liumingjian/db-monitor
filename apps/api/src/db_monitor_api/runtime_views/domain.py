from dataclasses import dataclass
from datetime import datetime


MAX_PROCESSLIST_LIMIT = 500
DEFAULT_PROCESSLIST_LIMIT = 200


@dataclass(frozen=True)
class ProcesslistEntryRow:
    process_id: int
    user: str
    host: str
    db: str
    command: str
    time_seconds: int
    state: str
    info: str
    trx_started_at: datetime | None


@dataclass(frozen=True)
class ProcesslistSnapshotView:
    collected_at: datetime
    entries: tuple[ProcesslistEntryRow, ...]


@dataclass(frozen=True)
class ProcesslistQuery:
    collected_after: datetime | None = None
    collected_before: datetime | None = None
    command: str | None = None
    host: str | None = None
    limit: int = DEFAULT_PROCESSLIST_LIMIT
    min_time_seconds: int | None = None
    user: str | None = None
