# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在 Epic 08 close-out review 已完成的前提下，执行 post-Epic-08 的 planning materialization
- 把 `Multi-Engine Alerting and Rule Semantics` 从 roadmap brief 物化为完整的 active epic skeleton
- 保持严格 phase separation：本轮先完成 phase 2，再把 Epic 09 的 child `#1` 作为唯一 `IN_PROGRESS` 入口

## Non-Goals

- 不在本任务中实现 Epic 09 的产品代码
- 不只创建 parent epic 文件而漏掉 child recovery skeleton
- 不在没有证据时新发明 roadmap 方向

## Constraints

- 新 epic 必须来自已有 roadmap 条目，而不是临时扩展方向
- 必须更新 `EPIC_ROADMAP.md`
- 必须一次性完整创建：
  - parent `EPIC.md`
  - parent `SUBTASKS.csv`
  - parent `PROGRESS.md`
  - 每个 child task 的 `SPEC.md` / `TODO.csv` / `PROGRESS.md`
- 完成后只允许一个 child task 标记为 `IN_PROGRESS`

## Deliverables

- 本轮 post-Epic-08 planning materialization 的恢复骨架与结论
- 更新后的 `EPIC_ROADMAP.md`
- 一个完整 materialize 的新 active epic：
  - `.codex-tasks/20260420-multi-engine-alerting-epic/`

## Final Validation Command

```bash
grep -q "| 09 | Multi-Engine Alerting and Rule Semantics | Active |" EPIC_ROADMAP.md \
  && test -f .codex-tasks/20260420-multi-engine-alerting-epic/EPIC.md \
  && test -f .codex-tasks/20260420-multi-engine-alerting-epic/SUBTASKS.csv \
  && test -f .codex-tasks/20260420-multi-engine-alerting-epic/PROGRESS.md \
  && test -f .codex-tasks/20260420-multi-engine-alerting-epic/tasks/20260420-06-alerting-signoff/PROGRESS.md
```
