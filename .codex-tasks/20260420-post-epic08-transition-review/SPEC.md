# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 按 `AGENT.md` 完成 Epic 08 之后的正式 close-out review
- 基于 `EPIC_ROADMAP.md`、Epic 08 truth artifacts 与当前仓库显式边界，判断是否应把 Epic 09 从 `Conditional Next` 提升为默认下一步
- 在真正进入 phase 2 之前，把“为什么下一步是 Epic 09 planning materialization，而不是直接实现”写回磁盘 truth source

## Non-Goals

- 不跳过 close-out review 直接开始 Epic 09 的产品代码实现
- 不在没有仓库证据时改写路线图方向
- 不把 mixed-engine overview baseline 误报成 multi-engine alert parity

## Constraints

- 这是 `epic close-out review` 阶段，不是 `next epic planning materialization`
- 在 phase 2 真正开始前，不允许创建 Epic 09 的 parent/child skeleton
- 结论必须显式写出：
  - Epic 08 证明了什么
  - Epic 08 没证明什么
  - default next epic chosen from roadmap
  - why that epic is next
  - what evidence would justify skipping or reordering it

## Deliverables

- 本轮 post-Epic-08 transition review 的恢复骨架与结论
- 一个明确的 close-out review，写清：
  - mixed-engine overview baseline 现在已经证明到什么程度
  - 为什么 Epic 09 现在成为最合理的默认下一步
  - 哪些显式仓库证据表明 rule / alert semantics 仍明显围绕 MySQL 指标组织
  - 什么新的证据才会让团队不直接进入 Epic 09 planning materialization

## Final Validation Command

```bash
grep -q "Close-Out Review" .codex-tasks/20260420-post-epic08-transition-review/PROGRESS.md \
  && grep -q "Epic 09" .codex-tasks/20260420-post-epic08-transition-review/PROGRESS.md \
  && grep -q "planning materialization" .codex-tasks/20260420-post-epic08-transition-review/PROGRESS.md \
  && grep -q "mysql_" .codex-tasks/20260420-post-epic08-transition-review/PROGRESS.md
```
