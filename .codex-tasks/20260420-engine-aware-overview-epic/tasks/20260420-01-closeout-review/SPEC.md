# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 完成 post-Epic-07 roadmap extension 与新 epic activation 收口

## Non-Goals

- 不在本 task 中开始产品实现

## Final Validation Command

```bash
grep -q "Engine-Aware Overview and Fleet Diagnostics" EPIC_ROADMAP.md \
  && test -f .codex-tasks/20260420-engine-aware-overview-epic/EPIC.md
```
