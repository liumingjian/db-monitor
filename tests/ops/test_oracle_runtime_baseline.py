from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_RUNBOOK = REPO_ROOT / "docs" / "operator-oracle-runtime-baseline.md"
RUNTIME_CHECKLIST = REPO_ROOT / "docs" / "operator-oracle-runtime-checklist.md"
RUNTIME_ROLLBACK = REPO_ROOT / "docs" / "operator-oracle-runtime-rollback-checklist.md"
RUNTIME_DOCTOR_SCRIPT = REPO_ROOT / "scripts" / "test-oracle-runtime-doctor.ps1"
RUNTIME_SIGNOFF_SCRIPT = REPO_ROOT / "scripts" / "test-oracle-runtime-signoff.ps1"


def test_oracle_runtime_baseline_contract_maps_to_real_repository_commands() -> None:
    package_scripts = _package_scripts()
    runbook = RUNTIME_RUNBOOK.read_text(encoding="utf-8")

    assert RUNTIME_RUNBOOK.exists()
    assert RUNTIME_CHECKLIST.exists()
    assert RUNTIME_ROLLBACK.exists()
    assert RUNTIME_DOCTOR_SCRIPT.exists()
    assert RUNTIME_SIGNOFF_SCRIPT.exists()
    assert "pnpm test:oracle-runtime:doctor" in runbook
    assert "pnpm test:oracle-runtime:signoff" in runbook
    assert "pnpm test:control-plane:postgres" in runbook
    assert "pnpm test:control-plane:oracle" in runbook
    assert "test:oracle-runtime:doctor" in package_scripts
    assert "test:oracle-runtime:signoff" in package_scripts
    assert "test:control-plane:postgres" in package_scripts
    assert "test:control-plane:oracle" in package_scripts


def test_oracle_runtime_baseline_captures_failure_isolation_and_rollback_boundaries() -> None:
    runbook = RUNTIME_RUNBOOK.read_text(encoding="utf-8")
    checklist = RUNTIME_CHECKLIST.read_text(encoding="utf-8")
    rollback = RUNTIME_ROLLBACK.read_text(encoding="utf-8")
    doctor_script = RUNTIME_DOCTOR_SCRIPT.read_text(encoding="utf-8")
    signoff_script = RUNTIME_SIGNOFF_SCRIPT.read_text(encoding="utf-8")

    assert "Rollback Trigger" in runbook
    assert "DPY-3010" in runbook
    assert "docker logs $(docker compose ps -q oracle-xe)" in runbook
    assert "pnpm test:oracle-runtime:doctor" in checklist
    assert "pnpm test:control-plane:oracle" in checklist
    assert "立即停止继续 signoff" in rollback
    assert "import oracledb" in doctor_script
    assert "sqlplus -s system/oracle@//127.0.0.1:1521/XE" in doctor_script
    assert "pnpm test:oracle-runtime:doctor" in signoff_script
    assert "pnpm test:control-plane:oracle" in signoff_script


def _package_scripts() -> dict[str, str]:
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    return dict(package["scripts"])
