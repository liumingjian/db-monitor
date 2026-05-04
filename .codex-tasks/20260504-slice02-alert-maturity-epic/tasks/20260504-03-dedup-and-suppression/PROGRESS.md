# Progress

## Summary

- Task shape: single-full
- Goal: 在 DispatchCoordinator 入口实现 (rule×instance×severity) 三元组去重 + 默认 10 分钟抑制窗口 + per-rule override

## Recovery

- 任务: Slice 2 child #3
- 形态: single-full
- 进度: 0/N
- 当前: PLANNED（依赖 child #2 + ADR-0014 决议）
- 文件: `.codex-tasks/20260504-slice02-alert-maturity-epic/tasks/20260504-03-dedup-and-suppression/`
- 下一步: ADR-0014 转 Accepted → 设计 schema 迁移 v11→v12 + DispatchCoordinator dedup 判定路径

## Reference

- ADR-0014 告警去重 + 抑制窗口
- ADR-0009 Notifier dynamic control discipline（anti-windup 与 dedup 职责正交）
- lepus `alarm_temp` 表语义（仅参考语义，不抄实现）

## Notes

- 不新增表；复用 `notify_history`
- dedup 判定必须在 DispatchCoordinator 入口（不下放到 channel，避免 4 通道各自实现）
- per-rule override = `alert_rules.suppression_window_seconds INT NULL`
- 抑制状态查询：`(rule_id, instance_id, severity, attempted_at DESC)` 索引
