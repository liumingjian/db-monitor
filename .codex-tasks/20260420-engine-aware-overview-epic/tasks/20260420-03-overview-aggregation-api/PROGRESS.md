# Progress

## Summary

- Task shape: single-full
- Goal: 实现 mixed-engine overview aggregation 与 analytics API

## Recovery

- 任务: child #3 已完成，mixed-engine overview aggregation 与 analytics API baseline 已落盘并通过门禁
- 形态: single-full
- 进度: 3/3
- 当前: 所有步骤已完成，等待 child `#4` 接手 web overview surface 与 fleet messaging
- 文件: `.codex-tasks/20260420-engine-aware-overview-epic/tasks/20260420-03-overview-aggregation-api/TODO.csv`
- 下一步: 让 web overview surface 消费新的 `summary.engines` 与 `coverage` 字段，停止把 mixed-engine fleet 继续写成 MySQL-first copy

## Delivery

- overview summary 现在按引擎输出 `healthy / unhealthy / total` 聚合，mixed-engine fleet 不再只靠全局总数表达状态
- overview payload 现在新增显式 `coverage`，说明当前哪些引擎具备 detail analytics、fleet health、overview instance metrics、overview cards/charts 语义
- 现有 MySQL cards/charts 与 per-instance numeric fields 继续保持兼容，没有在本 child 中被强行重写成伪装 parity 的“通用指标”

## Evidence

- 后端实现: `apps/api/src/db_monitor_api/analytics/domain.py` / `router.py` / `service.py`
- 契约与集成: `tests/api/analytics/test_analytics_overview.py` / `tests/api/analytics/test_analytics_contract.py` / `tests/integration/analytics_queries/test_analytics_queries.py`
- 客户端类型: `packages/api-client/src/index.ts`
- 预览夹具: `apps/web/src/monitoring-preview.ts`

## Validation

- `uv run pytest tests/api/analytics tests/integration/analytics_queries`
- `pnpm --filter web typecheck`
- `pnpm openapi:check`
