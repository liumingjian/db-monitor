# ADR-0007: MySQL slow query data source = performance_schema.events_statements_history_long

Status: accepted (2026-04-22)

切片 1 的 MySQL 慢查询短窗列表的数据源锁为 **`performance_schema.events_statements_history_long`**（worker 增量拉 → ClickHouse），而不是文件解析 slow log、查 `mysql.slow_log` 表、或 API 直连按需查询。采集频次 60 秒，按 EVENT_ID 增量去重；写入 ClickHouse `mysql_slow_query_events`（7 天 TTL；按 `started_at` 分区；保留 digest 字段但切片 1 UI 不展示，留给切片 5 做聚合分析）。阈值 `instance.slow_threshold_seconds` 默认 1 秒，每实例可配；筛选维度 min_duration / user / schema / digest prefix / time range。web 实例 detail 新增 "Slow queries" tab（默认 15 分钟窗口、Top 50）。Permission 复用 `INSTANCES_READ`。

## Schema

```sql
CREATE TABLE mysql_slow_query_events (
    organization_id String,
    instance_id String,
    collected_at DateTime64(3),
    event_id UInt64,
    thread_id UInt64,
    user String, host String, schema_name String,
    digest String,
    digest_text String,
    sql_text String,
    timer_wait_ms Float64,
    rows_examined UInt64, rows_sent UInt64, rows_affected UInt64,
    errors UInt32,
    started_at DateTime64(3)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(started_at)
ORDER BY (instance_id, started_at, event_id)
TTL collected_at + INTERVAL 7 DAY;
```

## Considered Options

- **文件解析 slow log（lepus 模式）**：被拒。需要 SSH/agent 访问被监控实例文件系统，违反 agentless 立场，跨 VPN/IDC 受限。
- **查 `mysql.slow_log` 表（`log_output='TABLE'`）**：被拒。需要改被监控实例敏感配置；CSV engine 写入锁表；生产 DBA 通常不允许。
- **API 按需查 performance_schema（不采集）**：被拒。同 ADR-0005 结论，API 直连被 DBA 页数放大、无历史回放。
- **新开 ClickHouse 表 vs 复用统一 metrics 表**：选前者。慢查询是多维数据（digest / sql_text / rows 等），硬塞进 `(engine, instance, metric_name, value)` 会需要多行多 metric_name 拼回，查询成本高且语义脏。

## Consequences

- 被监控 MySQL 仅需默认 performance_schema 配置，不要求改 `log_output`。未开启 `events_statements_history_long_size` 的实例会在 web 上提示但不阻塞 validation。
- 切片 1 的 schema 是切片 5 深度层（pt-query-digest 等价）的**子集**；切片 5 在同一张表上加 `GROUP BY digest` 聚合 + percentile/count，不返工。
- Performance_schema `events_statements_history_long` 是环形缓冲区，默认 10000 条；极端慢查询爆发（单实例 >166 条/秒）时可能 miss——接受此风险；DBA 可临时调大 `events_statements_history_long_size`，运维提示写入 `operator-*` baseline。
- 采集 worker 需要维护"上次采集到的 max event_id"以做增量；建议存 Redis（per instance key），也可以存实例元数据表；切片 1 实现时再定，都不是 schema-breaking。
- 阈值 `slow_threshold_seconds` 加在 instance 表而非 rule 表（lepus 也是如此）；"什么算慢"是实例属性，"什么算告警"才是规则。
