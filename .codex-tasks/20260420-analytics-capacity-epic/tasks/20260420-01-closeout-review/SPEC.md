# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 显式完成 Alert Maturity -> Analytics Epic 的 close-out review
- 选择 roadmap 中的下一个 active epic
- 物化完整 parent + child skeleton，满足 `AGENT.md` 的 planning completeness 规则

## Final Validation Command

```bash
bash -lc "test -f .codex-tasks/20260420-analytics-capacity-epic/EPIC.md && test -f .codex-tasks/20260420-analytics-capacity-epic/SUBTASKS.csv && test -f .codex-tasks/20260420-analytics-capacity-epic/PROGRESS.md"
```
