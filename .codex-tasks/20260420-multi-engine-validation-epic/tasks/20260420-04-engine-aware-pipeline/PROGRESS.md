# Progress

## Summary

- Task shape: single-full
- Goal: 建立 engine-aware dispatch seam

## Recovery

- 任务: 已完成 engine-aware pipeline dispatch baseline
- 形态: single-full
- 进度: 3/3
- 当前: 已完成最终验证
- 文件: `.codex-tasks/20260420-multi-engine-validation-epic/tasks/20260420-04-engine-aware-pipeline/TODO.csv`
- 下一步: 将父 epic 切换到子任务 `#5 Expose engine-aware semantics in web inventory and detail flows`

## Notes

- 子任务 `#2/#3` 已完成，因此当前主误差不再是资产建模或 Oracle onboarding，而是 pipeline 调度面是否真的能按 engine 分流
- 已实现的最小控制输入：
  - `CollectionJob` 现在持有 `engine`，并保留旧 MySQL 队列 payload 的向后兼容解码
  - scheduler 通过 `SUPPORTED_COLLECTION_ENGINES` 显式只调度当前受支持的引擎，而不是让 Oracle 假装掉进 MySQL worker
- 本轮验证证据：
  - `uv run pytest tests/scheduler tests/integration/metrics_pipeline tests/worker_mysql`
- 当前 pipeline gap 仍然明确存在，而且本轮故意没有掩盖：
  - Redis queue 默认名仍是 `db-monitor:mysql-metrics`
  - ClickHouse sink 表仍是 `mysql_metrics`
  - collector protocol、normalization、worker 实现仍是 MySQL-specific
  - Oracle 在 dispatch 层被显式跳过，而不是被伪装成已支持
