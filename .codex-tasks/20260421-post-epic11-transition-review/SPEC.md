# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 按 `AGENT.md` 完成 Epic 11 之后的正式 close-out review
- 基于 `EPIC_ROADMAP.md`、Epic 11 truth artifacts 与当前仓库显式 runtime seam，判断下一步是否应进入 `Epic 12`
- 在进入 phase 2 前，把“为什么下一步是 Oracle runtime reliability planning materialization”写回磁盘 truth

## Non-Goals

- 不跳过 close-out review 直接开始 Epic 12 的产品或运行时实现
- 不把 Epic 11 的 parity 完成误报成 Oracle runtime 已经制度化收口
- 不在没有显式仓库证据时发明新的 roadmap 方向

## Constraints

- 这是 `epic close-out review` 阶段，不是 `next epic planning materialization`
- 在 phase 2 开始前，不允许创建新的 active epic skeleton
- 结论必须显式写出：
  - Epic 11 证明了什么
  - Epic 11 没证明什么
  - default next epic chosen from current repo gaps
  - why that epic is next
  - what evidence would justify not choosing Oracle runtime reliability

## Deliverables

- 本轮 post-Epic-11 transition review 的恢复骨架与结论
- 一个明确的 close-out review，写清：
  - mixed-engine fleet parity 已完成到什么程度
  - 为什么 `Oracle Runtime Reliability and Live-Gate Productionization` 成为当前默认下一步
  - 哪些代码、脚本、文档与 gate 仍然把 Oracle runtime 复跑维持在脆弱状态
  - 什么证据才会阻止直接进入该 epic

## Final Validation Command

```bash
grep -q "Close-Out Review" .codex-tasks/20260421-post-epic11-transition-review/PROGRESS.md \
  && grep -q "Epic 12" .codex-tasks/20260421-post-epic11-transition-review/PROGRESS.md \
  && grep -q "Oracle Runtime Reliability" .codex-tasks/20260421-post-epic11-transition-review/PROGRESS.md \
  && grep -q "test:control-plane:oracle" .codex-tasks/20260421-post-epic11-transition-review/PROGRESS.md
```
