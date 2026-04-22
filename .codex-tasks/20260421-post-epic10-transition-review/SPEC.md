# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 按 `AGENT.md` 完成 Epic 10 之后的正式 close-out review
- 基于 `EPIC_ROADMAP.md`、`docs/prd-closeout.md`、Epic 10 truth artifacts 与当前仓库显式 gap，判断下一步是否应进入 `Epic 11`
- 在进入 phase 2 前，把“为什么下一步是 fleet metric parity planning materialization，而不是继续补 PRD debt 或直接做 Oracle runtime”写回磁盘 truth

## Non-Goals

- 不跳过 close-out review 直接开始 Epic 11 的产品代码实现
- 不把 phase-one closeout 完成误报成“仓库已经没有可扩展方向”
- 不在没有显式 repo 证据时激活 Oracle runtime hardening

## Constraints

- 这是 `epic close-out review` 阶段，不是 `next epic planning materialization`
- 在 phase 2 开始前，不允许创建新的 active epic skeleton
- 结论必须显式写出：
  - Epic 10 证明了什么
  - Epic 10 没证明什么
  - default next epic chosen from current repo gaps
  - why that epic is next
  - what evidence would justify choosing Oracle runtime reliability instead

## Deliverables

- 本轮 post-Epic-10 transition review 的恢复骨架与结论
- 一个明确的 close-out review，写清：
  - PRD closeout 已经完成到什么程度
  - 为什么 `Multi-Engine Fleet Metric Parity and Overview Convergence` 成为当前默认下一步
  - 哪些代码与文案仍然把 overview metrics 锁在 MySQL-only
  - 什么新的 runtime 证据才会让团队优先进入 Oracle live-gate productionization

## Final Validation Command

```bash
grep -q "Close-Out Review" .codex-tasks/20260421-post-epic10-transition-review/PROGRESS.md \
  && grep -q "Epic 11" .codex-tasks/20260421-post-epic10-transition-review/PROGRESS.md \
  && grep -q "Oracle Runtime Reliability" .codex-tasks/20260421-post-epic10-transition-review/PROGRESS.md \
  && grep -q "OVERVIEW_METRIC_ENGINES" .codex-tasks/20260421-post-epic10-transition-review/PROGRESS.md
```
