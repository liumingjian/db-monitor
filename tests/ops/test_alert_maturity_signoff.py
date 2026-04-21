from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[2]
SIGNOFF_SCRIPT = REPO_ROOT / "scripts" / "test-alert-maturity-signoff.ps1"
RUNBOOK = REPO_ROOT / "docs" / "operator-alert-maturity-baseline.md"
CHECKLIST = REPO_ROOT / "docs" / "operator-alert-maturity-checklist.md"


def test_alert_maturity_signoff_contract_covers_backend_web_and_live_gates() -> None:
    script = SIGNOFF_SCRIPT.read_text(encoding="utf-8")

    assert "pnpm openapi:check" in script
    assert "tests/ops/test_alert_maturity_signoff.py" in script
    assert "tests/alerting_contract" in script
    assert "tests/alerting_workflow" in script
    assert "tests/alerting_noise" in script
    assert "tests/alerting_delivery" in script
    assert "tests/recovery" in script
    assert "tests/api/alerting" in script
    assert "tests/integration/alert_pipeline" in script
    assert "pnpm test" in script
    assert "pnpm typecheck" in script
    assert "pnpm build" in script
    assert "pnpm test:alert-pipeline:postgres" in script
    assert "pnpm test:recovery-paths" in script


def test_alert_maturity_signoff_command_and_docs_are_registered() -> None:
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    runbook = RUNBOOK.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")

    assert "test:alert-maturity:signoff" in package["scripts"]
    assert "./scripts/powershell_shim.py" in package["scripts"]["test:alert-maturity:signoff"]
    assert "./scripts/test-alert-maturity-signoff.ps1" in package["scripts"]["test:alert-maturity:signoff"]
    assert "pnpm test:alert-maturity:signoff" in runbook
    assert "pnpm openapi:check" in runbook
    assert "pnpm test:alert-pipeline:postgres" in runbook
    assert "pnpm test:recovery-paths" in runbook
    assert "无需系统 PowerShell" in runbook
    assert "停止本次 signoff" in runbook
    assert "pnpm test:alert-maturity:signoff" in checklist
