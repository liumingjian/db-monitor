"""Domain types for the slow-query runtime view (ADR-0007)."""

from dataclasses import dataclass
from datetime import datetime


DEFAULT_SLOW_QUERY_LIMIT = 50
MAX_SLOW_QUERY_LIMIT = 200
DEFAULT_SLOW_QUERY_WINDOW_MINUTES = 15


@dataclass(frozen=True)
class SlowQueryEntryRow:
    event_id: int
    started_at: datetime
    user: str
    schema_name: str
    sql_text: str
    digest: str
    timer_wait_ms: float
    rows_examined: int
    rows_sent: int
    rows_affected: int
    errors: int


@dataclass(frozen=True)
class SlowQueryWindow:
    from_at: datetime
    to_at: datetime


@dataclass(frozen=True)
class SlowQuerySnapshotView:
    window: SlowQueryWindow
    entries: tuple[SlowQueryEntryRow, ...]


@dataclass(frozen=True)
class SlowQueryQuery:
    digest_prefix: str | None = None
    limit: int = DEFAULT_SLOW_QUERY_LIMIT
    min_duration_ms: float | None = None
    schema_name: str | None = None
    started_after: datetime | None = None
    started_before: datetime | None = None
    user: str | None = None
