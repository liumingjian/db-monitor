# Progress

## Summary

- Task shape: single-full
- Goal: 收敛 Oracle runtime 的 contract / ops tests 到新的 baseline

## Recovery

- 任务: child `#5` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 无。runtime contract / ops tests 已收口
- 文件: `.codex-tasks/20260421-oracle-runtime-reliability-epic/tasks/20260421-05-runtime-contract-tests/TODO.csv`
- 下一步: 进入 child `#6` 做 root runtime signoff

## Control Contract

- Primary Setpoint: 用 focused contract tests 把 docs、scripts、repo-local runner 与 Oracle validation hint surface 锁在一起
- Acceptance: ops tests 与 oracle validation tests 共同证明 runtime baseline 没有漂移，focused suites 全绿
- Guardrails: 不把 tests 当作 fake success path；不绕过 root commands；不在 docs 和 scripts 间留下未测试漂移

## Latest Evidence

- ops contract tests 已收口：
  - `tests/ops/test_oracle_runtime_baseline.py`
  - `tests/ops/test_macos_environment_entrypoints.py`
- validation hint tests 已收口：
  - `tests/api/control_plane/test_oracle_validation.py`

## Validation

- `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/api/control_plane/test_oracle_validation.py tests/ops/test_oracle_runtime_baseline.py tests/ops/test_macos_environment_entrypoints.py -q`

## Notes

- 本 child 的目标是防止 future drift，不是扩大 runtime signoff 的范围
