# Progress

## Summary

- Task shape: single-full
- Goal: 补齐实例详情页剩余的 TPS 与角色/版本产品语义

## Recovery

- 任务: child `#4` 已完成
- 形态: single-full
- 进度: 4/4
- 当前: 无。实例详情语义与 child 级 signoff 已完成
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/tasks/20260421-04-instance-detail-semantics/TODO.csv`
- 下一步: 回到 parent epic，进入 child `#5` root closeout signoff

## Control Contract

- Primary Setpoint: 用最小 detail payload / UI readout 补齐 PRD 点名的 TPS 与角色/版本显式展示，同时保持现有 analytics coverage boundary 诚实
- Acceptance: analytics detail contract 能显式返回 TPS 与 role/version readout；实例详情页把这些 readout 作为正式产品语义展示出来；web 与 analytics gates 全绿
- Guardrails: 不新增 overview scope；不新增 detail chart family；不把 Oracle 最小趋势支持伪装成全面 parity
- Sampling Plan: 先冻结 contract，再补 analytics/detail payload，最后补 web readout 与 focused signoff

## Latest Evidence

- Analytics/detail payload 已收口：
  - `apps/api/src/db_monitor_pipeline/normalization.py` 与 `collector.py` 现在能从 MySQL raw status 派生 `mysql_transactions_total`
  - `apps/api/src/db_monitor_api/analytics/service.py` 为 MySQL detail cards 新增 `mysql_transactions_per_second`
  - `apps/api/src/db_monitor_api/analytics/router.py` / `domain.py` 现在把 `server_role` 与 `server_version` 带入 detail metadata
- Web readout 已收口：
  - `apps/web/app/instances/[instanceId]/page.tsx` 渲染了显式的 validation / role / version readout
  - `apps/web/src/monitoring-ui.ts` 与 `apps/web/tests/instances.test.ts` 已把新语义纳入稳定模型与测试
- Focused gates 已通过：
  - `uv run pytest tests/api/analytics -q`
  - `uv run pytest tests/integration/metrics_pipeline/test_metrics_pipeline.py -q`
  - `pnpm --filter web test`
  - `pnpm --filter web typecheck`

## Notes

- 这次收口只把 TPS 放进 detail cards，没有新增新的 chart family 或 overview cards
- 角色/版本 readout 依然遵循当前 validation metadata 边界，没有把 detail page 扩成更重的 diagnostics 产品
