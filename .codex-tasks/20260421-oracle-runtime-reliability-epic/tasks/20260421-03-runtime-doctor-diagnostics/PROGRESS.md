# Progress

## Summary

- Task shape: single-full
- Goal: 交付 repo-local Oracle runtime doctor 与 richer diagnostics

## Recovery

- 任务: child `#3` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 无。runtime doctor 与 diagnostics 已收口
- 文件: `.codex-tasks/20260421-oracle-runtime-reliability-epic/tasks/20260421-03-runtime-doctor-diagnostics/TODO.csv`
- 下一步: 把稳定的 runtime doctor surface 提供给 child `#4/#5/#6`

## Control Contract

- Primary Setpoint: 让 Oracle runtime preflight 和 live-gate diagnostics 变成正式 repo surface，而不是当前环境的隐式知识
- Acceptance: root doctor command、shared sqlplus self-probe、Oracle validation hints 与 diagnostics 在同一条路径上收敛，focused tests 全绿
- Guardrails: 不引入 fake success path；不把 diagnostics 写成 silent fallback；不越界扩到新的产品 contract

## Latest Evidence

- root runtime doctor 已收口：
  - `package.json` 现在新增 `test:oracle-runtime:doctor`
  - `scripts/powershell_shim.py` 现在新增 `handle_oracle_runtime_doctor`
- richer diagnostics 已收口：
  - Oracle live-gate 失败时，shim 会输出 container health、recent logs 与 sqlplus self-probe
  - `handle_control_plane_oracle` 不再把 live-gate failure 当作 opaque test failure 直接抛出
- Oracle validation hint 已收口：
  - missing driver detail 现在显式提示 `DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER`
  - `DPY-3010` 现在会被解释成 Oracle 11g/XE thin-mode incompatibility，并明确提示 sqlplus docker fallback

## Validation

- `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/api/control_plane/test_oracle_validation.py tests/ops/test_macos_environment_entrypoints.py -q`
- `pnpm test:oracle-runtime:doctor`

## Notes

- 本 child 交付的是 debug-first runtime observability，不是新的 control-plane 功能
