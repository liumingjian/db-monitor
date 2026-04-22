# Progress

## Summary

- Task shape: single-full
- Goal: 用 targeted gate、web signoff 与 Oracle live coverage 为 Epic 11 收口

## Recovery

- 任务: child `#6` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 无。repo-root signoff、smoke 与 Oracle live coverage 已全部通过
- 文件: `.codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-06-parity-signoff/TODO.csv`
- 下一步: 无。Epic 11 可以正式关闭

## Control Contract

- Primary Setpoint: 用同一 signoff window 证明 Epic 11 的 mixed-engine parity 已经真实闭环，而不是单个 child 各自局部变绿
- Acceptance: backend、OpenAPI、api-client、web、build、smoke 与 Oracle live gate 同时通过；parent truth 与 roadmap 同步完成
- Guardrails: 不用历史 live baseline 冒充本轮结果；不拿单个 focused gate 代替 root signoff；不靠 silent fallback 让 build/smoke 假绿

## Latest Evidence

- backend / contract signoff 已通过：
  - `pnpm openapi:check`
  - `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/api/analytics tests/integration/analytics_queries tests/integration/metrics_pipeline -q`
  - `pnpm exec tsc --noEmit -p packages/api-client/tsconfig.json`
- web / smoke signoff 已通过：
  - `pnpm --filter web test`
  - `pnpm --filter web typecheck`
  - `pnpm --filter web build`
  - `pnpm smoke`
  - `git diff --check`
- Oracle live coverage 已刷新：
  - `pnpm test:control-plane:oracle`
  - `gates/control_plane/test_control_plane_oracle_live.py . [100%]`

## Notes

- 本 child 明确把 Google Fonts 网络依赖当成 signoff 阻塞来处理，而不是把它解释成“环境问题先跳过”
