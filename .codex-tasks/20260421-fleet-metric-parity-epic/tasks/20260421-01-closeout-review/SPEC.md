# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把 post-Epic-10 transition review 与 Epic 11 activation 的结论冻结到当前 epic 内
- 为后续 child 提供一个明确的 phase-1 / phase-2 入口，不允许从 roadmap 耗尽直接跳进实现

## Non-Goals

- 不在本任务中实现 parity 产品代码
- 不把 Oracle runtime reliability 提前当作当前 active epic

## Constraints

- 必须确认 Epic 10 已完成且 PRD closeout 已结束
- 必须确认新的 active epic skeleton 已完整存在
- 完成后 child `#2` 成为唯一 `IN_PROGRESS` child

## Deliverables

- 新 epic 内部的 closeout/activation 证据锚点
- 对应的 child `#1` recovery skeleton

## Final Validation Command

```bash
grep -q "Epic 11" .codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-01-closeout-review/PROGRESS.md \
  && grep -q "child `#2`" .codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-01-closeout-review/PROGRESS.md
```
