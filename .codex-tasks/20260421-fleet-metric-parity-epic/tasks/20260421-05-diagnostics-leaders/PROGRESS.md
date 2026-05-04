# Progress

## Summary

- Task shape: single-full
- Goal: 收敛 diagnostics、signal leaders 与 preset semantics 到新的 fleet parity baseline

## Recovery

- 任务: child `#5` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 无。diagnostics、leaders 与 build gate 已收口
- 文件: `.codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-05-diagnostics-leaders/TODO.csv`
- 下一步: 进入 child `#6` 做 repo-root signoff

## Control Contract

- Primary Setpoint: 让 capacity insights、signal leaders 与 preset semantics 对 mixed-engine parity 说真话，而不是继续隐含 MySQL-only 结构
- Acceptance: diagnostics/leaders 跟随 approved boundary 收敛，web tests/build 全绿
- Guardrails: 不把不同引擎指标强压成统一单位；不为了 build 绿而加 silent fallback；不新增与本 epic 无关的 UI 范围

## Latest Evidence

- diagnostics 已收口：
  - `apps/web/src/monitoring-ui.ts` 现在按 engine coverage 生成 MySQL / Oracle / mixed-engine capacity insights
  - full mixed-engine parity 会同时呈现 MySQL 与 Oracle insight sets，而不是继续只给 MySQL 解释
- signal leaders 已收口：
  - leader selection 改为从 overview instance `metrics[]` 读取 engine-specific metrics
  - full mixed-engine parity 现在并列呈现 `Highest MySQL QPS`、`Most MySQL Running Threads`、`Worst MySQL Replication Lag`、`Highest Oracle User Calls`、`Most Oracle Active Sessions`、`Highest Oracle Session Waits`
- build gate 也已收口：
  - `apps/web/app/layout.tsx` 不再依赖 `next/font/google`
  - `apps/web/package.json` 与 `apps/web/app/globals.css` 改为本地 Fontsource 字体装载，消除了 `web build` / `pnpm smoke` 的 Google Fonts 网络依赖

## Validation

- `pnpm --filter web test`
- `pnpm --filter web typecheck`
- `pnpm --filter web build`

## Notes

- 本 child 收口的是用户可见语义与构建确定性，不是新的设计系统或 runtime hardening epic
