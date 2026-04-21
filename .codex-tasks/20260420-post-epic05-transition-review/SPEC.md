# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 按 `AGENT.md` 完成 Epic 05 之后的正式 close-out review
- 基于 `EPIC_ROADMAP.md`、`PRD.md`、已完成 epic 与 Oracle follow-up 证据，判断是否可以激活后续 epic
- 如果激活会跨越当前单租户冻结边界，则把阻塞点和需要确认的决策写清楚

## Non-Goals

- 不在本任务中直接实现新的产品功能
- 不在未获确认前擅自激活 `Tenant and Organization Governance`
- 不跳过路线图临时发明新的顶层 epic

## Constraints

- 必须先完成 close-out review，再决定是否物化下一 epic 骨架
- 只能在已有路线图中做选择
- 如果下一步会突破 `PRD.md` 的单租户边界，必须显式停在决策门，而不是假装可以无损继续

## Deliverables

- 本轮 epic transition 的恢复骨架与 close-out review 记录
- 是否可激活下一 epic 的明确结论
- 若不可直接激活，给出最小确认问题

## Final Validation Command

```bash
test -f .codex-tasks/20260420-post-epic05-transition-review/PROGRESS.md \
  && grep -q "Epic 06" .codex-tasks/20260420-post-epic05-transition-review/PROGRESS.md
```
