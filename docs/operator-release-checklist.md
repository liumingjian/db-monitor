# Operator Release Checklist

- 确认 `docker`、`pnpm`、`.venv` 可用
- 确认 `pnpm dev:deps:up` 成功
- 确认 `pnpm test:schema:bootstrap` 成功
- 确认 `pnpm test:api:readiness` 成功
- 确认 `pnpm test:background-processes` 成功
- 确认 `pnpm test:recovery-paths` 成功
- 确认 `pnpm smoke` 成功
- 记录当前通过的命令和时间戳
