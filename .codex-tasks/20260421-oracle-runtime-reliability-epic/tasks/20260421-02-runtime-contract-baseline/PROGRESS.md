# Progress

## Summary

- Task shape: single-full
- Goal: 冻结 Oracle runtime reliability 的 contract baseline，避免 scripts / docs / tests 在后续 child 中各自发明不同边界

## Recovery

- 任务: child `#2` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 已关闭；frozen runtime contract 已被 child `#3-#5` 实际消费且未发生边界漂移
- 文件: `.codex-tasks/20260421-oracle-runtime-reliability-epic/tasks/20260421-02-runtime-contract-baseline/TODO.csv`
- 下一步: 无。进入 parent epic，由 child `#3` 及后续 child 复用该 frozen baseline

## Control Contract

- Primary Setpoint: child `#3` 开始前，团队已经明确知道这轮 runtime epic 支持哪些 doctor/signoff surface、哪些 diagnostics、哪些 operator assets，以及哪些仍然在本 epic 之外
- Acceptance: `SPEC.md` 与 `PROGRESS.md` 显式写出当前 seam、批准范围、非目标与 child `#3` 的实现入口
- Guardrails:
  - 不把 runtime doctor 偷换成 fake validator
  - 不在 signoff 尚未定义前就让 docs 宣称 baseline 已完成
  - 不动 analytics / alerting / web 产品 contract
- Sampling Plan:
  - 先记录当前 seam，再冻结批准范围，然后把 child `#3` 的实现入口写清

## Current Seam Inventory

- package/runtime entrypoints:
  - 当前只有 `test:control-plane:oracle`，缺少 repo-level Oracle runtime doctor/signoff 入口
- scripts:
  - `scripts/powershell_shim.py` 能驱动 live gate，但失败时缺少系统化 diagnostics / recovery cues
- validation hints:
  - `apps/api/src/db_monitor_api/control_plane/oracle_validation.py` 已有 sqlplus fallback，但 operator-facing hint 仍不足
- docs/tests:
  - 当前没有 `docs/operator-oracle-runtime-baseline.md`
  - 当前没有 Oracle runtime baseline/checklist 对应的 `tests/ops` contract

## Approved Boundary Draft

- 本 epic 批准的 runtime doctor 面：
  - repo-local root command
  - Oracle driver / sqlplus fallback / container reachability / Postgres prerequisite 的最小 preflight
- 本 epic 批准的 signoff 面：
  - operator docs/checklists/rollback
  - runtime contract tests
  - `pnpm test:control-plane:oracle` 与必要的 Postgres regression
- 本 epic 批准的 diagnostics 面：
  - live-gate 失败时输出 container health/logs 与 sqlplus probe线索
  - Oracle 11g thin-mode incompatibility 的明确 hint
- 本 epic 需要收敛的用户可见面：
  - root package scripts
  - repo-local shim handlers
  - operator runbook / checklist / rollback
  - runtime contract / ops tests
- 本 epic 明确保留在本 epic 之外的内容：
  - 新的产品 surface
  - 整体 release/deployment family 重写
  - 超出 Oracle runtime 的基础设施扩张

## Handoff Gate

- child `#3` 的入口条件：
  - runtime doctor / signoff 的目标语义已写明
  - diagnostics 的批准边界已经明确
  - operator assets 的交付范围已经明确
  - `pnpm test:control-plane:oracle` 与 Postgres regression 不被允许回退

## Latest Evidence

- frozen baseline 已被实现验证：
  - `package.json` / `scripts/powershell_shim.py` 已收敛到 root doctor/signoff 入口
  - `docs/operator-oracle-runtime-baseline.md` 与 checklists 已落地
  - runtime contract / ops tests 已证明 docs、scripts 和 validation hints 使用同一条边界

## Notes

- child `#2` 的价值不是单独交付一块代码，而是确保 runtime doctor/docs/tests/signoff 在同一边界上收敛
