"""Performance Schema probe during MySQL instance validation (ADR-0007).

The probe enriches `validation.detail` with a Chinese hint when PS is
disabled or the ring buffer size is below the recommended floor, but it
never downgrades `status` away from PASSED (slow-query SPEC).
"""

from typing import Literal

import pymysql
import pytest

from db_monitor_api.control_plane.domain import (
    MySQLConnectionConfig,
    ValidationStatus,
)
from db_monitor_api.control_plane.mysql_validation import (
    PS_DISABLED_HINT,
    PS_HISTORY_SIZE_HINT_PREFIX,
    PS_PROBE_FAILED_HINT,
    PyMySQLConnectionValidator,
)


class FakeCursor:
    def __init__(self, *, results: list[tuple[object, ...] | None]) -> None:
        self._results = list(results)
        self.executed: list[str] = []
        self._pending: tuple[object, ...] | None = None
        self._mode: Literal["ok", "error"] = "ok"
        self._raise_on_queries: set[str] = set()

    def fail_on(self, substring: str) -> None:
        self._raise_on_queries.add(substring)

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: object) -> Literal[False]:
        del args
        return False

    def execute(self, query: str, params: object = None) -> None:
        del params
        self.executed.append(query)
        for needle in self._raise_on_queries:
            if needle in query:
                raise pymysql.MySQLError(f"probe failed on {query}")
        self._pending = self._results.pop(0) if self._results else None

    def fetchone(self) -> tuple[object, ...] | None:
        return self._pending


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *args: object) -> Literal[False]:
        del args
        return False

    def cursor(self) -> FakeCursor:
        return self._cursor


def _config() -> MySQLConnectionConfig:
    return MySQLConnectionConfig(
        database="mysql",
        host="127.0.0.1",
        password="secret",
        port=3306,
        username="db_monitor",
    )


def _install_connection(
    monkeypatch: pytest.MonkeyPatch, cursor: FakeCursor
) -> None:
    monkeypatch.setattr(
        "db_monitor_api.control_plane.mysql_validation.pymysql.connect",
        lambda **_: FakeConnection(cursor),
    )


def test_validation_passes_cleanly_when_ps_enabled_and_size_meets_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        results=[
            ("8.4.0",),
            ("0",),
            ("1",),
            ("20000",),
        ]
    )
    _install_connection(monkeypatch, cursor)

    result = PyMySQLConnectionValidator().validate(_config())

    assert result.status is ValidationStatus.PASSED
    assert "Connection validated successfully." in result.detail
    assert PS_DISABLED_HINT not in result.detail
    assert PS_HISTORY_SIZE_HINT_PREFIX not in result.detail


def test_validation_passes_with_disabled_ps_hint_when_ps_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        results=[
            ("8.4.0",),
            ("0",),
            ("0",),
            ("10000",),
        ]
    )
    _install_connection(monkeypatch, cursor)

    result = PyMySQLConnectionValidator().validate(_config())

    assert result.status is ValidationStatus.PASSED, (
        "ADR-0007: PS off must NOT block validation PASSED"
    )
    assert PS_DISABLED_HINT in result.detail


def test_validation_passes_with_size_hint_when_history_too_small(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        results=[
            ("8.4.0",),
            ("0",),
            ("1",),
            ("512",),
        ]
    )
    _install_connection(monkeypatch, cursor)

    result = PyMySQLConnectionValidator().validate(_config())

    assert result.status is ValidationStatus.PASSED
    assert PS_HISTORY_SIZE_HINT_PREFIX in result.detail
    assert "512" in result.detail


def test_validation_still_passes_when_probe_query_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        results=[
            ("8.4.0",),
            ("0",),
        ]
    )
    cursor.fail_on("@@performance_schema")
    _install_connection(monkeypatch, cursor)

    result = PyMySQLConnectionValidator().validate(_config())

    assert result.status is ValidationStatus.PASSED
    assert PS_PROBE_FAILED_HINT in result.detail
