# Progress

## Summary

- Task shape: single-full
- Goal: MySQL slow query 短窗列表（PS 增量采集 → CH → API → web tab）

## Recovery

- 任务: Epic 15 child #3
- 形态: single-full
- 进度: 0/7
- 当前: 待启动（并行于 child #1、#4、#5）
- 文件: `.codex-tasks/20260422-slice01-epic15-monitoring-depth/tasks/20260422-03-mysql-slow-query-shortwindow/TODO.csv`
- 下一步: TODO `#1` — 冻结 schema

## Reference

- ADR-0007（数据源）
- ADR-0008（多维指标专表规则）
- child #1 的 web tab 结构（参考复用）

## Notes

- 切片 1 不展示 digest，但必须写入；Slice 5 会在同一张表上加 digest 聚合
- 游标 Redis key: `mysql:slowq:last_event_id:{instance_id}`
