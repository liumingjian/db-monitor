# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 完成 post-Epic-06 close-out review 与 roadmap extension 的 epic 内收口
- 让 Oracle data-plane epic 在磁盘上成为正式 active truth source

## Non-Goals

- 不在本任务中直接实现 Oracle data-plane 产品代码

## Deliverables

- parent `EPIC.md` / `SUBTASKS.csv` / `PROGRESS.md`
- 所有已批准 child task skeleton

## Final Validation Command

```bash
grep -q "Oracle Data Plane and Minimum Insights" EPIC_ROADMAP.md \
  && test -f .codex-tasks/20260420-oracle-data-plane-epic/EPIC.md
```
