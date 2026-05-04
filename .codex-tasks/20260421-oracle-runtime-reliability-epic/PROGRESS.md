# Progress

## Summary

- Task shape: epic
- Goal: 用一轮有边界的 runtime epic，把 Oracle live-gate 从“当前环境能跑”推进到诚实、可重复的运维基线

## Recovery

- 任务: Epic 12 已完成
- 形态: epic
- 进度: 6/6
- 当前: 无 active child；Oracle runtime doctor、signoff 与 operator baseline 已完成
- 文件: `.codex-tasks/20260421-oracle-runtime-reliability-epic/SUBTASKS.csv`
- 下一步: 无。若继续推进，先回到 roadmap close-out / extension 流程

## Control Contract

- Primary Setpoint: Oracle runtime / live-gate 的 doctor、diagnostics、operator baseline 与 signoff 不再停留在环境幸运或口头知识上
- Acceptance: 新 epic truth artifacts 与所有 child skeleton 已落盘；active child 能持续关闭 runtime repeatability gap；后续 child 仍可从磁盘恢复
- Guardrails: 不回退 `pnpm test:control-plane:oracle` 与 `pnpm test:control-plane:postgres`；不把 runtime epic 扩成新产品面；不引入 fake green path
- Sampling Plan: 先做 contract baseline，再做 runtime doctor / diagnostics 与 operator baseline，随后补 contract tests，最后用 signoff 收口
- Constraints: 只有 `SUBTASKS.csv` 中列出的 child 能进入实现；未进入 `IN_PROGRESS` 的 child 不允许提前写产品代码

## Latest Evidence

- child `#2` 已冻结 runtime baseline：
  - runtime doctor、root signoff、diagnostics surface 与 operator assets 的批准边界已写明
  - 本 epic 之外的非目标已经冻结，避免顺手扩成新产品面或新基础设施 phase
- child `#3` 已关闭 runtime doctor / diagnostics gap：
  - `package.json` 现在新增 `test:oracle-runtime:doctor` 与 `test:oracle-runtime:signoff`
  - `scripts/powershell_shim.py` 现在会在 Oracle runtime/live-gate 失败时输出 container health、recent logs 与 sqlplus self-probe 线索
  - `apps/api/src/db_monitor_api/control_plane/oracle_validation.py` 现在对 missing driver 与 `DPY-3010` 给出更明确的 runtime hint
- child `#4` 已关闭 operator baseline gap：
  - `docs/operator-oracle-runtime-baseline.md`
  - `docs/operator-oracle-runtime-checklist.md`
  - `docs/operator-oracle-runtime-rollback-checklist.md`
  - `scripts/test-oracle-runtime-signoff.ps1` / `test-oracle-runtime-doctor.ps1`
- child `#5` 已关闭 runtime contract drift：
  - `tests/ops/test_oracle_runtime_baseline.py`
  - `tests/ops/test_macos_environment_entrypoints.py`
  - `tests/api/control_plane/test_oracle_validation.py`
- child `#6` 已完成 runtime signoff：
  - `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/api/control_plane/test_oracle_validation.py tests/ops/test_oracle_runtime_baseline.py tests/ops/test_macos_environment_entrypoints.py -q`
  - `pnpm test:oracle-runtime:doctor`
  - `pnpm test:oracle-runtime:signoff`
  - `git diff --check`

## Notes

- 这是 roadmap 中最后一个已定义但未完成的 epic，不属于新的产品扩展
- 当前 roadmap 01-12 已全部 `Done`；若后续继续推进，将回到新的 roadmap close-out / extension 流程
