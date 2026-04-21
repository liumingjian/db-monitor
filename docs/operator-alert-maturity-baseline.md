# Operator Alert Maturity Baseline

## Scope

这份 runbook 固化 Epic 03 `Alert Maturity and On-Call Workflow` 的最终签收入口。
目标是用一个根级命令串起 alert contract、workflow、noise control、delivery、web triage 和 live PostgreSQL evidence。

## Preconditions

- 已安装 `docker`
- 已安装 `pnpm`
- 已准备仓库根目录下的 `.venv`
- 当前根级 `pnpm` 命令已适配 macOS，本地无需系统 PowerShell
- 本地端口 `5432`、`6379`、`38100`、`38101` 未被其他进程占用

## Canonical Signoff

1. 在仓库根目录执行：
   - `pnpm test:alert-maturity:signoff`
2. 该命令会顺序执行：
   - `pnpm openapi:check`
   - `uv run pytest tests/ops/test_alert_maturity_signoff.py tests/alerting_contract tests/alerting_workflow tests/alerting_noise tests/alerting_delivery tests/recovery tests/api/alerting tests/integration/alert_pipeline`
   - `pnpm test`
   - `pnpm typecheck`
   - `pnpm build`
   - `pnpm test:alert-pipeline:postgres`
   - `pnpm test:recovery-paths`

## Failure Isolation

1. 任一命令失败都视为 signoff 未通过，立即停止本次 signoff。
2. 若失败出现在 live gate，先单独重跑：
   - `pnpm test:alert-pipeline:postgres`
   - `pnpm test:recovery-paths`
3. 若失败出现在 API 或 Web 面，优先重跑根入口前的本地验证，而不是手工跳过 gate。

## Checklist

- Alert maturity checklist: [operator-alert-maturity-checklist.md](./operator-alert-maturity-checklist.md)
