from db_monitor_api.analytics.repository import (
    AnalyticsRepository,
    ClickHouseAnalyticsRepository,
    InMemoryAnalyticsRepository,
)
from db_monitor_api.analytics.service import AnalyticsService
from db_monitor_api.alerting.notifier import InMemoryNotifier, Notifier
from db_monitor_api.alerting.postgres_repository import PostgresAlertingRepository
from db_monitor_api.alerting.repository import AlertingRepository, InMemoryAlertingRepository
from db_monitor_api.alerting.service import AlertingService
from db_monitor_api.auth.repository import (
    AuditRepository,
    InMemoryAuditRepository,
    InMemorySessionRepository,
    InMemoryUserRepository,
)
from db_monitor_api.auth.postgres_repository import PostgresAuditRepository
from db_monitor_api.auth.service import (
    AuditService,
    AuthService,
    AuthorizationService,
    PasswordHasher,
)
from db_monitor_api.auth.seed_users import default_seed_users
from db_monitor_api.control_plane.mysql_validation import (
    MySQLConnectionValidator,
    PyMySQLConnectionValidator,
)
from db_monitor_api.control_plane.oracle_validation import (
    OracleConnectionValidator,
    PythonOracleConnectionValidator,
)
from db_monitor_api.control_plane.postgres_repository import PostgresControlPlaneRepository
from db_monitor_api.control_plane.repository import (
    ControlPlaneRepository,
    InMemoryControlPlaneRepository,
)
from db_monitor_api.control_plane.service import AssetService, SettingsService
from db_monitor_api.health import (
    ClickHouseDependencyCheck,
    DependencyCheck,
    PostgresDependencyCheck,
    ReadinessProbe,
    StaticDependencyCheck,
)
from db_monitor_api.runtime import AppRuntime
from db_monitor_api.runtime_views.kill import (
    ProcesslistKiller,
    ProcesslistKillService,
    PyMySQLProcesslistKiller,
)
from db_monitor_api.runtime_views.repository import (
    ClickHouseProcesslistRepository,
    InMemoryProcesslistRepository,
    ProcesslistRepository,
)
from db_monitor_api.runtime_views.service import ProcesslistService
from db_monitor_api.settings import ApiSettings, ClickHouseSettings, RuntimeMode
from db_monitor_schema.runtime import verify_api_runtime_schema


def build_runtime_from_settings(settings: ApiSettings) -> AppRuntime:
    if settings.runtime_mode is RuntimeMode.LOCAL:
        return build_local_runtime()
    if settings.clickhouse is None or settings.postgres_dsn is None:
        raise RuntimeError("Postgres runtime requires PostgreSQL and ClickHouse settings.")
    return build_postgres_runtime(
        clickhouse=settings.clickhouse,
        postgres_dsn=settings.postgres_dsn,
    )


def build_local_runtime(
    *,
    analytics_repository: AnalyticsRepository | None = None,
    alerting_repository: AlertingRepository | None = None,
    control_plane_repository: ControlPlaneRepository | None = None,
    dependency_checks: tuple[DependencyCheck, ...] | None = None,
    mysql_validator: MySQLConnectionValidator | None = None,
    oracle_validator: OracleConnectionValidator | None = None,
    notifier: Notifier | None = None,
    processlist_repository: ProcesslistRepository | None = None,
    processlist_killer: ProcesslistKiller | None = None,
) -> AppRuntime:
    return _build_runtime(
        analytics_repository=analytics_repository or InMemoryAnalyticsRepository(),
        alerting_repository=alerting_repository or InMemoryAlertingRepository(),
        audit_repository=InMemoryAuditRepository(),
        control_plane_repository=control_plane_repository or InMemoryControlPlaneRepository(),
        dependency_checks=dependency_checks
        or (
            StaticDependencyCheck(
                detail="Local in-memory repositories active.",
                name="runtime",
            ),
        ),
        mysql_validator=mysql_validator or PyMySQLConnectionValidator(),
        oracle_validator=oracle_validator or PythonOracleConnectionValidator(),
        notifier=notifier or InMemoryNotifier(),
        processlist_repository=processlist_repository or InMemoryProcesslistRepository(),
        processlist_killer=processlist_killer or PyMySQLProcesslistKiller(),
        runtime_mode=RuntimeMode.LOCAL.value,
    )


def build_postgres_runtime(
    *,
    analytics_repository: AnalyticsRepository | None = None,
    alerting_repository: AlertingRepository | None = None,
    clickhouse: ClickHouseSettings | None = None,
    dependency_checks: tuple[DependencyCheck, ...] | None = None,
    postgres_dsn: str,
    mysql_validator: MySQLConnectionValidator | None = None,
    oracle_validator: OracleConnectionValidator | None = None,
    notifier: Notifier | None = None,
    processlist_repository: ProcesslistRepository | None = None,
    processlist_killer: ProcesslistKiller | None = None,
) -> AppRuntime:
    verify_api_runtime_schema(
        analytics_repository=analytics_repository,
        clickhouse=clickhouse,
        postgres_dsn=postgres_dsn,
    )
    resolved_analytics = analytics_repository or _build_clickhouse_analytics_repository(clickhouse)
    resolved_processlist = processlist_repository or _build_clickhouse_processlist_repository(
        clickhouse
    )
    return _build_runtime(
        analytics_repository=resolved_analytics,
        alerting_repository=alerting_repository or PostgresAlertingRepository(postgres_dsn=postgres_dsn),
        audit_repository=PostgresAuditRepository(postgres_dsn=postgres_dsn),
        control_plane_repository=PostgresControlPlaneRepository(postgres_dsn=postgres_dsn),
        dependency_checks=dependency_checks
        or _build_postgres_dependency_checks(
            analytics_repository=analytics_repository,
            clickhouse=clickhouse,
            postgres_dsn=postgres_dsn,
        ),
        mysql_validator=mysql_validator or PyMySQLConnectionValidator(),
        oracle_validator=oracle_validator or PythonOracleConnectionValidator(),
        notifier=notifier or InMemoryNotifier(),
        processlist_repository=resolved_processlist,
        processlist_killer=processlist_killer or PyMySQLProcesslistKiller(),
        runtime_mode=RuntimeMode.POSTGRES.value,
    )


def _build_runtime(
    *,
    analytics_repository: AnalyticsRepository,
    alerting_repository: AlertingRepository,
    audit_repository: AuditRepository,
    control_plane_repository: ControlPlaneRepository,
    dependency_checks: tuple[DependencyCheck, ...],
    mysql_validator: MySQLConnectionValidator,
    oracle_validator: OracleConnectionValidator,
    notifier: Notifier,
    processlist_repository: ProcesslistRepository,
    processlist_killer: ProcesslistKiller,
    runtime_mode: str,
) -> AppRuntime:
    password_hasher = PasswordHasher()
    audit_service = AuditService(audit_repository=audit_repository)
    auth_service = AuthService(
        audit_service=audit_service,
        password_hasher=password_hasher,
        session_repository=InMemorySessionRepository(),
        user_repository=InMemoryUserRepository.from_seed_users(
            seed_users=default_seed_users(),
            password_hasher=password_hasher,
        ),
    )
    authorization_service = AuthorizationService(audit_service=audit_service)
    return AppRuntime(
        audit_repository=audit_repository,
        audit_service=audit_service,
        auth_service=auth_service,
        authorization_service=authorization_service,
        asset_service=AssetService(
            audit_service=audit_service,
            mysql_validator=mysql_validator,
            oracle_validator=oracle_validator,
            repository=control_plane_repository,
        ),
        analytics_service=AnalyticsService(
            analytics_repository=analytics_repository,
            control_plane_repository=control_plane_repository,
        ),
        alerting_service=AlertingService(
            audit_service=audit_service,
            control_plane_repository=control_plane_repository,
            notifier=notifier,
            repository=alerting_repository,
        ),
        processlist_service=ProcesslistService(
            control_plane_repository=control_plane_repository,
            processlist_repository=processlist_repository,
        ),
        processlist_kill_service=ProcesslistKillService(
            audit_service=audit_service,
            control_plane_repository=control_plane_repository,
            killer=processlist_killer,
        ),
        readiness_probe=ReadinessProbe(checks=dependency_checks),
        runtime_mode=runtime_mode,
        settings_service=SettingsService(
            audit_service=audit_service,
            repository=control_plane_repository,
        ),
    )


def _build_clickhouse_analytics_repository(
    clickhouse: ClickHouseSettings | None,
) -> AnalyticsRepository:
    if clickhouse is None:
        raise RuntimeError(
            "ClickHouse settings are required when no analytics repository is injected."
        )
    return ClickHouseAnalyticsRepository(
        database=clickhouse.database,
        endpoint=clickhouse.endpoint,
        password=clickhouse.password,
        username=clickhouse.username,
    )


def _build_clickhouse_processlist_repository(
    clickhouse: ClickHouseSettings | None,
) -> ProcesslistRepository:
    if clickhouse is None:
        raise RuntimeError(
            "ClickHouse settings are required when no processlist repository is injected."
        )
    return ClickHouseProcesslistRepository(
        database=clickhouse.database,
        endpoint=clickhouse.endpoint,
        password=clickhouse.password,
        username=clickhouse.username,
    )


def _build_postgres_dependency_checks(
    *,
    analytics_repository: AnalyticsRepository | None,
    clickhouse: ClickHouseSettings | None,
    postgres_dsn: str,
) -> tuple[DependencyCheck, ...]:
    checks: list[DependencyCheck] = [PostgresDependencyCheck(postgres_dsn=postgres_dsn)]
    if analytics_repository is None:
        if clickhouse is None:
            raise RuntimeError(
                "ClickHouse settings are required when no analytics repository is injected."
            )
        checks.append(
            ClickHouseDependencyCheck(
                database=clickhouse.database,
                endpoint=clickhouse.endpoint,
                password=clickhouse.password,
                username=clickhouse.username,
            )
        )
        return tuple(checks)
    checks.append(
        StaticDependencyCheck(
            detail="Custom analytics repository injected.",
            name="analytics",
        )
    )
    return tuple(checks)


