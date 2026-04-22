"""Oracle tablespace read-path Protocol + InMemory fixture.

ClickHouse-backed impl lives in `tablespace_clickhouse.py`; this module
intentionally carries no network IO so the in-memory fixture can be
reused by API tests without dragging the `urllib` dependency into unit
tests.
"""

from collections.abc import Iterable
from datetime import datetime
from typing import Protocol

from db_monitor_api.runtime_views.tablespace_domain import (
    TablespaceEntryRow,
    TablespaceHistoryPoint,
    TablespaceHistoryQuery,
    TablespaceHistoryView,
    TablespaceSnapshotQuery,
    TablespaceSnapshotView,
)


class TablespaceRepository(Protocol):
    def fetch_latest_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceSnapshotQuery,
    ) -> TablespaceSnapshotView | None:
        ...

    def fetch_history(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceHistoryQuery,
    ) -> TablespaceHistoryView:
        ...


class InMemoryTablespaceRepository:
    def __init__(
        self,
        *,
        snapshots: Iterable[tuple[str, str, TablespaceSnapshotView]] = (),
    ) -> None:
        self._snapshots: list[tuple[str, str, TablespaceSnapshotView]] = list(snapshots)

    def add_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        snapshot: TablespaceSnapshotView,
    ) -> None:
        self._snapshots.append((organization_id, instance_id, snapshot))

    def fetch_latest_snapshot(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceSnapshotQuery,
    ) -> TablespaceSnapshotView | None:
        matched = tuple(
            snapshot
            for snapshot_org, snapshot_instance, snapshot in self._snapshots
            if snapshot_org == organization_id
            and snapshot_instance == instance_id
            and _within_window(snapshot.collected_at, query)
        )
        if not matched:
            return None
        return max(matched, key=lambda item: item.collected_at)

    def fetch_history(
        self,
        *,
        instance_id: str,
        organization_id: str,
        query: TablespaceHistoryQuery,
    ) -> TablespaceHistoryView:
        points: list[TablespaceHistoryPoint] = []
        for snapshot_org, snapshot_instance, snapshot in self._snapshots:
            if snapshot_org != organization_id or snapshot_instance != instance_id:
                continue
            if not query.from_timestamp <= snapshot.collected_at <= query.to_timestamp:
                continue
            match = _find_entry(snapshot.entries, query.tablespace_name)
            if match is None:
                continue
            points.append(
                TablespaceHistoryPoint(
                    collected_at=snapshot.collected_at,
                    used_bytes=match.used_bytes,
                    total_bytes=match.total_bytes,
                    used_rate_percent=match.used_rate_percent,
                )
            )
        ordered = tuple(sorted(points, key=lambda point: point.collected_at))
        return TablespaceHistoryView(entries=ordered)


def _within_window(when: datetime, query: TablespaceSnapshotQuery) -> bool:
    if query.collected_after is not None and when < query.collected_after:
        return False
    if query.collected_before is not None and when > query.collected_before:
        return False
    return True


def _find_entry(
    entries: tuple[TablespaceEntryRow, ...],
    tablespace_name: str,
) -> TablespaceEntryRow | None:
    for entry in entries:
        if entry.tablespace_name == tablespace_name:
            return entry
    return None
