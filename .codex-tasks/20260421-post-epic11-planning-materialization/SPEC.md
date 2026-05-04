# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在 post-Epic-11 close-out review 已完成的前提下，执行 Epic 12 的 planning materialization
- 把用户同意的下一阶段方向落成正式 roadmap 条目，并完整 materialize 新的 active epic skeleton
- 保持严格 phase separation：本轮只完成 phase 2，不提前开始新 epic 的实现

## Non-Goals

- 不在本任务中实现 Oracle runtime / live-gate 的具体代码
- 不跳过 roadmap 激活直接把 Epic 12 做成隐式 side task
- 不只创建 parent epic 文件而漏掉 child recovery skeleton

## Constraints

- 新 epic 必须来自当前仓库显式暴露的主误差
- 必须更新 `EPIC_ROADMAP.md`
- 必须一次性完整创建：
  - parent `EPIC.md`
  - parent `SUBTASKS.csv`
  - parent `PROGRESS.md`
  - 每个 child task 的 `SPEC.md` / `TODO.csv` / `PROGRESS.md`
- 完成后只允许把一个 child task 标记为 `IN_PROGRESS`

## Deliverables

- 本轮 post-Epic-11 planning materialization 的恢复骨架与结论
- 更新后的 `EPIC_ROADMAP.md`
- 一个完整 materialize 的新 active epic：
  - `.codex-tasks/20260421-oracle-runtime-reliability-epic/`

## Final Validation Command

```bash
grep -q "Oracle Runtime Reliability and Live-Gate Productionization" EPIC_ROADMAP.md \
  && test -f .codex-tasks/20260421-oracle-runtime-reliability-epic/EPIC.md \
  && test -f .codex-tasks/20260421-oracle-runtime-reliability-epic/SUBTASKS.csv \
  && test -f .codex-tasks/20260421-oracle-runtime-reliability-epic/PROGRESS.md \
  && test -f .codex-tasks/20260421-oracle-runtime-reliability-epic/tasks/20260421-06-runtime-signoff/PROGRESS.md
```
