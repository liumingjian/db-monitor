# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在 Epic 07 close-out review 已完成的前提下，执行 post-Epic-07 的 roadmap extension
- 把用户同意的下一阶段方向落成正式 roadmap 条目，并完整 materialize 新的 active epic skeleton
- 保持严格 phase separation：本轮只完成 phase 2，不提前开始新 epic 的产品代码实现

## Non-Goals

- 不在本任务中实现 overview / diagnostics 产品代码
- 不把 multi-engine alerting 提前激活成当前 active epic
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

- 本轮 post-Epic-07 roadmap extension 的恢复骨架与结论
- 更新后的 `EPIC_ROADMAP.md`
- 一个完整 materialize 的新 active epic：
  - `.codex-tasks/20260420-engine-aware-overview-epic/`

## Final Validation Command

```bash
grep -q "Engine-Aware Overview and Fleet Diagnostics" EPIC_ROADMAP.md \
  && test -f .codex-tasks/20260420-engine-aware-overview-epic/EPIC.md \
  && test -f .codex-tasks/20260420-engine-aware-overview-epic/SUBTASKS.csv \
  && test -f .codex-tasks/20260420-engine-aware-overview-epic/PROGRESS.md \
  && test -f .codex-tasks/20260420-engine-aware-overview-epic/tasks/20260420-06-overview-signoff/PROGRESS.md
```
