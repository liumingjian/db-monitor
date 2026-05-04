# Progress

## Summary

- Task shape: single-full
- Goal: 完成 post-Epic-10 的 planning materialization，并把新的 active epic 完整物化到磁盘

## Recovery

- 任务: 在 Epic 10 close-out review 之后，把用户已同意的下一阶段方向正式写入 roadmap，并完成 phase 2 materialization
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260421-post-epic10-planning-materialization/TODO.csv`
- 下一步: phase 2 已完成；如继续推进，应从新 active epic 的子任务 `#2 Freeze fleet metric parity contract baseline` 开始实现

## Control Contract

- Primary Setpoint: 在不越界进入产品实现的前提下，把 `Multi-Engine Fleet Metric Parity and Overview Convergence` 落成正式 active epic
- Acceptance: `EPIC_ROADMAP.md` 出现新的 active epic；新 epic parent/child skeleton 完整存在；当前只有一个 child 处于 `IN_PROGRESS`
- Guardrails: 不把 Oracle runtime reliability 提前当作当前 epic；不把只完成 parent 文件误报成 planning complete；不回退 Epic 10 的 PRD closeout 结论
- Sampling Plan: 先基于 close-out review 固定方向，再更新 roadmap，然后一次性创建新 epic 的 parent/child files，最后做静态 completeness 校验
- Constraints: phase 2 只负责 roadmap extension 和 skeleton materialization，不开始 child 实现

## Decision Notes

- 选择 `Multi-Engine Fleet Metric Parity and Overview Convergence` 作为 active epic 的依据：
  - `apps/api/src/db_monitor_api/analytics/service.py` 仍显式把 fleet-level overview metrics 锁定在 MySQL
  - `apps/web/src/monitoring-ui.ts` 仍显式把 mixed-engine overview 呈现为 `Mixed-engine baseline` / `Metrics scoped`
  - 当前的主误差已经不再是 PRD debt，而是“第二引擎已进入产品面，但 overview fleet metrics 仍未完成 parity 收敛”
- roadmap extension 的结果：
  - 新增 `Epic 11: Multi-Engine Fleet Metric Parity and Overview Convergence` 作为 `Active`
  - 新增 `Epic 12: Oracle Runtime Reliability and Live-Gate Productionization` 作为 `Conditional Next`
- 新 active epic 的当前 child 规划：
  - `#1` 收口 post-Epic-10 review 与 epic activation
  - `#2` 冻结 fleet metric parity contract baseline
  - `#3` 实现 mixed-engine overview aggregation / analytics API parity
  - `#4` 实现 web overview parity surface 和 fleet messaging
  - `#5` 收敛 diagnostics、leaders 与 preset semantics
  - `#6` 运行 root signoff 与 Oracle live coverage

## Validation

- `bash -lc '
set -e
grep -q "| 11 | Multi-Engine Fleet Metric Parity and Overview Convergence | Active |" EPIC_ROADMAP.md
grep -q "| 12 | Oracle Runtime Reliability and Live-Gate Productionization | Conditional Next |" EPIC_ROADMAP.md
[ "$(rg -o "\| [0-9]{2} \| .* \| Active \|" EPIC_ROADMAP.md | wc -l | tr -d " ")" = "1" ]
test -f .codex-tasks/20260421-fleet-metric-parity-epic/EPIC.md
test -f .codex-tasks/20260421-fleet-metric-parity-epic/SUBTASKS.csv
test -f .codex-tasks/20260421-fleet-metric-parity-epic/PROGRESS.md
test -f .codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-06-parity-signoff/PROGRESS.md
[ "$(rg -o ",IN_PROGRESS," .codex-tasks/20260421-fleet-metric-parity-epic/SUBTASKS.csv | wc -l | tr -d " ")" = "1" ]
grep -q "Freeze fleet metric parity contract baseline,single-full,IN_PROGRESS" .codex-tasks/20260421-fleet-metric-parity-epic/SUBTASKS.csv
'`
