from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[2]
SIGNOFF_SCRIPT = REPO_ROOT / "scripts" / "test-hardening-signoff.ps1"


def test_hardening_signoff_contract_covers_all_operational_layers() -> None:
    script = SIGNOFF_SCRIPT.read_text(encoding="utf-8")

    assert "pnpm lint" in script
    assert "pnpm typecheck" in script
    assert "uv run ruff check ." in script
    assert "uv run mypy apps tests gates" in script
    assert "uv run pytest tests" in script
    assert "./scripts/test-api-runtime-readiness.ps1" in script
    assert "./scripts/test-background-processes.ps1" in script
    assert "./scripts/test-schema-bootstrap.ps1" in script
    assert "./scripts/test-recovery-paths.ps1" in script
    assert "pnpm smoke" in script


def test_hardening_signoff_command_is_registered_at_root() -> None:
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    assert "test:hardening:signoff" in package["scripts"]
    assert "./scripts/powershell_shim.py" in package["scripts"]["test:hardening:signoff"]
    assert "./scripts/test-hardening-signoff.ps1" in package["scripts"]["test:hardening:signoff"]
