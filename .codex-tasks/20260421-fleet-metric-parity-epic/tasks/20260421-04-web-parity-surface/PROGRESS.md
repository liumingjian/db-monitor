# Progress

## Summary

- Task shape: single-full
- Goal: 收敛 overview UI 与 capability boundary 到新的 fleet parity baseline

## Recovery

- 任务: child `#4` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 无。overview UI、capability boundary 与 messaging 已收口
- 文件: `.codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-04-web-parity-surface/TODO.csv`
- 下一步: 把稳定的 web parity surface 提供给 child `#5/#6` 做 diagnostics 与 signoff

## Control Contract

- Primary Setpoint: 让 overview UI、preview 和页面 messaging 与新的 mixed-engine overview contract 对齐，而不是继续躲在 baseline-only 文案里
- Acceptance: dashboard model、capability boundary、preview fixtures 与页面 copy 在同一套语义上收敛，web tests/typecheck 全绿
- Guardrails: 不夸大 partial coverage；不把 detail-only 能力描述成 fleet parity；不绕过 backend contract 另造前端字段

## Latest Evidence

- dashboard/model 语义已收口：
  - `apps/web/src/monitoring-ui.ts` 现在对 full mixed-engine parity、partial mixed coverage 和 Oracle-only coverage 做显式区分
  - overview chart title、metric labels 与 capability boundary 已跟随 backend contract 调整
- preview / page messaging 已收口：
  - `apps/web/src/monitoring-preview.ts` 已把 instance snapshot 切到 `metrics[]`
  - `apps/web/app/instances/page.tsx` 现在明确写 Oracle 已贡献 mixed-engine fleet metrics，而不是只停留在 health/detail baseline
- tests 已收口：
  - `apps/web/tests/dashboard.test.ts` 现在覆盖 MySQL-only、mixed-engine partial、mixed-engine full parity 三种场景
  - `apps/web/tests/instances.test.ts` 已同步新的 capability boundary wording

## Validation

- `pnpm --filter web test`
- `pnpm --filter web typecheck`

## Notes

- 本 child 收口的是 honest messaging，不是视觉改版或新的产品范围扩张
