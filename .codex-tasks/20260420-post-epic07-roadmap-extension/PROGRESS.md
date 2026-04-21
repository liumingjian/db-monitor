# Progress

## Summary

- Task shape: single-full
- Goal: 完成 post-Epic-07 的 roadmap extension，并把新的 active epic 完整物化到磁盘

## Recovery

- 任务: 在 Epic 07 close-out review 之后，把用户已同意的下一阶段方向正式写入 roadmap，并完成 phase 2 materialization
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260420-post-epic07-roadmap-extension/TODO.csv`
- 下一步: phase 2 已完成；如继续推进，应从新 active epic 的子任务 `#2 Freeze engine-aware overview contract baseline` 开始实现

## Control Contract

- Primary Setpoint: 在不越界进入产品实现的前提下，把 `Engine-Aware Overview and Fleet Diagnostics` 落成正式 active epic
- Acceptance: `EPIC_ROADMAP.md` 出现新的 active epic；新 epic parent/child skeleton 完整存在；当前只有一个 child 处于 `IN_PROGRESS`
- Guardrails: 不把 multi-engine alerting 提前当作当前 epic；不把只完成 parent 文件误报成 planning complete；不回退 Epic 07 的 Oracle 最小 data-plane 结论
- Sampling Plan: 先基于 close-out review 固定方向，再更新 roadmap，然后一次性创建新 epic 的 parent/child files，最后做静态 completeness 校验
- Constraints: phase 2 只负责 roadmap extension 和 skeleton materialization，不开始 child 实现

## Decision Notes

- 选择 `Engine-Aware Overview and Fleet Diagnostics` 作为 active epic 的依据：
  - `apps/web/src/monitoring-ui.ts` 仍显式写明 Oracle detail 可见，但 overview semantics 和 deeper diagnostics 仍是 `MySQL-first`
  - 当前 `OverviewResponse` / `OverviewInstanceResponse` 还没有 `engine` 维度，说明 overview contract 本身仍带有显式 MySQL-only 假设
  - 相比之下，multi-engine alerting 仍牵动 rule semantics、UI form contract 和 notifier expectations，属于更重的共享契约改动，适合作为 follow-up 而不是当前最小下一步
- roadmap extension 的结果：
  - 新增 `Epic 08: Engine-Aware Overview and Fleet Diagnostics` 作为 `Active`
  - 新增 `Epic 09: Multi-Engine Alerting and Rule Semantics` 作为 `Conditional Next`
- 新 active epic 的当前 child 规划：
  - `#1` 收口 post-Epic-07 review 与 epic activation
  - `#2` 冻结 engine-aware overview contract baseline
  - `#3` 实现 mixed-engine overview aggregation / analytics API
  - `#4` 实现 web overview surface 和 fleet messaging
  - `#5` 深化 engine-aware diagnostics 和 preset semantics
  - `#6` 运行 root signoff 与 live Oracle coverage

## Validation

- `bash -lc '
set -e
grep -q "| 08 | Engine-Aware Overview and Fleet Diagnostics | Active |" EPIC_ROADMAP.md
grep -q "| 09 | Multi-Engine Alerting and Rule Semantics | Conditional Next |" EPIC_ROADMAP.md
[ "$(rg -o "\| [0-9]{2} \| .* \| Active \|" EPIC_ROADMAP.md | wc -l | tr -d " ")" = "1" ]
test -f .codex-tasks/20260420-engine-aware-overview-epic/EPIC.md
test -f .codex-tasks/20260420-engine-aware-overview-epic/SUBTASKS.csv
test -f .codex-tasks/20260420-engine-aware-overview-epic/PROGRESS.md
test -f .codex-tasks/20260420-engine-aware-overview-epic/tasks/20260420-06-overview-signoff/PROGRESS.md
[ "$(rg -o ",IN_PROGRESS," .codex-tasks/20260420-engine-aware-overview-epic/SUBTASKS.csv | wc -l | tr -d " ")" = "1" ]
grep -q "Freeze engine-aware overview contract baseline,single-full,IN_PROGRESS" .codex-tasks/20260420-engine-aware-overview-epic/SUBTASKS.csv
'`
