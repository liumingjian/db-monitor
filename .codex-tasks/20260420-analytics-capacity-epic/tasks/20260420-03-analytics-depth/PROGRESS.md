# Progress

## Summary

- Task shape: single-full
- Goal: 提升 analytics API 的 workload / engine-health 深度

## Recovery

- 任务: workload / engine-health analytics depth 已完成并通过 live gate
- 形态: single-full
- 进度: 3/3
- 当前: 已完成，等待后续 capacity insight 子任务消费
- 文件: `.codex-tasks/20260420-analytics-capacity-epic/tasks/20260420-03-analytics-depth/TODO.csv`
- 下一步: 子任务 `#4` 基于新增的 throughput / buffer-pool signals 定义 risk semantics 与 ranking 视图

## Notes

- analytics service 现在把 `mysql_bytes_sent_total` 聚合成 `mysql_bytes_sent_per_second`，并把 `mysql_innodb_buffer_pool_reads_total` 聚合成 `mysql_innodb_buffer_pool_reads_per_second`
- overview / instance cards 与 charts 已同步补深，preview 和 smoke fixtures 也已更新，避免 UI 与 API spec 再次漂移
- 离线验证已通过：
  - `uv run pytest tests/api/analytics tests/integration/analytics_queries`
  - `pnpm --filter web test`
  - `pnpm --filter web build`
  - `pnpm openapi:check`
- live 验证已通过：
  - `pnpm test:analytics:clickhouse`
