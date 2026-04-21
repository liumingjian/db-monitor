from dataclasses import dataclass

from db_monitor_api.analytics.service import AnalyticsService
from db_monitor_api.alerting.service import AlertingService
from db_monitor_api.auth.repository import AuditRepository
from db_monitor_api.auth.service import AuditService, AuthService, AuthorizationService
from db_monitor_api.control_plane.service import AssetService, SettingsService
from db_monitor_api.health import ReadinessProbe


@dataclass(frozen=True)
class AppRuntime:
    audit_repository: AuditRepository
    audit_service: AuditService
    auth_service: AuthService
    authorization_service: AuthorizationService
    asset_service: AssetService
    analytics_service: AnalyticsService
    alerting_service: AlertingService
    readiness_probe: ReadinessProbe
    runtime_mode: str
    settings_service: SettingsService
