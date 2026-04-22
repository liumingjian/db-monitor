# Operator Docker Target Baseline

## Scope

这份 runbook 定义一个贴近内部投产目标的 Docker target-environment 路径。
它不是新的发布流程，也不替代已有 `pnpm test:launch-readiness:signoff`，而是把
`api + web + scheduler + worker + foundation dependencies` 真实放进 Docker
里，并用同一套 repo-local smoke 验证主链是否打通。

## Preconditions

- 已通过 `pnpm test:launch-readiness:signoff`
- 当前机器可以运行 `docker compose`
- 当前仓库可执行 `pnpm exec playwright`
- 本机端口 `39100`、`39101` 未被占用

## Stack Shape

| 服务 | 角色 | 说明 |
| --- | --- | --- |
| `postgres` | 控制面状态 | 复用 root compose 基础依赖 |
| `clickhouse` | 指标存储 | 复用 root compose 基础依赖 |
| `redis` | 队列 | 复用 root compose 基础依赖 |
| `mysql-target` | MySQL probe | 供 target stack 做真实实例校验与指标采集，避免复用 root compose 中已失效的旧 MySQL 启动参数 |
| `oracle-xe` | Oracle baseline | 若本机没有可复用的 `oracle-xe-local`，才由 compose profile 拉起；Oracle 真值仍以 root Oracle signoff 为准 |
| `bootstrap-runtime` | 一次性 schema bootstrap | 显式执行，不隐式塞进应用启动 |
| `seed-target-runtime` | 一次性数据 seed | 生成 deterministic smoke 数据集 |
| `api` | FastAPI runtime | 运行 `db_monitor_api.main:app` |
| `scheduler` | 调度进程 | 运行 scheduler loop |
| `worker-mysql` | 指标 worker | 运行 worker loop |
| `web` | Next.js runtime | 指向容器内 `api` 服务 |

## Host Ports

| 端口 | 服务 | 用途 |
| --- | --- | --- |
| `39100` | `api` | Docker target API |
| `39101` | `web` | Docker target web |

## Canonical Commands

1. 启动并保持 Docker target stack 运行：
   - `pnpm docker:target:up`
2. 在运行中的 stack 上执行完整 signoff：
   - `pnpm test:docker-target:signoff`
3. 结束 rehearsal 并清理容器：
   - `pnpm docker:target:down`

## Verification Contract

- `pnpm docker:target:up` 必须完成：
  - foundation dependencies 拉起
  - schema bootstrap
  - deterministic seed
  - `api` 与 `web` 的健康检查通过
- `pnpm test:docker-target:signoff` 必须额外完成：
  - Playwright 登录与主链 smoke
  - `web -> api -> postgres/clickhouse/mysql` 的主流程验证
- Oracle 覆盖边界：
  - Docker target path 不在容器内重复实现 Oracle live probe
  - Oracle runtime 真值继续由 `pnpm test:oracle-runtime:signoff` 提供
- 若任何一步失败，预期行为是显式失败并输出 Docker logs，而不是静默跳过 bootstrap、seed 或 smoke

## Failure Triage

若 `pnpm test:docker-target:signoff` 失败，优先查看：

- `docker compose -f compose.yaml -f compose.target.yaml --profile oracle ps`
- `docker compose -f compose.yaml -f compose.target.yaml --profile oracle logs --tail 80 api`
- `docker compose -f compose.yaml -f compose.target.yaml --profile oracle logs --tail 80 web`
- `docker compose -f compose.yaml -f compose.target.yaml --profile oracle logs --tail 80 bootstrap-runtime`
- `docker compose -f compose.yaml -f compose.target.yaml --profile oracle logs --tail 80 seed-target-runtime`
- `docker compose -f compose.yaml -f compose.target.yaml --profile oracle logs --tail 80 mysql-target`

## Boundaries

- 当前只覆盖 internal single-environment Docker rehearsal
- 不包含 Kubernetes、Terraform、multi-node HA、persistent secret manager wiring
- 不把 Oracle live gate 伪装成容器内 smoke；Oracle 仍沿用 root runtime baseline
- 若真实问题已经变成容量、故障域、备份恢复或 RTO/RPO，不在本 runbook 内继续扩 scope
