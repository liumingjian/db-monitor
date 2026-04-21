# Operator Alert Maturity Checklist

- 确认 `docker`、`pnpm`、`.venv` 可用
- 确认本地端口 `5432`、`6379`、`38100`、`38101` 未冲突
- 执行 `pnpm test:alert-maturity:signoff`
- 若失败，停止本次 signoff，记录失败命令与时间戳
- 若失败点是 live gate，单独重跑 `pnpm test:alert-pipeline:postgres` 与 `pnpm test:recovery-paths`
