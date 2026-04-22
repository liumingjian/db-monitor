# Operator Rollback Checklist

- 一旦任一 release / launch gate 失败，立即停止继续发布
- 记录失败命令和失败时间
- 记录失败时缺失的环境变量、端口冲突或依赖状态
- 保存 `.tmp-smoke-api.err.log`、`.tmp-smoke-web.err.log` 等现场日志
- 执行 `pnpm dev:deps:down`
- 确认 `5432`、`6379`、`8123`、`3306`、`38100`、`38101` 已释放
- 若本轮包含 Oracle，额外确认 `15211` 已释放或 `oracle-xe-local` 状态可解释
- 明确本次回滚触发条件，再决定是否重新执行发布步骤
