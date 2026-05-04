from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[2]
RELEASE_RUNBOOK = REPO_ROOT / "docs" / "operator-release-baseline.md"
RELEASE_CHECKLIST = REPO_ROOT / "docs" / "operator-release-checklist.md"
ROLLBACK_CHECKLIST = REPO_ROOT / "docs" / "operator-rollback-checklist.md"
ENVIRONMENT_RUNBOOK = REPO_ROOT / "docs" / "operator-launch-environment-baseline.md"
ACCEPTANCE_CHECKLIST = REPO_ROOT / "docs" / "operator-launch-acceptance-checklist.md"


def test_release_baseline_contract_maps_to_real_repository_commands() -> None:
    package_scripts = _package_scripts()
    runbook = RELEASE_RUNBOOK.read_text(encoding="utf-8")

    assert RELEASE_RUNBOOK.exists()
    assert RELEASE_CHECKLIST.exists()
    assert ROLLBACK_CHECKLIST.exists()
    assert ENVIRONMENT_RUNBOOK.exists()
    assert ACCEPTANCE_CHECKLIST.exists()
    assert "pnpm dev:deps:up" in runbook
    assert "pnpm dev:deps:down" in runbook
    assert "pnpm smoke" in runbook
    assert "pnpm test:hardening:signoff" in runbook
    assert "pnpm test:launch-readiness:signoff" in runbook
    assert "pnpm test:api:readiness" in runbook
    assert "pnpm test:background-processes" in runbook
    assert "pnpm test:schema:bootstrap" in runbook
    assert "pnpm test:recovery-paths" in runbook
    assert "dev:deps:up" in package_scripts
    assert "dev:deps:down" in package_scripts
    assert "smoke" in package_scripts
    assert "test:api:readiness" in package_scripts
    assert "test:background-processes" in package_scripts
    assert "test:schema:bootstrap" in package_scripts
    assert "test:recovery-paths" in package_scripts


def test_release_baseline_runbook_captures_verification_and_rollback_boundaries() -> None:
    runbook = RELEASE_RUNBOOK.read_text(encoding="utf-8")
    release_checklist = RELEASE_CHECKLIST.read_text(encoding="utf-8")
    rollback_checklist = ROLLBACK_CHECKLIST.read_text(encoding="utf-8")
    acceptance_checklist = ACCEPTANCE_CHECKLIST.read_text(encoding="utf-8")

    assert "Rollback Trigger" in runbook
    assert ".tmp-smoke-api.err.log" in runbook
    assert ".tmp-smoke-web.err.log" in runbook
    assert "pnpm test:hardening:signoff" in release_checklist
    assert "pnpm test:launch-readiness:signoff" in release_checklist
    assert "git diff --check" in acceptance_checklist
    assert "pnpm dev:deps:down" in rollback_checklist
    assert "立即停止继续发布" in rollback_checklist


def _package_scripts() -> dict[str, str]:
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    return dict(package["scripts"])
