# Progress

## Summary

- Task shape: single-full
- Goal: Notifier 抽象 + notify_history schema + 最小 admin 查询

## Recovery

- 任务: Epic 16 child #1
- 形态: single-full
- 进度: 0/6
- 当前: PLANNED（Epic 16 未激活）
- 文件: `.codex-tasks/20260422-slice01-epic16-notifier-reality/tasks/20260422-01-notifier-abstraction/TODO.csv`
- 下一步: Epic 16 激活后 → TODO `#1` 冻结 PG migration

## Reference

- ADR-0003（Slice 1 monitoring before notification）
- Epic 16 EPIC.md Scope 第 1 项

## Notes

- 本子任务是 #2/#3 的前置；registry 设计必须能插 WeCom/SMS 而无需改 dispatch
- notify_history payload_hash 预留给未来去重 / 静默窗口（Slice 3 会用）
