# Progress

## Summary

- Task shape: single-full
- Goal: 完成 Epic 12 之后面向投产上线目标的正式 close-out review，并把新的 launch-oriented next step 冻结到磁盘 truth

## Recovery

- 任务: 关闭 Epic 12 之后，重新判断当前仓库距离“可投产上线”还差什么；如果主阻塞不再是产品面，就把下一步冻结为 launch-baseline epic
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260422-post-epic12-launch-transition-review/PROGRESS.md`
- 下一步: 已由 `20260422-post-epic12-launch-planning-materialization` 完成 phase 2 materialization；当前从 `.codex-tasks/20260422-production-launch-readiness-epic/` 的 child `#2` 继续

## Control Contract

- Primary Setpoint: 在不伪造“还缺功能”的前提下，基于真实 repo gap 决定投产目标下的下一 epic
- Acceptance: 本任务 `PROGRESS.md` 明确写出 Epic 12 close-out review、为什么下一步是 launch baseline、什么证据会阻止继续扩产品面
- Guardrails: 不把当前 dirty worktree 的 lint 问题说成新的产品 epic；不把最小内部投产目标偷换成 full CI/CD 或 HA 平台建设；不回退 Epic 12 的 runtime close-out 结论
- Sampling Plan: 先读 roadmap / PRD / operator baselines，再跑最关键的 live gate，对比哪些已绿、哪些仍阻塞投产
- Constraints: 只有在 Epic 01-12 已全部 `Done` 的前提下，才允许用投产目标驱动 roadmap extension

## Close-Out Review

- Epic 12 证明了什么：
  - Oracle runtime / live-gate 已具备 doctor、signoff、operator baseline、rollback 与 diagnostics surface
  - runtime confidence 已经从“环境偶然能跑一次”提升到“有 repo-local signoff 与恢复入口”
  - 01-12 的历史 epic 已让产品能力明显超出原始 `PRD.md`
- Epic 12 没证明什么：
  - 当前 worktree 是否已经满足 repo 自身的 release / hardening gate
  - operator 是否拥有正式的 internal production deployment baseline，而不只是最小本地发布说明
  - 当前仓库是否已经具备一套明确的 launch config / secrets / acceptance contract
- 当前最强证据：
  - `pnpm test:oracle-runtime:signoff` 已通过，说明 runtime 不再是本轮最强阻塞
  - `pnpm test:hardening:signoff` 在 `pnpm lint` 处失败，Biome 报出 `21` 个格式 / import-order 问题，说明当前分支还不能按 repo 自身门禁直接发版
  - `docs/operator-release-baseline.md` 仍显式定位为“最小 operator 发布基线”，并明确目标不是完整 `CI/CD`
  - 仓库中尚未形成正式的 production deployment baseline / launch checklist / env contract epic

## Decision Gate

- 当前结论：
  - 当前主误差已经从“功能还不够”切到“投产闭环还没正式收口”
  - 下一步不应再开启新的产品 epic，而应激活 `Production Launch Readiness and Deployment Baseline`
- 为什么不是别的方向：
  - 再扩 dashboard / analytics / control-plane feature 不能解决当前 hardening gate 仍为红灯的问题
  - 直接跳到 HA / DR 会过早引入重基础设施复杂性，与当前内部单环境投产目标不匹配
- 当前结果：
  - roadmap 已扩展到 `Epic 13: Production Launch Readiness and Deployment Baseline`
  - `Epic 14: Scale, High Availability, and Disaster Recovery Hardening` 被保留为 `Conditional Next`

## Validation

- `bash -lc "grep -q 'pnpm test:hardening:signoff' .codex-tasks/20260422-post-epic12-launch-transition-review/PROGRESS.md && grep -q 'Production Launch Readiness and Deployment Baseline' .codex-tasks/20260422-post-epic12-launch-transition-review/PROGRESS.md && grep -q 'Conditional Next' .codex-tasks/20260422-post-epic12-launch-transition-review/PROGRESS.md"`
