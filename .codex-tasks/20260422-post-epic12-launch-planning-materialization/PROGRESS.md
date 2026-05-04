# Progress

## Summary

- Task shape: single-full
- Goal: 完成 post-Epic-12 的 planning materialization，并把新的 active launch epic 完整物化到磁盘

## Recovery

- 任务: 在 Epic 12 close-out review 之后，把面向投产上线目标的新阶段正式写入 roadmap，并完成 phase 2 materialization
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260422-post-epic12-launch-planning-materialization/PROGRESS.md`
- 下一步: phase 2 已完成；如继续推进，应从新 active epic 的子任务 `#2 Freeze production launch control contract baseline` 开始实现

## Control Contract

- Primary Setpoint: 在不越界进入 launch 实现细节的前提下，把 `Production Launch Readiness and Deployment Baseline` 落成正式 active epic
- Acceptance: `EPIC_ROADMAP.md` 出现新的 active epic；新 epic parent/child skeleton 完整存在；当前只有一个 child 处于 `IN_PROGRESS`
- Guardrails: 不把只完成 roadmap 更新误报成 planning complete；不提前把 Epic 14 激活；不回退“当前产品能力已基本满足内部目标”的 close-out 结论
- Sampling Plan: 先固定 close-out decision，再更新 roadmap，然后一次性创建新 epic 的 parent/child files，最后做静态 completeness 校验
- Constraints: phase 2 只负责 roadmap extension、activation 和 skeleton materialization，不开始 child `#3-#6` 的实现

## Decision Notes

- 选择 `Production Launch Readiness and Deployment Baseline` 作为 active epic 的依据：
  - 当前仓库最大的真实阻塞已经不是产品 surface，而是 release / deployment / launch signoff 闭环
  - `docs/operator-release-baseline.md` 仍是最小 operator baseline，不是正式投产基线
  - 本轮 live evidence 中 `pnpm test:hardening:signoff` 仍未通过，而 `pnpm test:oracle-runtime:signoff` 已通过，说明 launch closure 比 runtime 更接近当前误差中心
  - 仓库当前没有一套正式的 internal production deployment baseline、env contract 和 acceptance signoff 家族
- roadmap extension 的结果：
  - 新增 `Epic 13: Production Launch Readiness and Deployment Baseline` 作为 `Active`
  - 新增 `Epic 14: Scale, High Availability, and Disaster Recovery Hardening` 作为 `Conditional Next`
- 新 active epic 的当前 child 规划：
  - `#1` 收口 post-Epic-12 review 与 epic activation
  - `#2` 冻结 production launch control contract baseline
  - `#3` 恢复 release / hardening gates
  - `#4` 交付 internal production deployment baseline
  - `#5` 收敛 launch config / secrets / ops signoff
  - `#6` 运行 root launch readiness signoff 并关闭 epic

## Validation

- `bash -lc '
set -e
grep -q "| 13 | Production Launch Readiness and Deployment Baseline | Active |" EPIC_ROADMAP.md
grep -q "| 14 | Scale, High Availability, and Disaster Recovery Hardening | Conditional Next |" EPIC_ROADMAP.md
[ "$(rg -o "\| [0-9]{2} \| .* \| Active \|" EPIC_ROADMAP.md | wc -l | tr -d " ")" = "1" ]
test -f .codex-tasks/20260422-production-launch-readiness-epic/EPIC.md
test -f .codex-tasks/20260422-production-launch-readiness-epic/SUBTASKS.csv
test -f .codex-tasks/20260422-production-launch-readiness-epic/PROGRESS.md
test -f .codex-tasks/20260422-production-launch-readiness-epic/tasks/20260422-06-launch-readiness-signoff/PROGRESS.md
[ "$(rg -o ",IN_PROGRESS," .codex-tasks/20260422-production-launch-readiness-epic/SUBTASKS.csv | wc -l | tr -d " ")" = "1" ]
grep -q "Freeze production launch control contract baseline,single-full,IN_PROGRESS" .codex-tasks/20260422-production-launch-readiness-epic/SUBTASKS.csv
'`
