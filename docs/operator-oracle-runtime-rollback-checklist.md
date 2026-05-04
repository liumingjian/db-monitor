# Operator Oracle Runtime Rollback Checklist

- 任何一个 runtime gate 失败后，立即停止继续 signoff
- 先执行 `docker compose stop postgres oracle-xe`
- 若本轮显式启动了 `oracle-xe-local`，记录其状态并按本地约定恢复
- 保留最近一次 doctor 输出与 Oracle 容器日志
- 记录最后一个失败命令和失败时间
- 在未定位失败前，不要跳过 `pnpm test:oracle-runtime:doctor` 或 `pnpm test:control-plane:oracle`
