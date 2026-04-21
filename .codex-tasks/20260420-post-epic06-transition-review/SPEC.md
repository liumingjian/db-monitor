# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 按 `AGENT.md` 完成 Epic 06 之后的正式 close-out review
- 基于 `EPIC_ROADMAP.md`、`PRD.md`、当前已完成 epic 与仓库内显式 gap，判断“下一阶段”是否还存在默认 epic
- 如果现有 roadmap 已耗尽，则先扩展 roadmap，再物化新的 epic 骨架并进入实现

## Non-Goals

- 不跳过 close-out review 直接写新的产品代码
- 不伪造“默认 next”来绕开 roadmap 已完成的事实
- 不在没有显式 repo 证据时拍脑袋发明宽泛新方向

## Constraints

- 必须先完成 close-out review，再扩展 roadmap 或物化新 epic
- 新阶段方向必须来自当前仓库已经显式暴露的主误差，而不是聊天中的抽象想象
- 必须把结论回写到磁盘 truth source，保证后续 agent 可冷启动恢复

## Deliverables

- 本轮 post-Epic-06 transition review 的恢复骨架与结论
- 更新后的 `EPIC_ROADMAP.md`
- 一个已经完整 materialize 的新 epic parent/child skeleton

## Final Validation Command

```bash
grep -q "Oracle Data Plane and Minimum Insights" EPIC_ROADMAP.md \
  && test -f .codex-tasks/20260420-oracle-data-plane-epic/EPIC.md \
  && test -f .codex-tasks/20260420-oracle-data-plane-epic/SUBTASKS.csv \
  && test -f .codex-tasks/20260420-oracle-data-plane-epic/PROGRESS.md
```
