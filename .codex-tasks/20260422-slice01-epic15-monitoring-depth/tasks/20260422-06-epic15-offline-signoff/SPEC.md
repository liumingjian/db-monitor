# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- Epic 15 的离线 signoff：hardening gate 全绿、schema bootstrap 成立、新能力 smoke 通过；Epic 15 的 EPIC.md / SUBTASKS.csv / PROGRESS.md 最终状态更新；**不**做真实值班演练（那是 Epic 16 child `#5`）

## Scope

- 复跑 `pnpm test:hardening:signoff`
- 复跑 `pnpm test:schema:bootstrap`（覆盖新建 3 张 CH 表 + 1 张 PG 表）
- 复跑 `pnpm smoke:web`（覆盖新 4 个 UI 面：Processes tab、Slow queries tab、Tablespaces tab、Rule overrides 子表）
- 更新 `.codex-tasks/20260422-slice01-epic15-monitoring-depth/PROGRESS.md` Recovery 段到 6/6
- 更新 `SUBTASKS.csv` 将所有 child 标 `DONE`
- 写一段 Close-Out Review：Epic 15 证明了什么 / 没证明什么 / 下一步 Epic 16 的 activation 条件

## Non-Goals

- 不做真实值班演练（Epic 16）
- 不发公告、不改 operator baseline（Slice 1 结束再说）
- 不扩新能力 / 新 ADR

## Final Validation Command

```bash
pnpm test:hardening:signoff && pnpm test:schema:bootstrap && pnpm smoke:web
```
