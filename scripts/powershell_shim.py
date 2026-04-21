#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_PORT = 38100
WEB_PORT = 38101


def run(cmd: list[str], *, env_overrides: dict[str, str] | None = None) -> None:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    printable = " ".join(shlex.quote(part) for part in cmd)
    print(f"+ {printable}", flush=True)
    subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=True)


def capture(cmd: list[str], *, env_overrides: dict[str, str] | None = None) -> str:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    printable = " ".join(shlex.quote(part) for part in cmd)
    print(f"+ {printable}", flush=True)
    completed = subprocess.run(
        cmd,
        capture_output=True,
        cwd=REPO_ROOT,
        env=env,
        check=True,
        text=True,
    )
    stdout = completed.stdout.strip()
    if stdout:
        print(stdout, flush=True)
    return stdout


@contextmanager
def compose_services(*services: str):
    run(["docker", "compose", "up", "-d", *services])
    try:
        yield
    finally:
        run(["docker", "compose", "stop", *services])


@contextmanager
def oracle_gate_container():
    legacy_container = "oracle-xe-local"
    if _docker_container_exists(legacy_container):
        started_here = False
        if not _docker_container_running(legacy_container):
            run(["docker", "start", legacy_container])
            started_here = True
        try:
            yield legacy_container
        finally:
            if started_here:
                run(["docker", "stop", legacy_container])
        return

    with compose_services("oracle-xe"):
        yield _compose_container_id("oracle-xe")


def wait_http_200(url: str, name: str, *, attempts: int = 60, timeout_seconds: int = 3) -> None:
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(1)
    raise RuntimeError(f"{name} did not become healthy at {url} within {attempts} seconds.")


def terminate_process(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def show_log_if_present(path: Path) -> None:
    if path.exists():
        print(path.read_text(encoding="utf-8"), flush=True)


@contextmanager
def started_process(
    cmd: list[str],
    *,
    env_overrides: dict[str, str] | None = None,
    stdout_path: Path,
    stderr_path: Path,
):
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    printable = " ".join(shlex.quote(part) for part in cmd)
    print(f"+ {printable}", flush=True)

    with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr_file:
        process = subprocess.Popen(
            cmd,
            cwd=REPO_ROOT,
            env=env,
            stdout=stdout_file,
            stderr=stderr_file,
            text=True,
            start_new_session=True,
        )

    try:
        yield process
    finally:
        terminate_process(process)


def default_postgres_test_dsn() -> str:
    return "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor"


def default_clickhouse_env() -> dict[str, str]:
    return {
        "DB_MONITOR_CLICKHOUSE_DATABASE": "db_monitor",
        "DB_MONITOR_CLICKHOUSE_ENDPOINT": "http://127.0.0.1:8123",
        "DB_MONITOR_CLICKHOUSE_PASSWORD": "db_monitor",
        "DB_MONITOR_CLICKHOUSE_USERNAME": "db_monitor",
    }


def default_oracle_gate_env() -> dict[str, str]:
    return {
        "DB_MONITOR_ORACLE_TEST_HOST": "127.0.0.1",
        "DB_MONITOR_ORACLE_TEST_PASSWORD": "oracle",
        "DB_MONITOR_ORACLE_TEST_PORT": "15211",
        "DB_MONITOR_ORACLE_TEST_SERVICE": "XE",
        "DB_MONITOR_ORACLE_TEST_USERNAME": "system",
    }


def handle_dev_up() -> None:
    run(["docker", "compose", "-f", "compose.yaml", "up", "-d"])
    print("Local foundation dependencies are running.", flush=True)


def handle_dev_down() -> None:
    run(["docker", "compose", "-f", "compose.yaml", "down"])


def handle_alert_maturity_signoff() -> None:
    commands = [
        ["pnpm", "openapi:check"],
        [
            "uv",
            "run",
            "pytest",
            "tests/ops/test_alert_maturity_signoff.py",
            "tests/alerting_contract",
            "tests/alerting_workflow",
            "tests/alerting_noise",
            "tests/alerting_delivery",
            "tests/recovery",
            "tests/api/alerting",
            "tests/integration/alert_pipeline",
        ],
        ["pnpm", "test"],
        ["pnpm", "typecheck"],
        ["pnpm", "build"],
        ["pnpm", "test:alert-pipeline:postgres"],
        ["pnpm", "test:recovery-paths"],
    ]
    for cmd in commands:
        run(cmd)


def handle_alert_pipeline_postgres() -> None:
    env = {"DB_MONITOR_POSTGRES_TEST_DSN": default_postgres_test_dsn()}
    with compose_services("postgres"):
        run(
            ["uv", "run", "pytest", "gates/alerting/test_alert_pipeline_postgres.py"],
            env_overrides=env,
        )


def handle_analytics_clickhouse() -> None:
    with compose_services("clickhouse"):
        run(
            ["uv", "run", "pytest", "gates/analytics/test_analytics_clickhouse_live.py"],
            env_overrides=default_clickhouse_env(),
        )


def handle_api_runtime_readiness() -> None:
    env = {
        "DB_MONITOR_RUNTIME": "postgres",
        "DB_MONITOR_POSTGRES_DSN": default_postgres_test_dsn(),
        **default_clickhouse_env(),
    }
    with compose_services("postgres", "clickhouse"):
        run(
            ["uv", "run", "pytest", "gates/api/test_api_runtime_readiness_live.py"],
            env_overrides=env,
        )


def handle_background_processes() -> None:
    env = {
        "DB_MONITOR_RUNTIME": "postgres",
        "DB_MONITOR_POSTGRES_DSN": default_postgres_test_dsn(),
        "DB_MONITOR_REDIS_URL": "redis://127.0.0.1:6379/0",
        **default_clickhouse_env(),
    }
    with compose_services("postgres", "clickhouse", "redis"):
        run(
            ["uv", "run", "pytest", "gates/processes/test_background_processes_live.py"],
            env_overrides=env,
        )


def handle_control_plane_postgres() -> None:
    env = {"DB_MONITOR_POSTGRES_TEST_DSN": default_postgres_test_dsn()}
    with compose_services("postgres"):
        run(
            [
                "uv",
                "run",
                "pytest",
                "tests/integration/control_plane/test_control_plane_postgres.py",
            ],
            env_overrides=env,
        )


def handle_control_plane_oracle() -> None:
    with compose_services("postgres"):
        with oracle_gate_container() as container_ref:
            env = {
                "DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER": container_ref,
                "DB_MONITOR_POSTGRES_TEST_DSN": default_postgres_test_dsn(),
                **default_oracle_gate_env(),
            }
            run(
                ["uv", "run", "pytest", "gates/control_plane/test_control_plane_oracle_live.py"],
                env_overrides=env,
            )


def handle_hardening_signoff() -> None:
    commands = [
        ["pnpm", "lint"],
        ["pnpm", "typecheck"],
        ["uv", "run", "ruff", "check", "."],
        ["uv", "run", "mypy", "apps", "tests", "gates"],
        ["uv", "run", "pytest", "tests"],
        ["pnpm", "test:api:readiness"],
        ["pnpm", "test:background-processes"],
        ["pnpm", "test:schema:bootstrap"],
        ["pnpm", "test:recovery-paths"],
        ["pnpm", "smoke"],
    ]
    for cmd in commands:
        run(cmd)


def handle_metrics_pipeline_live() -> None:
    env = {
        "DB_MONITOR_REDIS_URL": "redis://127.0.0.1:6379/0",
        **default_clickhouse_env(),
    }
    with compose_services("clickhouse", "redis"):
        run(
            ["uv", "run", "pytest", "gates/metrics_pipeline/test_metrics_pipeline_live.py"],
            env_overrides=env,
        )


def handle_recovery_paths() -> None:
    env = {
        "DB_MONITOR_POSTGRES_DSN": default_postgres_test_dsn(),
        "DB_MONITOR_REDIS_URL": "redis://127.0.0.1:6379/0",
    }
    with compose_services("postgres", "redis"):
        run(
            ["uv", "run", "pytest", "gates/recovery/test_recovery_paths_live.py"],
            env_overrides=env,
        )


def handle_schema_bootstrap() -> None:
    env = {
        "DB_MONITOR_RUNTIME": "postgres",
        "DB_MONITOR_POSTGRES_DSN": default_postgres_test_dsn(),
        "PYTHONPATH": str((REPO_ROOT / "apps" / "api" / "src").resolve()),
        **default_clickhouse_env(),
    }
    with compose_services("postgres", "clickhouse"):
        run(
            ["uv", "run", "pytest", "gates/schema/test_schema_bootstrap_live.py"],
            env_overrides=env,
        )


def handle_web_smoke() -> None:
    api_url = f"http://localhost:{API_PORT}"
    web_url = f"http://localhost:{WEB_PORT}"
    api_out = REPO_ROOT / ".tmp-smoke-api.out.log"
    api_err = REPO_ROOT / ".tmp-smoke-api.err.log"
    web_out = REPO_ROOT / ".tmp-smoke-web.out.log"
    web_err = REPO_ROOT / ".tmp-smoke-web.err.log"

    for path in (api_out, api_err, web_out, web_err):
        path.unlink(missing_ok=True)

    api_process: subprocess.Popen[str] | None = None
    web_process: subprocess.Popen[str] | None = None

    try:
        run(["pnpm", "--filter", "web", "build"])
        run(["pnpm", "exec", "playwright", "install", "chromium"])
        with started_process(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "db_monitor_api.smoke_main:app",
                "--app-dir",
                "apps/api/src",
                "--host",
                "127.0.0.1",
                "--port",
                str(API_PORT),
            ],
            stdout_path=api_out,
            stderr_path=api_err,
        ) as api_process:
            wait_http_200(f"{api_url}/openapi.json", "Smoke API")

            with started_process(
                [
                    "pnpm",
                    "--filter",
                    "web",
                    "exec",
                    "next",
                    "start",
                    "--hostname",
                    "127.0.0.1",
                    "--port",
                    str(WEB_PORT),
                ],
                env_overrides={"DB_MONITOR_API_BASE_URL": api_url},
                stdout_path=web_out,
                stderr_path=web_err,
            ) as web_process:
                wait_http_200(f"{web_url}/login", "Smoke Web")
                run(
                    ["pnpm", "exec", "playwright", "test", "-c", "playwright.smoke.config.ts"],
                    env_overrides={"PLAYWRIGHT_BASE_URL": web_url},
                )
    except Exception:
        print("--- Smoke API stderr ---", flush=True)
        show_log_if_present(api_err)
        print("--- Smoke API stdout ---", flush=True)
        show_log_if_present(api_out)
        print("--- Smoke Web stderr ---", flush=True)
        show_log_if_present(web_err)
        print("--- Smoke Web stdout ---", flush=True)
        show_log_if_present(web_out)
        raise
    finally:
        terminate_process(web_process)
        terminate_process(api_process)


def _docker_container_exists(container_name: str) -> bool:
    completed = subprocess.run(
        ["docker", "container", "inspect", container_name],
        capture_output=True,
        cwd=REPO_ROOT,
        text=True,
    )
    return completed.returncode == 0


def _docker_container_running(container_name: str) -> bool:
    running = capture(
        ["docker", "container", "inspect", "-f", "{{.State.Running}}", container_name]
    )
    return running.lower() == "true"


def _compose_container_id(service: str) -> str:
    container_id = capture(["docker", "compose", "ps", "-q", service])
    if container_id == "":
        raise RuntimeError(f"Compose service {service} did not produce a container id.")
    return container_id


HANDLERS = {
    "dev-down.ps1": handle_dev_down,
    "dev-up.ps1": handle_dev_up,
    "test-alert-maturity-signoff.ps1": handle_alert_maturity_signoff,
    "test-alert-pipeline-postgres.ps1": handle_alert_pipeline_postgres,
    "test-analytics-clickhouse.ps1": handle_analytics_clickhouse,
    "test-api-runtime-readiness.ps1": handle_api_runtime_readiness,
    "test-background-processes.ps1": handle_background_processes,
    "test-control-plane-oracle.ps1": handle_control_plane_oracle,
    "test-control-plane-postgres.ps1": handle_control_plane_postgres,
    "test-hardening-signoff.ps1": handle_hardening_signoff,
    "test-metrics-pipeline-live.ps1": handle_metrics_pipeline_live,
    "test-recovery-paths.ps1": handle_recovery_paths,
    "test-schema-bootstrap.ps1": handle_schema_bootstrap,
    "test-web-smoke.ps1": handle_web_smoke,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-platform repo-local runner for the workspace PowerShell task scripts."
    )
    parser.add_argument("-ExecutionPolicy", nargs="?", default=None)
    parser.add_argument("-File", dest="file", required=True)
    args = parser.parse_args()

    script_name = Path(args.file).name
    handler = HANDLERS.get(script_name)
    if handler is None:
        supported = ", ".join(sorted(HANDLERS))
        raise SystemExit(
            f"Unsupported PowerShell shim target: {script_name}. Supported: {supported}"
        )

    handler()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
