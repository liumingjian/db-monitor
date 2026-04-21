# Progress

## Summary

- Task shape: single-full
- Goal: 为 Oracle 建立最小资产接入与校验路径

## Recovery

- 任务: 已完成 Oracle onboarding baseline
- 形态: single-full
- 进度: 3/3
- 当前: 已完成最终验证
- 文件: `.codex-tasks/20260420-multi-engine-validation-epic/tasks/20260420-03-oracle-onboarding-baseline/TODO.csv`
- 下一步: 将父 epic 切换到子任务 `#4 Generalize scheduler and pipeline dispatch for engine-aware jobs`

## Notes

- 前置依赖 `#2` 已完成，因此现在可以在真实 `engine-aware` 资产契约上增加 Oracle baseline，而不是继续堆叠 mysql-only 别名
- Oracle baseline 契约已冻结：
  - `connection.database` 对 Oracle 表示 DSN/service name
  - 调用方必须显式提供 Oracle listener port，本轮不引入 engine-specific 默认端口推断
  - 本任务不承诺 Oracle metrics/analytics parity，只验证资产创建、连接校验以及显式能力边界
- 已实现的控制输入：
  - 新增 Oracle validator seam，并通过 runtime 注入打通 `AssetService`
  - 控制面 create/validate 测试覆盖 Oracle in-memory 与 Postgres 路径
  - OpenAPI 说明增加 Oracle DSN/service name 与显式端口语义
- 本轮验证证据：
  - `uv run pytest tests/api/assets tests/integration/control_plane`
  - `pnpm openapi:check`
- 该任务完成时曾显式记录 live Oracle gate 仍未闭环；后续 `.codex-tasks/20260420-oracle-live-gate/` 已补齐：
  - `oracledb` 运行依赖
  - `PythonOracleConnectionValidator` 的 docker `sqlplus` fallback（用于本地 11g XE）
  - `pnpm test:control-plane:oracle` 真实门禁
