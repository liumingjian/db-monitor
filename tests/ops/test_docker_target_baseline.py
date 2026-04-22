from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_JSON = REPO_ROOT / "package.json"
DOCKER_RUNBOOK = REPO_ROOT / "docs" / "operator-docker-target-baseline.md"
RELEASE_RUNBOOK = REPO_ROOT / "docs" / "operator-release-baseline.md"
REHEARSAL_RUNBOOK = REPO_ROOT / "docs" / "operator-prelaunch-rehearsal-runbook.md"
COMPOSE_TARGET = REPO_ROOT / "compose.target.yaml"
RUNTIME_DOCKERFILE = REPO_ROOT / "Dockerfile.runtime"
WEB_DOCKERFILE = REPO_ROOT / "Dockerfile.web"
STACK_SCRIPT = REPO_ROOT / "scripts" / "docker_target_stack.py"
RUNTIME_SCRIPT = REPO_ROOT / "scripts" / "docker_target_runtime.py"
SMOKE_SPEC = REPO_ROOT / "smoke" / "phase-one.spec.ts"


def test_docker_target_baseline_maps_to_real_repo_assets() -> None:
    package_scripts = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))["scripts"]
    runbook = DOCKER_RUNBOOK.read_text(encoding="utf-8")

    assert COMPOSE_TARGET.exists()
    assert RUNTIME_DOCKERFILE.exists()
    assert WEB_DOCKERFILE.exists()
    assert STACK_SCRIPT.exists()
    assert RUNTIME_SCRIPT.exists()
    assert "docker:target:up" in package_scripts
    assert "docker:target:down" in package_scripts
    assert "test:docker-target:signoff" in package_scripts
    assert "pnpm docker:target:up" in runbook
    assert "pnpm test:docker-target:signoff" in runbook
    assert "pnpm docker:target:down" in runbook
    assert "bootstrap-runtime" in runbook
    assert "seed-target-runtime" in runbook


def test_docker_target_path_is_linked_from_launch_and_rehearsal_docs() -> None:
    release_runbook = RELEASE_RUNBOOK.read_text(encoding="utf-8")
    rehearsal_runbook = REHEARSAL_RUNBOOK.read_text(encoding="utf-8")
    smoke_spec = SMOKE_SPEC.read_text(encoding="utf-8")

    assert "operator-docker-target-baseline.md" in release_runbook
    assert "operator-docker-target-baseline.md" in rehearsal_runbook
    assert "DB_MONITOR_SMOKE_INSTANCE_HOST" in smoke_spec
    assert "DB_MONITOR_SMOKE_INSTANCE_PASSWORD" in smoke_spec
