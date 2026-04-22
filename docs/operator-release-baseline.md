# Operator Release Baseline

## Scope

这份 runbook 定义 Epic 13 `Production Launch Readiness and Deployment Baseline`
的内部投产基线。
目标不是建设完整 CI/CD，而是把当前仓库面向 `internal single-environment`
production launch 的前置检查、signoff、回滚和验收入口固化为显式步骤。

## Target Environment

| 字段 | 当前批准边界 |
| --- | --- |
| 目标环境 | 内部单环境 production |
| 租户边界 | 单租户 |
| 操作模式 | 受控 operator + repo-local signoff |
| 非目标 | 完整 CI/CD、Kubernetes、Terraform、多环境 promotion、HA/DR |

## Environment Contract

核心 runtime 与发布门禁依赖以下环境契约：

| 类别 | 变量 | 要求 |
| --- | --- | --- |
| API runtime | `DB_MONITOR_RUNTIME` | 固定为 `postgres` |
| API runtime | `DB_MONITOR_POSTGRES_DSN` | 必须可连接控制面 PostgreSQL |
| Metrics pipeline | `DB_MONITOR_REDIS_URL` | 必须可连接调度/worker 队列 |
| Analytics | `DB_MONITOR_CLICKHOUSE_DATABASE` | 必须指向可写 ClickHouse database |
| Analytics | `DB_MONITOR_CLICKHOUSE_ENDPOINT` | 必须指向可访问 ClickHouse endpoint |
| Analytics | `DB_MONITOR_CLICKHOUSE_USERNAME` | 必须提供可用账号 |
| Analytics | `DB_MONITOR_CLICKHOUSE_PASSWORD` | 必须通过环境注入，不得写入源码 |
| Web smoke | `DB_MONITOR_API_BASE_URL` | 由 repo-local smoke runner 注入 |
| Oracle parity | `DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER` | Oracle signoff 路径需要 |
| Oracle parity | `DB_MONITOR_ORACLE_TEST_HOST` / `PORT` / `SERVICE` / `USERNAME` / `PASSWORD` | Oracle signoff 路径需要 |

更完整的变量、端口和 secret 约束见：

- [operator-launch-environment-baseline.md](./operator-launch-environment-baseline.md)

## Preconditions

- 已安装 `docker`
- 已安装 `pnpm`
- 已准备仓库根目录下的 `.venv`
- 当前根级 `pnpm` 命令已适配 macOS，本地无需系统 PowerShell
- `pnpm smoke` 使用 Playwright 自管 `chromium`，本地无需安装 Microsoft Edge
- 本地端口 `38100`、`38101`、`5432`、`6379`、`8123`、`3306` 未被其他进程占用
- 若当前上线窗口包含 Oracle 能力，额外确认本地端口 `15211` 可用，且 Oracle
  runtime baseline 已准备好

## Canonical Flow

1. 准备本地依赖与端口：
   - `pnpm dev:deps:up`
2. 先执行仓库根级 hardening signoff：
   - `pnpm test:hardening:signoff`
3. 当前 approved launch contract 仍包含 Oracle runtime baseline：
   - `pnpm test:oracle-runtime:signoff`
4. 在以上门禁全部通过后，执行最终 launch signoff：
   - `pnpm test:launch-readiness:signoff`
5. 若本次是目标环境试运行，再按：
   - [operator-prelaunch-rehearsal-runbook.md](./operator-prelaunch-rehearsal-runbook.md)
6. 若需要先在本机 Docker 中打通完整 target stack，再按：
   - [operator-docker-target-baseline.md](./operator-docker-target-baseline.md)

## Deployment Baseline

1. 依赖准备：
   - 先确认 `.venv`、`docker`、`pnpm` 可用
   - 再确认环境变量与 secrets 已按环境合同注入，而不是写入源码
2. 基础依赖拉起：
   - `pnpm dev:deps:up`
3. 根级门禁收口：
   - `pnpm test:hardening:signoff`
4. Oracle 运行时收口：
   - `pnpm test:oracle-runtime:signoff`
5. 最终 launch signoff：
   - `pnpm test:launch-readiness:signoff`
6. 目标环境 rehearsal：
   - [operator-prelaunch-rehearsal-runbook.md](./operator-prelaunch-rehearsal-runbook.md)
7. Docker target rehearsal：
   - [operator-docker-target-baseline.md](./operator-docker-target-baseline.md)

## Acceptance Signals

| 命令 | 证明什么 | 失败后默认动作 |
| --- | --- | --- |
| `pnpm test:hardening:signoff` | lint/typecheck/python checks/unit tests/live gates/smoke 已同时通过 | 立即停止本次发布 |
| `pnpm test:oracle-runtime:signoff` | Oracle runtime/live gate 与 rollback baseline 仍成立 | 立即停止本次发布 |
| `pnpm test:launch-readiness:signoff` | docs/scripts/tests/signoff contract 已与当前 repo 对齐 | 立即停止本次发布 |
| `git diff --check` | 当前变更没有残留 whitespace / patch hygiene 问题 | 先修复 diff hygiene 再继续 |

## Verify Procedure

1. 执行根级 smoke：
   - `pnpm smoke`
2. 如 smoke 失败，先查看：
   - `.tmp-smoke-api.err.log`
   - `.tmp-smoke-api.out.log`
   - `.tmp-smoke-web.err.log`
   - `.tmp-smoke-web.out.log`
3. 如需进一步确认运行时硬化 gates，按顺序执行：
   - `pnpm test:api:readiness`
   - `pnpm test:background-processes`
   - `pnpm test:schema:bootstrap`
   - `pnpm test:recovery-paths`
4. 如需做最终 launch 合同确认，执行：
   - `pnpm test:launch-readiness:signoff`

## Rollback Trigger

出现以下任一信号，默认停止继续发布并进入回滚：

- `pnpm test:hardening:signoff` 失败
- `pnpm test:launch-readiness:signoff` 失败
- `pnpm smoke` 失败
- `pnpm test:api:readiness` 失败
- `pnpm test:background-processes` 失败
- `pnpm test:schema:bootstrap` 失败
- `pnpm test:recovery-paths` 失败
- Docker 依赖无法稳定拉起，或本地端口冲突无法消除
- 当前环境合同缺项，导致 PostgreSQL / Redis / ClickHouse / Oracle 任一依赖无法满足

## Rollback Procedure

1. 停止本地依赖：
   - `pnpm dev:deps:down`
2. 清理残留 smoke 进程日志并确认端口释放。
3. 记录最后一个失败 gate、错误日志路径、当前环境合同缺项和当前运行命令，再重新开始下一次发布尝试。

## Checklists

- Release checklist: [operator-release-checklist.md](./operator-release-checklist.md)
- Rollback checklist: [operator-rollback-checklist.md](./operator-rollback-checklist.md)
- Environment baseline: [operator-launch-environment-baseline.md](./operator-launch-environment-baseline.md)
- Acceptance checklist: [operator-launch-acceptance-checklist.md](./operator-launch-acceptance-checklist.md)
- Prelaunch rehearsal: [operator-prelaunch-rehearsal-runbook.md](./operator-prelaunch-rehearsal-runbook.md)
- Evidence template: [operator-prelaunch-evidence-template.md](./operator-prelaunch-evidence-template.md)
- Docker target baseline: [operator-docker-target-baseline.md](./operator-docker-target-baseline.md)
