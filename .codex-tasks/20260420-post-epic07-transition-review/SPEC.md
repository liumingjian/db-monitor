# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 按 `AGENT.md` 完成 Epic 07 之后的正式 close-out review
- 基于 `EPIC_ROADMAP.md`、Epic 07 truth artifacts、`PRD.md`、`RESEARCH.md` 与当前仓库显式边界，判断是否还存在可直接激活的既有 roadmap epic
- 如果现有 roadmap 已耗尽，则明确冻结“下一步”到 roadmap extension，而不是伪造默认 next

## Non-Goals

- 不跳过 close-out review 直接物化新的 epic skeleton
- 不在没有既有 roadmap 选项时伪造“默认 next epic”
- 不在没有显式 repo 证据时拍脑袋发明宽泛新方向

## Constraints

- 这是 `epic close-out review` 阶段，不是 `next epic planning materialization`
- 在 phase 2 真正开始前，不允许创建新的 active epic parent/child skeleton
- 任何后续 roadmap extension 都必须来自当前仓库已显式暴露的主误差
- 必须把结论写回磁盘 truth source，保证后续 agent 可冷启动恢复

## Deliverables

- 本轮 post-Epic-07 transition review 的恢复骨架与结论
- 一个明确的 close-out review，写清：
  - Epic 07 证明了什么
  - Epic 07 没证明什么
  - 当前 roadmap 是否还存在可直接激活的既有 epic
  - 为什么当前下一步必须是 roadmap extension，而不是直接进入实现
  - 哪些显式 repo gap 值得在 phase 2 中被纳入 roadmap 扩展讨论

## Final Validation Command

```bash
grep -q "Close-Out Review" .codex-tasks/20260420-post-epic07-transition-review/PROGRESS.md \
  && grep -q "roadmap 01-07 已全部完成" .codex-tasks/20260420-post-epic07-transition-review/PROGRESS.md \
  && grep -q "phase 2" .codex-tasks/20260420-post-epic07-transition-review/PROGRESS.md
```
