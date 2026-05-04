from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_JSON = REPO_ROOT / "package.json"
RELEASE_RUNBOOK = REPO_ROOT / "docs" / "operator-release-baseline.md"
ENVIRONMENT_RUNBOOK = REPO_ROOT / "docs" / "operator-launch-environment-baseline.md"
ACCEPTANCE_CHECKLIST = REPO_ROOT / "docs" / "operator-launch-acceptance-checklist.md"
ROLLBACK_CHECKLIST = REPO_ROOT / "docs" / "operator-rollback-checklist.md"
SIGNOFF_SCRIPT = REPO_ROOT / "scripts" / "test-launch-readiness-signoff.ps1"


def test_launch_readiness_baseline_maps_to_real_repository_entrypoints() -> None:
    package_scripts = _package_scripts()
    release_runbook = RELEASE_RUNBOOK.read_text(encoding="utf-8")
    signoff_script = SIGNOFF_SCRIPT.read_text(encoding="utf-8")

    assert RELEASE_RUNBOOK.exists()
    assert ENVIRONMENT_RUNBOOK.exists()
    assert ACCEPTANCE_CHECKLIST.exists()
    assert SIGNOFF_SCRIPT.exists()
    assert "internal single-environment" in release_runbook
    assert "pnpm test:hardening:signoff" in release_runbook
    assert "pnpm test:oracle-runtime:signoff" in release_runbook
    assert "pnpm test:launch-readiness:signoff" in release_runbook
    assert "test:launch-readiness:signoff" in package_scripts
    assert "pnpm test:hardening:signoff" in signoff_script
    assert "pnpm test:oracle-runtime:signoff" in signoff_script
    assert "git diff --check" in signoff_script


def test_launch_environment_contract_captures_runtime_and_secret_boundaries() -> None:
    environment_runbook = ENVIRONMENT_RUNBOOK.read_text(encoding="utf-8")
    acceptance_checklist = ACCEPTANCE_CHECKLIST.read_text(encoding="utf-8")
    rollback_checklist = ROLLBACK_CHECKLIST.read_text(encoding="utf-8")

    assert "DB_MONITOR_RUNTIME" in environment_runbook
    assert "DB_MONITOR_POSTGRES_DSN" in environment_runbook
    assert "DB_MONITOR_REDIS_URL" in environment_runbook
    assert "DB_MONITOR_CLICKHOUSE_DATABASE" in environment_runbook
    assert "DB_MONITOR_CLICKHOUSE_ENDPOINT" in environment_runbook
    assert "DB_MONITOR_CLICKHOUSE_USERNAME" in environment_runbook
    assert "DB_MONITOR_CLICKHOUSE_PASSWORD" in environment_runbook
    assert "DB_MONITOR_API_BASE_URL" in environment_runbook
    assert "DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER" in environment_runbook
    assert "不得写入源码" in environment_runbook
    assert "pnpm test:launch-readiness:signoff" in acceptance_checklist
    assert "git diff --check" in acceptance_checklist
    assert "launch gate" in rollback_checklist


def _package_scripts() -> dict[str, str]:
    package = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    return dict(package["scripts"])
