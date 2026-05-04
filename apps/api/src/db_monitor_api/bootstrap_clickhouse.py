"""ClickHouse-backed repository/ dependency check factories for bootstrap.

Extracted from `bootstrap.py` to keep the top-level orchestration file
under the 300-line hard limit while still exposing a DRY seam for wiring
ClickHouse-dependent repositories in the postgres runtime path.
"""

from db_monitor_api.analytics.repository import (
    AnalyticsRepository,
    ClickHouseAnalyticsRepository,
)
from db_monitor_api.health import (
    ClickHouseDependencyCheck,
    DependencyCheck,
    PostgresDependencyCheck,
    StaticDependencyCheck,
)
from db_monitor_api.runtime_views.repository import (
    ClickHouseProcesslistRepository,
    ProcesslistRepository,
)
from db_monitor_api.runtime_views.slow_query_repository import (
    ClickHouseSlowQueryRepository,
    SlowQueryRepository,
)
from db_monitor_api.runtime_views.tablespace_clickhouse import ClickHouseTablespaceRepository
from db_monitor_api.runtime_views.tablespace_repository import TablespaceRepository
from db_monitor_api.settings import ClickHouseSettings


def build_clickhouse_analytics_repository(
    clickhouse: ClickHouseSettings | None,
) -> AnalyticsRepository:
    _require_clickhouse(clickhouse, "analytics")
    assert clickhouse is not None
    return ClickHouseAnalyticsRepository(
        database=clickhouse.database,
        endpoint=clickhouse.endpoint,
        password=clickhouse.password,
        username=clickhouse.username,
    )


def build_clickhouse_processlist_repository(
    clickhouse: ClickHouseSettings | None,
) -> ProcesslistRepository:
    _require_clickhouse(clickhouse, "processlist")
    assert clickhouse is not None
    return ClickHouseProcesslistRepository(
        database=clickhouse.database,
        endpoint=clickhouse.endpoint,
        password=clickhouse.password,
        username=clickhouse.username,
    )


def build_clickhouse_slow_query_repository(
    clickhouse: ClickHouseSettings | None,
) -> SlowQueryRepository:
    _require_clickhouse(clickhouse, "slow_query")
    assert clickhouse is not None
    return ClickHouseSlowQueryRepository(
        database=clickhouse.database,
        endpoint=clickhouse.endpoint,
        password=clickhouse.password,
        username=clickhouse.username,
    )


def build_clickhouse_tablespace_repository(
    clickhouse: ClickHouseSettings | None,
) -> TablespaceRepository:
    _require_clickhouse(clickhouse, "tablespace")
    assert clickhouse is not None
    return ClickHouseTablespaceRepository(
        database=clickhouse.database,
        endpoint=clickhouse.endpoint,
        password=clickhouse.password,
        username=clickhouse.username,
    )


def build_postgres_dependency_checks(
    *,
    analytics_repository: AnalyticsRepository | None,
    clickhouse: ClickHouseSettings | None,
    postgres_dsn: str,
) -> tuple[DependencyCheck, ...]:
    checks: list[DependencyCheck] = [PostgresDependencyCheck(postgres_dsn=postgres_dsn)]
    if analytics_repository is not None:
        checks.append(
            StaticDependencyCheck(
                detail="Custom analytics repository injected.",
                name="analytics",
            )
        )
        return tuple(checks)
    _require_clickhouse(clickhouse, "analytics")
    assert clickhouse is not None
    checks.append(
        ClickHouseDependencyCheck(
            database=clickhouse.database,
            endpoint=clickhouse.endpoint,
            password=clickhouse.password,
            username=clickhouse.username,
        )
    )
    return tuple(checks)


def _require_clickhouse(clickhouse: ClickHouseSettings | None, scope: str) -> None:
    if clickhouse is None:
        raise RuntimeError(
            f"ClickHouse settings are required when no {scope} repository is injected."
        )
