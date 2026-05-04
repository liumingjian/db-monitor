# Progress

## Summary

- Task shape: single-full
- Goal: 冻结 production launch readiness 的 contract baseline，避免后续 child 围绕不同的投产目标各自收敛

## Recovery

- 任务: child `#2` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 已关闭；launch boundary 已被 child `#3-#6` 实际消费并未发生范围漂移
- 文件: `.codex-tasks/20260422-production-launch-readiness-epic/tasks/20260422-02-launch-contract-baseline/TODO.csv`
- 下一步: 无。后续 child 已按该 baseline 收口

## Control Contract

- Primary Setpoint: child `#3` 开始前，团队已经明确知道本轮 launch epic 针对哪种上线目标、哪些门禁必须恢复、哪些能力仍然故意不做
- Acceptance: `SPEC.md` 与 `PROGRESS.md` 显式写出当前 seam、批准的 launch boundary、非目标与 child `#3` 的实现入口
- Guardrails:
  - 不把 dirty worktree 的 gate 失败解释成新的产品功能缺口
  - 不在 deployment baseline 尚未定义前就写死具体基础设施方案
  - 不把内部单环境 launch 偷换成 full CI/CD、HA 或多环境 platform
- Sampling Plan:
  - 先记录当前 seam，再冻结批准范围，然后写清 child `#3-#6` 的实现入口

## Current Seam Inventory

- 产品与 runtime 基线：
  - `EPIC_ROADMAP.md` 现在已经关闭 01-12，说明主线产品与 Oracle runtime close-out 已完成
  - `PRD.md` 仍把目标界定为内部单租户、local-first，而不是广义平台化发布系统
- operator / release 基线：
  - `docs/operator-release-baseline.md` 仍显式定位为“最小 operator 发布基线”
  - 该文档还明确写出目标不是建设完整 `CI/CD`
- live gate 证据：
  - 本轮 live 运行中，`pnpm test:oracle-runtime:signoff` 已通过
  - 同一轮里，`pnpm test:hardening:signoff` 在 `pnpm lint` 处失败，Biome 报出 `21` 个格式 / import-order 问题
- deployment / env 资产：
  - 当前 repo 尚未形成一套正式的 internal production deployment baseline / launch checklist / env contract truth family
  - 当前最强误差不是“还能再加什么产品功能”，而是“当前分支还不能按仓库自己的标准完成投产签收”

## Latest Evidence

- 当前 seam inventory 已完成，并有静态证据锚点：
  - `rg -q '最小 operator 发布基线' docs/operator-release-baseline.md`
  - `rg -q 'CI/CD' docs/operator-release-baseline.md`
  - `rg -q '单租户' PRD.md`
  - `rg -q 'pnpm test:hardening:signoff' .codex-tasks/20260422-post-epic12-launch-transition-review/PROGRESS.md`
- 当前 live evidence 结论：
  - runtime signoff 已绿，但 hardening signoff 仍红
  - launch closure 比继续扩产品面更接近当前主误差

## Approved Boundary Draft

- 本 epic 批准的目标环境：
  - internal single-environment production launch
  - 单租户、受控 operator、repo-local signoff 驱动
- 本 epic 需要收敛的门禁族：
  - branch / root release gate
  - internal production deployment baseline
  - launch config / secrets / ops acceptance contract
  - final launch readiness signoff
- 本 epic 批准的交付面：
  - 发布与部署前置条件
  - operator checklist / rollback / acceptance
  - repo-local script / doc / test / signoff 对齐
- 本 epic 明确保留在边界之外的内容：
  - 完整 CI/CD / environment promotion 平台
  - Kubernetes / Terraform / 多环境编排
  - HA / DR / 多地域架构
  - 新的 analytics / alerting / control-plane 产品功能

## Handoff Gate

- child `#3` 的入口条件：
  - launch target 已冻结为 internal single-environment production
  - 当前红灯已明确收敛到 release / hardening gate，而不是产品功能缺口
  - later children 需要对齐的 gate family 与非目标已写明
- child `#4-#6` 的预期协同：
  - `#3` 先恢复 release gate，避免在脏分支上堆新的 deployment baseline
  - `#4` 再把真实部署 / rollback / acceptance 资产物化成 repo-local baseline
  - `#5` 负责把 config / secrets / ops validation 收拢成同一 contract
  - `#6` 只在前三者一致后运行最终 signoff

## Notes

- child `#2` 的价值不是先写实现代码，而是防止后续 child 各自发明不同的投产目标
- 当前 frozen boundary 已被 child `#3-#6` 证明可执行，因此本 child 无残留 open question
