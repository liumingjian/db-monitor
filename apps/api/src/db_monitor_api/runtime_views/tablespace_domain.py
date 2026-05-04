"""Oracle tablespace view-layer domain (Epic 15 Slice 1 child #4).

Pure data carriers used by the service + repository layers. Separated
from `runtime_views/domain.py` to keep per-feature churn isolated and
respect the 300-line file limit.
"""

from dataclasses import dataclass
from datetime import datetime

MAX_TABLESPACE_HISTORY_DAYS = 30
DEFAULT_TABLESPACE_HISTORY_DAYS = 7
HISTORY_HOURLY_DOWNSAMPLE_THRESHOLD_DAYS = 7


@dataclass(frozen=True)
class TablespaceEntryRow:
    tablespace_name: str
    status: str
    used_bytes: int
    total_bytes: int
    used_rate_percent: float
    autoextensible: bool


@dataclass(frozen=True)
class TablespaceSnapshotView:
    collected_at: datetime
    entries: tuple[TablespaceEntryRow, ...]


@dataclass(frozen=True)
class TablespaceHistoryPoint:
    collected_at: datetime
    used_bytes: int
    total_bytes: int
    used_rate_percent: float


@dataclass(frozen=True)
class TablespaceHistoryView:
    entries: tuple[TablespaceHistoryPoint, ...]


@dataclass(frozen=True)
class TablespaceSnapshotQuery:
    collected_after: datetime | None = None
    collected_before: datetime | None = None


@dataclass(frozen=True)
class TablespaceHistoryQuery:
    tablespace_name: str
    from_timestamp: datetime
    to_timestamp: datetime
