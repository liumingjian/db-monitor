# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 完成 phase-one 的 close-out review
- 从 roadmap 中选择并激活下一个 epic
- 为新 epic 建立可恢复的 parent truth source

## Non-Goals

- 不在本任务中实现下一 epic 的业务代码
- 不绕过 roadmap 临时发明新 epic

## Constraints

- 必须基于 `EPIC_ROADMAP.md` 做顺序裁决
- close-out review 必须记录本轮已证明与未证明的边界
- 只有 close-out review 结束后才允许进入新 epic 的 planning materialization

## Deliverables

- close-out review 结论
- 新 epic 的 parent `EPIC.md` / `SUBTASKS.csv` / `PROGRESS.md`

## Final Validation Command

```bash
powershell -NoProfile -Command "Test-Path '.codex-tasks/20260419-operational-hardening-epic/EPIC.md'; Test-Path '.codex-tasks/20260419-operational-hardening-epic/SUBTASKS.csv'; Test-Path '.codex-tasks/20260419-operational-hardening-epic/PROGRESS.md'"
```
