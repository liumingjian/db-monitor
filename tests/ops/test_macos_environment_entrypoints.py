from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_JSON = REPO_ROOT / "package.json"
RELEASE_RUNBOOK = REPO_ROOT / "docs" / "operator-release-baseline.md"
ALERT_RUNBOOK = REPO_ROOT / "docs" / "operator-alert-maturity-baseline.md"
ORACLE_RUNTIME_RUNBOOK = REPO_ROOT / "docs" / "operator-oracle-runtime-baseline.md"
PLAYWRIGHT_SMOKE_CONFIG = REPO_ROOT / "playwright.smoke.config.ts"


def test_macos_environment_entrypoints_use_repo_local_runner() -> None:
    package = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))

    expected_script_targets = {
        "dev:deps:down": "./scripts/dev-down.ps1",
        "dev:deps:up": "./scripts/dev-up.ps1",
        "docker:target:down": "./scripts/docker-target-down.ps1",
        "docker:target:up": "./scripts/docker-target-up.ps1",
        "smoke:web": "./scripts/test-web-smoke.ps1",
        "test:api:readiness": "./scripts/test-api-runtime-readiness.ps1",
        "test:analytics:clickhouse": "./scripts/test-analytics-clickhouse.ps1",
        "test:background-processes": "./scripts/test-background-processes.ps1",
        "test:control-plane:oracle": "./scripts/test-control-plane-oracle.ps1",
        "test:control-plane:postgres": "./scripts/test-control-plane-postgres.ps1",
        "test:docker-target:signoff": "./scripts/test-docker-target-signoff.ps1",
        "test:hardening:signoff": "./scripts/test-hardening-signoff.ps1",
        "test:launch-readiness:signoff": "./scripts/test-launch-readiness-signoff.ps1",
        "test:metrics-pipeline:live": "./scripts/test-metrics-pipeline-live.ps1",
        "test:oracle-runtime:doctor": "./scripts/test-oracle-runtime-doctor.ps1",
        "test:oracle-runtime:signoff": "./scripts/test-oracle-runtime-signoff.ps1",
        "test:schema:bootstrap": "./scripts/test-schema-bootstrap.ps1",
    }

    for script_name, target in expected_script_targets.items():
        command = package["scripts"][script_name]
        assert "./scripts/powershell_shim.py" in command
        assert target in command


def test_runbooks_mark_root_commands_as_macos_safe() -> None:
    release_runbook = RELEASE_RUNBOOK.read_text(encoding="utf-8")
    alert_runbook = ALERT_RUNBOOK.read_text(encoding="utf-8")
    oracle_runtime_runbook = ORACLE_RUNTIME_RUNBOOK.read_text(encoding="utf-8")

    assert "macOS" in release_runbook
    assert "无需系统 PowerShell" in release_runbook
    assert "macOS" in alert_runbook
    assert "无需系统 PowerShell" in alert_runbook
    assert "macOS" in oracle_runtime_runbook
    assert "无需系统 PowerShell" in oracle_runtime_runbook


def test_smoke_uses_playwright_managed_chromium_instead_of_system_edge() -> None:
    config = PLAYWRIGHT_SMOKE_CONFIG.read_text(encoding="utf-8")

    assert 'browserName: "chromium"' in config
    assert 'channel: "msedge"' not in config
