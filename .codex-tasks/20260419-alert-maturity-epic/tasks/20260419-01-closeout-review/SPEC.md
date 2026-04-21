# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 完成 Operational Hardening 的 close-out review
- 基于 roadmap 选择并激活下一个 epic
- 为 Alert Maturity epic 建立可恢复的 parent truth source 与 child skeletons

## Non-Goals

- 不在本任务中实现 alert workflow 业务代码
- 不绕过 roadmap 临时发明新 epic

## Constraints

- 必须基于 Epic 02 的真实 gate 证据做顺序裁决
- 必须一次性创建所有已批准 child task skeleton
- planning 完成前不得提前进入某个 child 的产品实现

## Deliverables

- close-out review 结论
- 新 epic 的 parent `EPIC.md` / `SUBTASKS.csv` / `PROGRESS.md`
- 全量 child `SPEC.md` / `TODO.csv` / `PROGRESS.md`

## Final Validation Command

```bash
powershell -NoProfile -Command "Test-Path '.codex-tasks/20260419-alert-maturity-epic/EPIC.md'; Test-Path '.codex-tasks/20260419-alert-maturity-epic/SUBTASKS.csv'; Test-Path '.codex-tasks/20260419-alert-maturity-epic/PROGRESS.md'"
```
