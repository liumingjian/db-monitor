# Progress

## Summary

- Task shape: epic
- Goal: 基于 `PRD.md` 和 `RESEARCH.md` 设计可直接执行的 `MySQL-first` phase-one 开发 epic

## Recovery

- 任务: 交付 `MySQL-first` phase-one 开发 epic，并准备好后续逐个子任务执行
- 形态: epic
- 进度: 9/9
- 当前: 所有子任务已完成，epic 进入最终收口态
- 文件: `.codex-tasks/20260419-mysql-phase1-epic/SUBTASKS.csv`
- 下一步: 维持 root release gate 作为 phase-one 的后续回归入口，无需继续拆分子任务

## Notes

- 本 epic 完全来源于已批准的 `PRD.md` 与 `RESEARCH.md`
- 子任务拆分遵循控制面、数据面、前端面和最终门禁分离原则
- 任何子任务都必须以其 `validation_command` 通过为前提才能标记为 `DONE`
- 子任务 `#4` 已通过本地测试、Ruff、Mypy 以及 Redis + ClickHouse live gate，避免“离线通过但状态面失败”的假收敛
- 子任务 `#5` 已通过 API 契约、服务聚合、本地静态门禁以及 ClickHouse read-side live gate，证明 chart-ready 查询路径成立
- 子任务 `#6` 已通过规则/通知本地套件和 PostgreSQL live gate，证明 alert lifecycle 不依赖隐式内存状态
- 子任务 `#7` 已通过 web lint/typecheck/test 和 next build，证明前端壳层与 typed client 真正可编译运行
- 子任务 `#8` 已通过 web test、lint、typecheck、next build 与 smoke route validation，证明 monitoring UI 已切到正式 API 与 server action 主链
- 子任务 `#9` 已通过根级静态检查、全量 pytest、OpenAPI contract check 和 production-mode smoke，形成 phase-one 可复用签收门禁

## Latest Validation

- `pnpm lint`
- `pnpm typecheck`
- `uv run ruff check .`
- `uv run mypy apps`
- `uv run pytest tests/api/auth tests/api/rbac`
- `uv run pytest tests/api/assets tests/integration/control_plane`
- `powershell -ExecutionPolicy Bypass -File ./scripts/test-control-plane-postgres.ps1`
- `uv run pytest tests/scheduler tests/worker_mysql tests/integration/metrics_pipeline`
- `powershell -ExecutionPolicy Bypass -File ./scripts/test-metrics-pipeline-live.ps1`
- `uv run pytest tests/api/analytics tests/integration/analytics_queries`
- `powershell -ExecutionPolicy Bypass -File ./scripts/test-analytics-clickhouse.ps1`
- `uv run pytest tests/rule_engine tests/notifier tests/integration/alert_pipeline`
- `powershell -ExecutionPolicy Bypass -File ./scripts/test-alert-pipeline-postgres.ps1`
- `pnpm --filter web lint`
- `pnpm --filter web typecheck`
- `pnpm --filter web test`
- `pnpm --filter web build`

## Epic Initialization

- **Status**: DONE
- **Date**: 2026-04-19
- **What was done**:
  - 创建 parent `EPIC.md`、`SUBTASKS.csv`、`PROGRESS.md`
  - 按依赖关系拆出 9 个 `single-full` 子任务
  - 为每个子任务预建独立目录与恢复骨架
- **Next step**: 启动子任务 `#1`，建立 monorepo 基础设施和根级工具链
