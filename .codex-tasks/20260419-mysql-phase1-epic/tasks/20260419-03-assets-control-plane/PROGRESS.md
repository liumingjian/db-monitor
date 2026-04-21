# Progress

## Summary

- Task shape: single-full
- Goal: 实现 MySQL 资产接入、连接校验和控制面核心 API

## Recovery

- 任务: 建立控制面资产与设置模型，并对外提供稳定 API
- 形态: single-full
- 进度: 4/4
- 当前: 已完成，资产接入、连接校验、列表详情和系统设置 API 已通过自动化验证
- 文件: `.codex-tasks/20260419-mysql-phase1-epic/tasks/20260419-03-assets-control-plane/TODO.csv`
- 下一步: 将父 epic 的子任务 `#3` 标记为 `DONE`，再推进 `#4 metrics-pipeline`

## Notes

- 上游依赖: 子任务 `#1`、`#2`
- 下游影响: 子任务 `#4`、`#5`、`#6`、`#8`、`#9`
- 该任务是 phase-one 控制面真相来源，不应复用旧 Lepus 表契约

## Verification

- `uv run pytest tests/api/assets -k contract`
- `uv run pytest tests/api/assets -k onboarding`
- `uv run pytest tests/integration/control_plane -k settings`
- `uv run pytest tests/api/assets tests/integration/control_plane`
- `powershell -ExecutionPolicy Bypass -File ./scripts/test-control-plane-postgres.ps1`
- `uv run pytest tests/api/auth tests/api/rbac`
- `uv run ruff check .`
- `uv run mypy apps tests`
- `pnpm lint`
- `pnpm typecheck`

## Approximation Validity

- 自动化验证使用显式注入的本地 runtime，目的是稳定 API 语义、RBAC 边界和审计行为
- `PostgresControlPlaneRepository` 与 `build_postgres_runtime()` 已落盘，真实 PostgreSQL 存储边界不再停留在口头约定
- 已补 `live PostgreSQL gate`，通过真实 `postgres` 容器验证 `create/list/detail/settings` 持久化链路
