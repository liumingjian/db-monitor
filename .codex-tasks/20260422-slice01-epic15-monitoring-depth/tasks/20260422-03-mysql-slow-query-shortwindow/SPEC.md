# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 db-monitor 能呈现"最近 N 分钟最慢 K 条"的 MySQL 慢查询：worker 增量拉 `performance_schema.events_statements_history_long` 写入 ClickHouse；API 支持多维筛选；web 实例 detail 新增 Slow queries tab

## Key Decisions (Inputs)

- `docs/adr/0007-mysql-slow-query-data-source.md`
- `docs/adr/0008-multi-dimensional-metrics-dedicated-tables.md`

## Schema

- 新 ClickHouse 表 `mysql_slow_query_events`（列与 TTL 见 ADR-0007）
- `slow_threshold_seconds` 存于 `instance_parameters` JSONB 载体：`parameters->>'slow_threshold_seconds'`（默认 1.0；表由 child `#1` 建，见 ADR-0011 D3）
- 采集 worker 维护每实例 `last_event_id`（用 Redis key `mysql:slowq:last_event_id:{instance_id}` 做游标）

## API Contract

- `GET /instances/{instance_id}/slow-queries`
  - query: `min_duration_ms?`, `user?`, `schema?`, `digest_prefix?`, `started_after?`, `started_before?`, `limit?` (默认 50、上限 200)
  - response: `{ window: {from, to}, entries: [{event_id, started_at, user, schema_name, sql_text, timer_wait_ms, rows_examined, rows_sent, rows_affected, errors}] }`
  - 默认窗口：最近 15 分钟；Top 50 按 timer_wait_ms 降序
- Permission: 复用 `INSTANCES_READ`

## Web

- `apps/web/app/instances/[instanceId]/slow-queries/page.tsx` 作为 Slow queries 子路由（ADR-0011 D1 子路由模型）
- 表格列：started_at / duration_ms / user / schema / rows_examined / rows_sent / sql_text (截断 + 悬浮全文)
- 顶部筛选：min_duration_ms / user / schema / time window
- 空态 / 前置条件不满足态：PS 未启用时显示"Performance Schema events_statements_history_long 未启用，请在被监控实例设置 performance_schema=ON 并确保 events_statements_history_long_size >= 10000"

## Validation Hook

- 实例 validation 时探测 `@@performance_schema` 与 `events_statements_history_long_size`；探测失败**不**阻塞 validation PASSED，只在 `validation.detail` 里记录并在 web tab 展示提示

## Non-Goals

- 不做 digest 聚合 / percentile / count trend（留到 Slice 5）
- 不解析 slow_log 文件
- 不改被监控实例 `log_output`

## Final Validation Command

```bash
uv run pytest tests/worker_mysql/test_slow_query_collector.py tests/api/runtime/test_mysql_slow_queries.py \
  && pnpm openapi:check \
  && pnpm --filter web typecheck
```
