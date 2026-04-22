from __future__ import annotations

import argparse
import http.client
import os
import shlex
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_URL = "http://127.0.0.1:39100"
WEB_URL = "http://127.0.0.1:39101"
APP_SERVICES = ("api", "scheduler", "worker-mysql", "web")
BUILD_SERVICES = ("bootstrap-runtime", "seed-target-runtime", *APP_SERVICES)
LOG_SERVICES = (
    "bootstrap-runtime",
    "seed-target-runtime",
    "api",
    "scheduler",
    "worker-mysql",
    "web",
    "postgres",
    "clickhouse",
    "redis",
    "mysql-target",
    "oracle-xe",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("up", "down", "signoff"))
    args = parser.parse_args()
    if args.command == "up":
        bring_up_target_stack()
    elif args.command == "down":
        compose("down")
    else:
        bring_up_target_stack()
        run_playwright_smoke()
    return 0


def bring_up_target_stack() -> None:
    oracle_runtime = resolve_oracle_runtime()
    compose_allow_failure("rm", "-sf", *BUILD_SERVICES, env_overrides=oracle_runtime.env_overrides)
    compose("up", "-d", *dependency_services(oracle_runtime), env_overrides=oracle_runtime.env_overrides)
    prepare_oracle_runtime_network(oracle_runtime)
    compose("build", *BUILD_SERVICES, env_overrides=oracle_runtime.env_overrides)
    compose("run", "--rm", "bootstrap-runtime", env_overrides=oracle_runtime.env_overrides)
    compose("run", "--rm", "seed-target-runtime", env_overrides=oracle_runtime.env_overrides)
    compose("up", "-d", *APP_SERVICES, env_overrides=oracle_runtime.env_overrides)
    try:
        wait_http_200(f"{API_URL}/health/ready", "Docker target API")
        wait_http_200(f"{WEB_URL}/login", "Docker target web")
        compose("ps", env_overrides=oracle_runtime.env_overrides)
    except Exception:
        show_target_logs(oracle_runtime.env_overrides)
        raise


def run_playwright_smoke() -> None:
    try:
        run(["pnpm", "exec", "playwright", "install", "chromium"])
        run(
            ["pnpm", "exec", "playwright", "test", "-c", "playwright.smoke.config.ts"],
            env_overrides={
                "DB_MONITOR_SMOKE_INSTANCE_DATABASE": "mysql_probe",
                "DB_MONITOR_SMOKE_INSTANCE_HOST": "mysql-target",
                "DB_MONITOR_SMOKE_INSTANCE_PASSWORD": "db_monitor",
                "DB_MONITOR_SMOKE_INSTANCE_PORT": "3306",
                "DB_MONITOR_SMOKE_INSTANCE_USERNAME": "db_monitor",
                "PLAYWRIGHT_BASE_URL": WEB_URL,
            },
        )
    except Exception:
        show_target_logs()
        raise


def compose(*args: str, env_overrides: dict[str, str] | None = None) -> None:
    run(compose_cmd(*args), env_overrides=env_overrides)


def compose_allow_failure(
    *args: str,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return capture_allow_failure(compose_cmd(*args), env_overrides=env_overrides)


def compose_cmd(*args: str) -> list[str]:
    return [
        "docker",
        "compose",
        "-f",
        "compose.yaml",
        "-f",
        "compose.target.yaml",
        "--profile",
        "oracle",
        *args,
    ]


def run(cmd: list[str], *, env_overrides: dict[str, str] | None = None) -> None:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    print(f"+ {printable(cmd)}", flush=True)
    subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=True)


def capture_allow_failure(
    cmd: list[str],
    *,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    print(f"+ {printable(cmd)}", flush=True)
    return subprocess.run(
        cmd,
        capture_output=True,
        cwd=REPO_ROOT,
        env=env,
        check=False,
        text=True,
    )


def show_target_logs(env_overrides: dict[str, str] | None = None) -> None:
    print("--- Docker target diagnostics ---", flush=True)
    compose_allow_failure("ps", env_overrides=env_overrides)
    for service in LOG_SERVICES:
        completed = compose_allow_failure("logs", "--tail", "80", service, env_overrides=env_overrides)
        if completed.stdout.strip():
            print(f"--- {service} stdout ---", flush=True)
            print(completed.stdout.strip(), flush=True)
        if completed.stderr.strip():
            print(f"--- {service} stderr ---", flush=True)
            print(completed.stderr.strip(), flush=True)


def wait_http_200(url: str, name: str) -> None:
    last_error: Exception | None = None
    for _ in range(90):
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status == 200:
                    return
        except (http.client.RemoteDisconnected, urllib.error.URLError, TimeoutError) as error:
            last_error = error
        time.sleep(1)
    raise RuntimeError(f"{name} did not become healthy at {url}") from last_error


def printable(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


class OracleRuntime:
    def __init__(
        self,
        *,
        env_overrides: dict[str, str],
        legacy_container_name: str | None,
        service_name: str | None,
    ) -> None:
        self.env_overrides = env_overrides
        self.legacy_container_name = legacy_container_name
        self.service_name = service_name


def dependency_services(oracle_runtime: OracleRuntime) -> tuple[str, ...]:
    services = ["postgres", "clickhouse", "redis", "mysql-target"]
    if oracle_runtime.service_name is not None:
        services.append(oracle_runtime.service_name)
    return tuple(services)


def resolve_oracle_runtime() -> OracleRuntime:
    legacy_name = "oracle-xe-local"
    if docker_container_exists(legacy_name):
        if not docker_container_running(legacy_name):
            run(["docker", "start", legacy_name])
        return OracleRuntime(
            env_overrides={
                "DB_MONITOR_TARGET_ORACLE_HOST": legacy_name,
                "DB_MONITOR_TARGET_ORACLE_PASSWORD": "oracle",
                "DB_MONITOR_TARGET_ORACLE_PORT": "1521",
                "DB_MONITOR_TARGET_ORACLE_SERVICE": "XE",
                "DB_MONITOR_TARGET_ORACLE_USERNAME": "system",
            },
            legacy_container_name=legacy_name,
            service_name=None,
        )
    return OracleRuntime(
        env_overrides={},
        legacy_container_name=None,
        service_name="oracle-xe",
    )


def prepare_oracle_runtime_network(oracle_runtime: OracleRuntime) -> None:
    if oracle_runtime.legacy_container_name is None:
        return
    completed = capture_allow_failure(
        [
            "docker",
            "network",
            "connect",
            "db-monitor-dev_default",
            oracle_runtime.legacy_container_name,
        ]
    )
    if completed.returncode == 0:
        return
    stderr = completed.stderr.strip()
    if "already exists" not in stderr:
        raise RuntimeError(stderr or completed.stdout.strip())


def docker_container_exists(container_name: str) -> bool:
    completed = subprocess.run(
        ["docker", "container", "inspect", container_name],
        capture_output=True,
        cwd=REPO_ROOT,
        text=True,
    )
    return completed.returncode == 0


def docker_container_running(container_name: str) -> bool:
    completed = capture_allow_failure(
        ["docker", "container", "inspect", "-f", "{{.State.Running}}", container_name]
    )
    return completed.stdout.strip().lower() == "true"


if __name__ == "__main__":
    raise SystemExit(main())
