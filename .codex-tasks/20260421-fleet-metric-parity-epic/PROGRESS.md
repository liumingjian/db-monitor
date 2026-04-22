# Progress

## Summary

- Task shape: epic
- Goal: 用一轮有边界的 parity epic，把 mixed-engine fleet overview 从 baseline-only 推进到诚实、可验证的 metric parity

## Recovery

- 任务: Epic 11 已完成
- 形态: epic
- 进度: 6/6
- 当前: 无 active child；mixed-engine fleet parity signoff 与 Oracle live coverage 已完成
- 文件: `.codex-tasks/20260421-fleet-metric-parity-epic/SUBTASKS.csv`
- 下一步: 无。若继续推进，先做 post-Epic-11 close-out review，再决定是否激活后续 runtime-oriented epic

## Control Contract

- Primary Setpoint: mixed-engine fleet overview 的 cards、charts、coverage boundary 和 signal leaders 不再显式停留在 `mysql-only` 假设
- Acceptance: 新 epic truth artifacts 与所有 child skeleton 已落盘；active child 能持续关闭 mixed-engine parity gap；后续 child 仍可从磁盘恢复
- Guardrails: 不回退 MySQL overview 与 Oracle detail baseline；不把 parity 扩成 full BI 或 runtime hardening；不在 signal leaders 尚未支持时提前宣称 full parity
- Sampling Plan: 先做 contract baseline，再做 analytics API 与 web surface，再收敛 diagnostics / leaders，最后用 signoff 收口
- Constraints: 只有 `SUBTASKS.csv` 中列出的 child 能进入实现；未进入 `IN_PROGRESS` 的 child 不允许提前写产品代码

## Latest Evidence

- child `#2` 已冻结 parity baseline：
  - Oracle fleet metric family 收敛到 `oracle_sessions_total`、`oracle_sessions_active`、`oracle_session_waits`、`oracle_user_calls_total`、`oracle_physical_reads_total`
  - overview instance contract 已批准切换到通用 `metrics[]`，不再伪造跨引擎同名字段
  - signal leaders 已显式限定为 engine-specific semantics，而不是假统一单位
- child `#3` 已关闭 analytics / API parity gap：
  - `apps/api/src/db_monitor_api/analytics/service.py` 现在对 MySQL + Oracle 同时聚合 overview cards / charts / instance metrics
  - `apps/api/src/db_monitor_api/analytics/domain.py`、`router.py` 与 `packages/api-client/src/index.ts` 已同步到 `metrics[]` contract
  - `contracts/openapi.snapshot.json` 与 analytics/integration tests 已更新并通过
- child `#4` 与 child `#5` 已关闭 web parity gap：
  - `apps/web/src/monitoring-ui.ts` 现在对 full mixed-engine parity、partial coverage 和 single-engine coverage 做诚实区分
  - diagnostics、capacity insights 与 signal leaders 已切到 engine-aware semantics
  - `apps/web/app/instances/page.tsx` 与 preview fixtures 已停止把 Oracle fleet metrics 固定成 baseline-only 叙事
- child `#6` 已完成 repo-root parity signoff：
  - `pnpm openapi:check`
  - `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/api/analytics tests/integration/analytics_queries tests/integration/metrics_pipeline -q`
  - `pnpm --filter web test`
  - `pnpm --filter web typecheck`
  - `pnpm --filter web build`
  - `pnpm smoke`
  - `pnpm test:control-plane:oracle`
  - `pnpm exec tsc --noEmit -p packages/api-client/tsconfig.json`
  - `git diff --check`
- build/smoke 的环境性阻塞也已收口：
  - `apps/web/app/layout.tsx` 已移除 `next/font/google`
  - `apps/web/package.json` 与 `apps/web/app/globals.css` 现在使用本地 Fontsource 依赖，避免构建阶段访问 Google Fonts

## Notes

- 这是 roadmap extension 之后的新产品扩展 epic，不再属于原始 PRD closeout
- `Epic 12` 仍保留为 runtime-oriented future epic，但本轮不会提前激活
