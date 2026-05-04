# Progress

## Summary

- Task shape: epic
- Goal: 用一轮有边界的 launch epic，把仓库从“能力基本具备”推进到“可面向内部单环境投产的正式发布 / 部署基线”

## Recovery

- 任务: Epic 13 已完成
- 形态: epic
- 进度: 6/6
- 当前: 无 active child；launch baseline、env contract 与 final signoff 已完成
- 文件: `.codex-tasks/20260422-production-launch-readiness-epic/SUBTASKS.csv`
- 下一步: 无。若继续推进，先做 post-Epic-13 close-out review，再判断是否激活 `Epic 14`

## Control Contract

- Primary Setpoint: 当前仓库的下一轮投入，必须直接减少投产上线误差，而不是继续扩产品面
- Acceptance: 新 epic truth artifacts 与 child skeleton 已落盘；active child 已写明当前 launch seam 和批准边界；后续 child 仍可从磁盘恢复
- Guardrails: 不回退 Epic 01-12 的产品和 runtime close-out；不把 internal single-environment launch 偷换成 full CI/CD 或 HA；不在 gate 尚未恢复前宣称“已可投产”
- Sampling Plan: 先做 contract baseline，再做 release gate / deployment baseline / env contract，最后做 root signoff
- Constraints: 只有 `SUBTASKS.csv` 中列出的 child 能进入实现；未进入 `IN_PROGRESS` 的 child 不允许提前写生产实现

## Latest Evidence

- child `#2` 已冻结 launch boundary：
  - 目标环境固定为 `internal single-environment production`
  - gate family 固定为 `hardening + oracle-runtime + launch-readiness signoff`
  - 非目标明确排除 `CI/CD / Kubernetes / Terraform / HA/DR`
- child `#3` 已恢复 release / hardening gates：
  - `pnpm exec biome check --write ...` 收口了 web/api-client 的格式与 import-order drift
  - `apps/api/src/db_monitor_api/control_plane/oracle_validation.py` 与多处 gate/tests 已补齐 mypy contract
  - `pnpm test:hardening:signoff` 已通过
- child `#4` 与 child `#5` 已交付 launch baseline：
  - `docs/operator-release-baseline.md` 已升级为 internal production launch runbook
  - `docs/operator-launch-environment-baseline.md` 与 `docs/operator-launch-acceptance-checklist.md` 已补齐 env / acceptance contract
  - `scripts/test-launch-readiness-signoff.ps1`、`package.json` 与 `scripts/powershell_shim.py` 已新增 root launch signoff 入口
  - `tests/ops/test_launch_readiness_baseline.py` 已覆盖 docs / scripts / runner mapping contract
- child `#6` 已完成 final signoff：
  - `pnpm test:launch-readiness:signoff`
  - `pnpm test:hardening:signoff`
  - `pnpm test:oracle-runtime:signoff`
  - `git diff --check`

## Notes

- 这个 epic 的目标是内部单环境投产，不是一次性建立完整发布平台
- `Epic 14` 已保留为 `Conditional Next`，但当前没有证据要求立刻激活
