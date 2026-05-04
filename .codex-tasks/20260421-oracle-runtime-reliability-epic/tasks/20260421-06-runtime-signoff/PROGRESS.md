# Progress

## Summary

- Task shape: single-full
- Goal: 用 runtime contract、doctor 与 live gates 为 Epic 12 收口

## Recovery

- 任务: child `#6` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 无。Oracle runtime signoff 与 Epic 12 closeout 已完成
- 文件: `.codex-tasks/20260421-oracle-runtime-reliability-epic/tasks/20260421-06-runtime-signoff/TODO.csv`
- 下一步: 无。Epic 12 可以正式关闭

## Control Contract

- Primary Setpoint: 用同一 signoff window 证明 Oracle runtime doctor/docs/tests/live gate 已真实闭环，而不是局部绿
- Acceptance: contract tests、doctor、Postgres control-plane gate 与 Oracle live gate 同时通过；parent truth 与 roadmap 同步完成
- Guardrails: 不用历史 live baseline 冒充本轮结果；不跳过 doctor 直接跑 live gate；不靠 silent fallback 让 signoff 假绿

## Latest Evidence

- runtime contract / doctor 已通过：
  - `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/api/control_plane/test_oracle_validation.py tests/ops/test_oracle_runtime_baseline.py tests/ops/test_macos_environment_entrypoints.py -q`
  - `pnpm test:oracle-runtime:doctor`
- control-plane live signoff 已通过：
  - `pnpm test:control-plane:postgres`
  - `pnpm test:control-plane:oracle`
- root runtime signoff 已通过：
  - `pnpm test:oracle-runtime:signoff`
  - `git diff --check`

## Notes

- 本 child 明确把 runtime repeatability 当成根级 gate 来处理，而不是把 live gate 继续当作一次性环境幸运
