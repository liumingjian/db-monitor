# Progress

## Summary

- Task shape: single-full
- Goal: 交付 operator baseline、checklists 与 root signoff

## Recovery

- 任务: child `#4` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 无。operator baseline、checklists 与 root signoff surface 已收口
- 文件: `.codex-tasks/20260421-oracle-runtime-reliability-epic/tasks/20260421-04-operator-baseline-signoff/TODO.csv`
- 下一步: 把 operator baseline 提供给 child `#5/#6` 做 contract tests 与 signoff

## Control Contract

- Primary Setpoint: 让 Oracle runtime preconditions、rollback、failure isolation 与 root signoff 进入正式 operator surface
- Acceptance: runbook/checklist/rollback 真实映射到 package scripts 与 repo-local runner，ops tests 全绿
- Guardrails: 不在文档里编造不存在的恢复路径；不把 runtime doc 扩成新的 release family；不让 docs 与 root commands 漂移

## Latest Evidence

- operator assets 已收口：
  - `docs/operator-oracle-runtime-baseline.md`
  - `docs/operator-oracle-runtime-checklist.md`
  - `docs/operator-oracle-runtime-rollback-checklist.md`
- root signoff surface 已收口：
  - `scripts/test-oracle-runtime-doctor.ps1`
  - `scripts/test-oracle-runtime-signoff.ps1`
  - `package.json` 中的 `test:oracle-runtime:doctor` / `test:oracle-runtime:signoff`

## Validation

- `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/ops/test_oracle_runtime_baseline.py tests/ops/test_macos_environment_entrypoints.py -q`

## Notes

- 本 child 收口的是 operator-facing baseline，不是新的部署系统
