from db_monitor_api.auth.domain import utc_now
from db_monitor_api.control_plane.domain import (
    ConnectionValidation,
    InstanceConnectionConfig,
    MySQLConnectionConfig,
    ValidationStatus,
)
from db_monitor_api.control_plane.mysql_validation import MySQLConnectionValidator
from db_monitor_api.control_plane.oracle_validation import OracleConnectionValidator


class StaticMySQLConnectionValidator(MySQLConnectionValidator):
    def __init__(self) -> None:
        self.next_result = ConnectionValidation(
            checked_at=utc_now(),
            detail="Static validator accepted the connection.",
            server_version="8.4.0",
            status=ValidationStatus.PASSED,
            server_role="primary",
        )

    def validate(self, config: MySQLConnectionConfig) -> ConnectionValidation:
        del config
        return self.next_result


class StaticOracleConnectionValidator(OracleConnectionValidator):
    def __init__(self) -> None:
        self.next_result = ConnectionValidation(
            checked_at=utc_now(),
            detail="Static Oracle validator accepted the connection.",
            server_version="19.21.0.0.0",
            status=ValidationStatus.PASSED,
            server_role="primary",
        )

    def validate(self, config: InstanceConnectionConfig) -> ConnectionValidation:
        del config
        return self.next_result
