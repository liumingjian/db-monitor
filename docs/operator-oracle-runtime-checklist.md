# Operator Oracle Runtime Checklist

- 确认 `docker`、`pnpm`、`.venv` 可用
- 确认本地端口 `5432`、`15211` 空闲
- 确认需要时可复用 `oracle-xe-local`，或允许 compose 拉起 `oracle-xe`
- 确认 `pnpm test:oracle-runtime:doctor` 成功
- 确认 `pnpm test:control-plane:postgres` 成功
- 确认 `pnpm test:control-plane:oracle` 成功
- 记录当前通过的命令和时间戳
