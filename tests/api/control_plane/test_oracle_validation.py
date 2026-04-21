import subprocess

from db_monitor_api.control_plane.domain import InstanceConnectionConfig, ValidationStatus
from db_monitor_api.control_plane.oracle_validation import (
    DEFAULT_ORACLE_SQLPLUS_LOCALHOST_ALIAS,
    PythonOracleConnectionValidator,
)


def test_oracle_validator_uses_sqlplus_docker_fallback_for_localhost(monkeypatch) -> None:
    config = InstanceConnectionConfig(
        database="XE",
        host="127.0.0.1",
        password="oracle",
        port=15211,
        username="system",
    )
    captured: dict[str, object] = {}

    monkeypatch.setenv("DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER", "oracle-xe-local")
    monkeypatch.setattr(
        "db_monitor_api.control_plane.oracle_validation._load_oracle_driver",
        lambda: None,
    )

    def fake_run(
        cmd: list[str],
        *,
        capture_output: bool,
        check: bool,
        env: dict[str, str],
        text: bool,
    ) -> subprocess.CompletedProcess[str]:
        del capture_output, check, text
        captured["cmd"] = cmd
        captured["env"] = env
        return subprocess.CompletedProcess(cmd, 0, stdout="1\n", stderr="")

    monkeypatch.setattr(
        "db_monitor_api.control_plane.oracle_validation.subprocess.run",
        fake_run,
    )

    validation = PythonOracleConnectionValidator().validate(config)

    assert validation.status is ValidationStatus.PASSED
    assert "sqlplus via docker container oracle-xe-local" in validation.detail
    env = captured["env"]
    assert isinstance(env, dict)
    assert env["ORACLE_HOST"] == DEFAULT_ORACLE_SQLPLUS_LOCALHOST_ALIAS


def test_oracle_validator_reports_missing_driver_when_no_fallback(monkeypatch) -> None:
    config = InstanceConnectionConfig(
        database="XE",
        host="oracle.internal",
        password="oracle",
        port=1521,
        username="system",
    )

    monkeypatch.delenv("DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER", raising=False)
    monkeypatch.setattr(
        "db_monitor_api.control_plane.oracle_validation._load_oracle_driver",
        lambda: None,
    )

    validation = PythonOracleConnectionValidator().validate(config)

    assert validation.status is ValidationStatus.FAILED
    assert "python-oracledb or cx_Oracle" in validation.detail
