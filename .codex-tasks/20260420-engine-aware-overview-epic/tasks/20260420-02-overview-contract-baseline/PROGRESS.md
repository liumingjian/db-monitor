# Progress

## Summary

- Task shape: single-full
- Goal: 冻结 engine-aware overview contract baseline

## Recovery

- 任务: child #2 已完成，engine-aware overview contract baseline 已冻结为一个最小且真实的 mixed-engine 边界
- 形态: single-full
- 进度: 3/3
- 当前: 所有步骤已完成，等待后续 child `#3` 接手 mixed-engine overview aggregation 与 analytics API 深化
- 文件: `.codex-tasks/20260420-engine-aware-overview-epic/tasks/20260420-02-overview-contract-baseline/TODO.csv`
- 下一步: 进入 child `#3`，把 fleet overview cards/charts 与 mixed-engine diagnostics 从隐式 MySQL 聚合推进到诚实可用的 engine-aware API 行为

## Contract Freeze

- engine-aware overview baseline 现在明确允许 mixed-engine fleet 在 `instances[]` 中暴露 `environment`、`engine`、`instance_id`、`labels`、`name`、`status` 与现有 per-instance numeric fields
- Oracle instance 已可在 overview instance metadata 中真实出现，不再被 MySQL-only instance contract 隐藏
- fleet summary 继续保持跨引擎聚合语义，只表达实例总数与健康分布，不假装提供完整的 per-engine parity
- fleet cards/charts 在本 child 中仍保持 MySQL-shaped metric names，这是显式非目标，后续 child 必须继续处理
- 对于当前 overview contract 中尚未得到 Oracle parity 的 per-instance numeric fields，Oracle instance 允许返回 `0` 作为诚实的占位边界，而不是伪造等价指标

## Evidence

- 代码: `apps/api/src/db_monitor_api/analytics/domain.py` / `router.py` / `service.py` 已把 `engine` 维度贯通到 overview instance snapshot 与 API response
- 测试: `tests/api/analytics/test_analytics_overview.py` 新增 mixed-engine snapshot 用例；`tests/api/analytics/test_analytics_contract.py` 新增 mixed-engine overview contract 用例
- 集成: `tests/integration/analytics_queries/test_analytics_queries.py` 已补 overview instance `engine` 断言
- 客户端: `packages/api-client/src/index.ts` 与 `apps/web/src/monitoring-preview.ts` 已同步最小类型面，`pnpm --filter web typecheck` 通过
- OpenAPI: `contracts/openapi.snapshot.json` 已同步，`pnpm openapi:check` 通过

## Validation

- `uv run pytest tests/api/analytics/test_analytics_overview.py tests/api/analytics/test_analytics_contract.py`
- `uv run pytest tests/integration/analytics_queries/test_analytics_queries.py`
- `pnpm --filter web typecheck`
- `pnpm openapi:check`
