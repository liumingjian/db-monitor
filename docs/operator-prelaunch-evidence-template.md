# Operator Prelaunch Evidence Template

## Environment Snapshot

| 字段 | 记录 |
| --- | --- |
| 目标环境标识 | `<fill-me>` |
| 执行人 | `<fill-me>` |
| 仓库修订 | `<fill-me>` |
| 执行时间 | `<fill-me>` |
| Oracle baseline 可用 | `<yes/no>` |
| 回滚责任人 | `<fill-me>` |

## Environment Contract Check

| 项目 | 状态 | 备注 |
| --- | --- | --- |
| `DB_MONITOR_RUNTIME` | `<ok/fail>` | `<fill-me>` |
| `DB_MONITOR_POSTGRES_DSN` | `<ok/fail>` | `<fill-me>` |
| `DB_MONITOR_REDIS_URL` | `<ok/fail>` | `<fill-me>` |
| `DB_MONITOR_CLICKHOUSE_DATABASE` | `<ok/fail>` | `<fill-me>` |
| `DB_MONITOR_CLICKHOUSE_ENDPOINT` | `<ok/fail>` | `<fill-me>` |
| `DB_MONITOR_CLICKHOUSE_USERNAME` | `<ok/fail>` | `<fill-me>` |
| `DB_MONITOR_CLICKHOUSE_PASSWORD` | `<ok/fail>` | `<secret source only>` |
| `DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER` | `<ok/fail/not-applicable>` | `<fill-me>` |
| 端口合同 | `<ok/fail>` | `<fill-me>` |

## Gate Results

| 命令 | 结果 | 时间 | 备注 |
| --- | --- | --- | --- |
| `pnpm test:hardening:signoff` | `<pass/fail>` | `<fill-me>` | `<fill-me>` |
| `pnpm test:oracle-runtime:signoff` | `<pass/fail>` | `<fill-me>` | `<fill-me>` |
| `pnpm test:launch-readiness:signoff` | `<pass/fail>` | `<fill-me>` | `<fill-me>` |
| `git diff --check` | `<pass/fail>` | `<fill-me>` | `<fill-me>` |

## Failure Artifacts

| Artifact | 路径 / 摘要 |
| --- | --- |
| 最后一个失败命令 | `<fill-me>` |
| `.tmp-smoke-api.err.log` | `<fill-me>` |
| `.tmp-smoke-web.err.log` | `<fill-me>` |
| docker / runtime diagnostics | `<fill-me>` |
| 缺失变量 / 端口冲突 | `<fill-me>` |

## Decision

| 项目 | 结论 |
| --- | --- |
| Go / No-Go | `<GO / NO-GO / GO WITH FIXES>` |
| 结论原因 | `<fill-me>` |
| 后续动作 | `<继续发布 / 修 launch baseline / 评估 Epic 14>` |
| 审核人 | `<fill-me>` |
