# Progress

## Summary

- Task shape: single-full
- Goal: 在 analytics / API contract 中实现批准范围内的 mixed-engine overview parity

## Recovery

- 任务: child `#3` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 无。analytics/API parity 与 contract signoff 已完成
- 文件: `.codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-03-overview-parity-api/TODO.csv`
- 下一步: 把 backend parity 结果回灌到 parent epic，并为 child `#4/#5` 提供稳定 contract

## Control Contract

- Primary Setpoint: 让 overview payload 停止依赖 MySQL-only tuples，并在 analytics/API 层显式承载批准范围内的 mixed-engine parity
- Acceptance: overview cards/charts、coverage、instance snapshot、OpenAPI snapshot 与 typed client 同步收敛；focused backend gates 全绿
- Guardrails: 不回退 MySQL overview baseline；不伪造跨引擎等价字段；不把 API parity 偷换成 full BI/reporting scope
- Sampling Plan: 先改 analytics service 与 domain contract，再同步 router/OpenAPI/client，最后补 focused tests

## Latest Evidence

- analytics contract 已收口：
  - `apps/api/src/db_monitor_api/analytics/service.py` 现在对 MySQL + Oracle 同时聚合 overview cards、charts 与 instance metrics
  - `apps/api/src/db_monitor_api/analytics/domain.py` / `router.py` 把 overview instance snapshot 从固定 `qps` / `threads_*` / `replication_lag_seconds` 切到通用 `metrics[]`
  - `overview_metric_engines` 与 `overview_instance_metric_engines` 已按 present engines 暴露 `mysql` + `oracle`
- shared contract 已收口：
  - `packages/api-client/src/index.ts` 已同步到新的 overview contract，并把 `API_CONTRACT_VERSION` 提升到 `0.10.0`
  - `contracts/openapi.snapshot.json` 已在 `pnpm openapi:update` 后回写并通过 `pnpm openapi:check`
- focused backend tests 已收口：
  - `tests/api/analytics/test_analytics_contract.py`
  - `tests/api/analytics/test_analytics_overview.py`
  - `tests/integration/analytics_queries/test_analytics_queries.py`

## Validation

- `uv run pytest tests/api/analytics tests/integration/analytics_queries -q`
- `pnpm openapi:update`
- `pnpm openapi:check`
- `pnpm exec tsc --noEmit -p packages/api-client/tsconfig.json`

## Notes

- 本 child 只交付批准范围内的 mixed-engine overview parity，不扩展到更深 Oracle analytics / BI 面
