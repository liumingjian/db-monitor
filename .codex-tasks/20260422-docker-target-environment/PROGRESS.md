# Progress

## Summary

- Task shape: single-full
- Goal: 把当前 launch baseline 补成一条真实可运行的 Docker target-environment 路径

## Recovery

- 任务: 已完成
- 形态: single-full
- 进度: 4/4
- 当前: 已关闭；Docker target environment 已落盘并通过全链路 signoff
- 文件: `.codex-tasks/20260422-docker-target-environment/TODO.csv`
- 下一步: operator 可直接按 runbook 在本机 Docker 中复现 target stack，后续只在真实目标环境证据要求更高时再决定是否升级为新的 roadmap 工作

## Control Contract

- Primary Setpoint: 用 Docker 把 `web -> api -> postgres/redis/clickhouse/mysql/oracle` 的 target environment 真实拉起，并给出一条可重复执行的 signoff 命令
- Acceptance:
  - 新增的 compose overlay、Dockerfiles、bootstrap/seed 脚本落盘
  - operator runbook 与 repo entrypoints 更新
  - Docker target signoff 能真实通过
- Guardrails:
  - 不把 schema/bootstrap 隐式塞进主应用启动
  - 不改写已有 `pnpm test:launch-readiness:signoff` 语义
  - 不把当前任务扩成 K8s/HA/CI/CD 设计
- Sampling Plan:
  - 先静态校对 compose 与脚本合同
  - 再做容器实际拉起和健康检查
  - 最后跑浏览器 smoke 证明确实打通产品主链

## Current Gap

- 原始缺口已收口，当前仓库现在具备一条显式的 Docker target path：
  - `compose.target.yaml` 负责编排 app runtime 与 `mysql-target`
  - `Dockerfile.runtime` / `Dockerfile.web` 提供 repo-local 应用镜像
  - `scripts/docker_target_runtime.py` 显式负责 bootstrap 与 deterministic seed
  - `scripts/docker_target_stack.py` 负责 `up / down / signoff` 编排与 smoke
- Oracle 边界也已经显式化：
  - Docker target seed 不再伪装容器内 Oracle live probe
  - Oracle 真值继续委托给根级 `pnpm test:oracle-runtime:signoff`

## Latest Evidence

### Assets

- 新增 Docker target 资产：
  - `compose.target.yaml`
  - `Dockerfile.runtime`
  - `Dockerfile.web`
  - `scripts/docker_target_runtime.py`
  - `scripts/docker_target_stack.py`
  - `scripts/docker-target-up.ps1`
  - `scripts/docker-target-down.ps1`
  - `scripts/test-docker-target-signoff.ps1`
  - `docs/operator-docker-target-baseline.md`
  - `tests/ops/test_docker_target_baseline.py`
- 更新的 repo wiring：
  - `package.json`
  - `scripts/powershell_shim.py`
  - `docs/operator-release-baseline.md`
  - `docs/operator-prelaunch-rehearsal-runbook.md`
  - `tests/ops/test_macos_environment_entrypoints.py`
  - `smoke/phase-one.spec.ts`
  - `apps/web/app/api/login/route.ts`
  - `apps/web/tests/login-route.test.ts`

### Docker Validation

- 静态合同校验：
  - `docker compose -f compose.yaml -f compose.target.yaml --profile oracle config`
  - `python3 -m py_compile scripts/docker_target_runtime.py scripts/docker_target_stack.py`
  - `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/ops/test_docker_target_baseline.py tests/ops/test_release_baseline.py tests/ops/test_macos_environment_entrypoints.py tests/ops/test_prelaunch_rehearsal_packet.py -q`
  - `pnpm --filter web test -- login-route.test.ts`
  - `pnpm exec biome check apps/web/app/api/login/route.ts apps/web/tests/login-route.test.ts smoke/phase-one.spec.ts`
- 真实 Docker 全链路验证：
  - `pnpm test:docker-target:signoff`
  - 结果：`1 passed (2.3s)`，Docker target stack 完整重建、bootstrap、seed、health checks 与 Playwright smoke 全部通过
  - 登录重定向合同 spot check：
    - `curl -i -X POST ... http://127.0.0.1:39101/api/login`
    - `location: /overview`

### Root Cause Notes

- `compose.yaml` 里的旧 MySQL 参数已不适配 MySQL `8.4`，因此 Docker target path 独立引入 `mysql-target`
- Dockerized `web` 登录接口此前会生成 `http://0.0.0.0:3000/overview` 跳转，现已修正为相对 `location: /overview`
- Oracle 11g/XE 容器内 thin-mode probe 不是这条路径的真实最小闭环，因此当前显式委托给 root Oracle signoff，而不是制造假成功

## Next Operator Path

1. 用 `pnpm docker:target:up` 在本机或预演环境拉起完整 Docker target stack。
2. 用 `pnpm test:docker-target:signoff` 做容器化全链路 gate。
3. 结束后执行 `pnpm docker:target:down` 清理容器。
4. 若目标已转为真实内部环境投产，继续按 `docs/operator-prelaunch-rehearsal-runbook.md` 和 `docs/operator-release-baseline.md` 执行 launch gate，而不是在这里继续扩 scope。
