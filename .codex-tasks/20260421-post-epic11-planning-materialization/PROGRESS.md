# Progress

## Summary

- Task shape: single-full
- Goal: 完成 post-Epic-11 的 planning materialization，并把新的 active epic 完整物化到磁盘

## Recovery

- 任务: 在 Epic 11 close-out review 之后，把用户已同意的下一阶段方向正式写入 roadmap，并完成 phase 2 materialization
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260421-post-epic11-planning-materialization/TODO.csv`
- 下一步: phase 2 已完成；如继续推进，应从新 active epic 的子任务 `#2 Oracle runtime control contract baseline` 开始实现

## Control Contract

- Primary Setpoint: 在不越界进入产品或 runtime 实现的前提下，把 `Oracle Runtime Reliability and Live-Gate Productionization` 落成正式 active epic
- Acceptance: `EPIC_ROADMAP.md` 出现新的 active epic；新 epic parent/child skeleton 完整存在；当前只有一个 child 处于 `IN_PROGRESS`
- Guardrails: 不发明新的 future epic；不把只完成 parent 文件误报成 planning complete；不回退 Epic 11 的 parity close-out 结论
- Sampling Plan: 先基于 close-out review 固定方向，再更新 roadmap，然后一次性创建新 epic 的 parent/child files，最后做静态 completeness 校验
- Constraints: phase 2 只负责 roadmap activation 和 skeleton materialization，不开始 child 实现

## Decision Notes

- 选择 `Oracle Runtime Reliability and Live-Gate Productionization` 作为 active epic 的依据：
  - 当前仓库已经没有显式的产品 contract gap，Oracle runtime repeatability 成为主误差
  - `package.json` 仍缺少 Oracle runtime doctor/signoff 入口
  - `docs/` 仍缺少 Oracle runtime/live-gate operator baseline
  - `scripts/powershell_shim.py` 虽能跑 live gate，但 diagnostics 和恢复路径尚未固化为 operator-friendly surface
- roadmap activation 的结果：
  - `Epic 12: Oracle Runtime Reliability and Live-Gate Productionization` 现在成为 `Active`
- 新 active epic 的当前 child 规划：
  - `#1` 收口 post-Epic-11 review 与 epic activation
  - `#2` 冻结 Oracle runtime control contract baseline
  - `#3` 实现 Oracle runtime doctor 与 richer diagnostics
  - `#4` 交付 operator baseline、checklists 与 root signoff
  - `#5` 补齐 runtime contract / ops tests
  - `#6` 运行 root signoff 与关闭 epic

## Validation

- `bash -lc '
set -e
grep -q "| 12 | Oracle Runtime Reliability and Live-Gate Productionization | Active |" EPIC_ROADMAP.md
[ "$(rg -o "\| [0-9]{2} \| .* \| Active \|" EPIC_ROADMAP.md | wc -l | tr -d " ")" = "1" ]
test -f .codex-tasks/20260421-oracle-runtime-reliability-epic/EPIC.md
test -f .codex-tasks/20260421-oracle-runtime-reliability-epic/SUBTASKS.csv
test -f .codex-tasks/20260421-oracle-runtime-reliability-epic/PROGRESS.md
test -f .codex-tasks/20260421-oracle-runtime-reliability-epic/tasks/20260421-06-runtime-signoff/PROGRESS.md
[ "$(rg -o ",IN_PROGRESS," .codex-tasks/20260421-oracle-runtime-reliability-epic/SUBTASKS.csv | wc -l | tr -d " ")" = "1" ]
grep -q "Oracle runtime control contract baseline,single-full,IN_PROGRESS" .codex-tasks/20260421-oracle-runtime-reliability-epic/SUBTASKS.csv
'`
