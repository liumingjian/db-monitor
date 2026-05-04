# Progress

## Summary

- Task shape: single-full
- Goal: 在 post-Epic-13 close-out review（已于 2026-04-22 上午完成，结论"无 active epic"）之后，基于 Boss 新输入的"还原 lepus-v3.8 全部能力"目标，把 roadmap 显式扩展为 Lepus Parity 路径，并激活 Epic 15 作为新的 active epic

## Recovery

- 任务: post-Epic-13 roadmap extension（从"Epic 14 Conditional Next"转向"Slice 1-8 Lepus Parity"）
- 形态: single-full
- 进度: 3/3
- 当前: 已完成；Epic 15 已激活，Epic 16 已 planned
- 文件: `.codex-tasks/20260422-post-epic13-roadmap-extension-lepus-parity/PROGRESS.md`
- 下一步: 进入 Epic 15 child `#1`（MySQL processlist list）实施

## Why This Extension Happened

- post-Epic-13 close-out review 的结论曾是"无 active epic，Epic 14 仍是 Conditional Next"
- 2026-04-22 Boss 推翻该结论：产品最终目标被重置为"还原 legacy `lepus-v3.8/` 的全部能力"（Option A）
- 执行路径按阶段推进（Option B），已锁定 8 个切片序列（MongoDB 永不复刻、Redis 条件性、SQLServer/OS 正式支持）
- 原始 `PRD.md` 被显式作废；新产品目标以 `CONTEXT.md` + `docs/adr/0001-lepus-parity-pivot.md` + `docs/adr/0002-slice-sequence-and-engine-scope.md` 为真相源

## Decisions Made In The Interview (Q1-Q10)

- `docs/adr/0001-lepus-parity-pivot.md`: PRD 作废；Option B 执行、Option A 终极
- `docs/adr/0002-slice-sequence-and-engine-scope.md`: 8 切片序列 + 永不复刻清单
- `docs/adr/0003-slice1-monitoring-before-notification.md`: 切片 1 拆 Epic 15 + Epic 16，监控先通知后
- `docs/adr/0004-per-instance-threshold-overrides.md`: `rule_instance_overrides` 关联表
- `docs/adr/0005-mysql-runtime-inspection-data-flow.md`: processlist 走采集→CH，kill 走实时
- `docs/adr/0006-runtime-action-permission-and-safety.md`: 新增 `Permission.INSTANCES_ACTION`，切片 1 kill 安全网最小化
- `docs/adr/0007-mysql-slow-query-data-source.md`: performance_schema 采集，不改被监控实例配置
- `docs/adr/0008-multi-dimensional-metrics-dedicated-tables.md`: 多维指标走专表，后续 OS/SQLServer 复用

## Roadmap Changes

- `EPIC_ROADMAP.md` 已更新：Slice 1-8 作为 post-Epic-13 的新主线插入；`Epic 14 (Scale/HA/DR)` 降级为 Slice 8 之后的条件性方向
- Slice 1 = Epic 15 + Epic 16（串行，监控在前通知在后）
- Slice 2-8 在 `CONTEXT.md` 的 Slice sequence 节冻结，每个 slice 激活时再 materialize

## Epic Activation

- Epic 15 "Monitoring depth & rule granularity" 已被激活为 active epic
- 骨架路径：`.codex-tasks/20260422-slice01-epic15-monitoring-depth/`
- Epic 16 "Notification reality & slice-1 acceptance" 已 materialize 但保持 planned，直到 Epic 15 关闭
- 骨架路径：`.codex-tasks/20260422-slice01-epic16-notifier-reality/`

## Validation

- `bash -lc "test -f docs/adr/0001-lepus-parity-pivot.md && test -f docs/adr/0008-multi-dimensional-metrics-dedicated-tables.md && test -f .codex-tasks/20260422-slice01-epic15-monitoring-depth/EPIC.md && test -f .codex-tasks/20260422-slice01-epic16-notifier-reality/EPIC.md && grep -q 'Slice 1 — Monitoring Depth' EPIC_ROADMAP.md"`
