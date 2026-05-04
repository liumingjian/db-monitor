# ADR-0005: MySQL processlist runtime view flows through ClickHouse, not direct query

Status: accepted (2026-04-22)

MySQL processlist 的展示路径锁为"采集器每 30 秒快照 → ClickHouse 流式表 → API 从 ClickHouse 读"，而不是 lepus 式的"API 直连被监控实例跑 `SHOW PROCESSLIST`"。kill 操作**单独**走实时路径，从实例表读 connection config → 临时连接 → `KILL {process_id}` → 关闭连接，不经过 ClickHouse。这条决策同时确立了后续所有引擎"实时状态视图"的模式：**展示走采集，命令走实时**。OS 的 `ps`、SQLServer 的 `sys.dm_exec_sessions`、Oracle 的 `v$session` 都将沿用此模式。

## Data model

```sql
CREATE TABLE mysql_processlist (
    organization_id String,
    instance_id String,
    collected_at DateTime64(3),
    process_id UInt64,
    user String, host String, db String,
    command LowCardinality(String),
    time_seconds UInt32,
    state LowCardinality(String),
    info String,
    trx_started_at Nullable(DateTime64(3))
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(collected_at)
ORDER BY (instance_id, collected_at, process_id)
TTL collected_at + INTERVAL 7 DAY;
```

- 采集频次：30 秒（运行时可配，不硬编码）
- 覆盖：**全量**，含 `COMMAND='Sleep'`
- 保留：7 天
- API 筛选：user / host / command / min_time；支持按 `collected_at` 切时间片做历史回放

## Considered Options

- **API 直查被监控实例**（lepus 模式）：被拒。DBA 开页数会放大被监控实例压力、无历史回放、MySQL hang 时监控页也 hang、控制面↔被监控实例直连是 ADR-0001 明确作废的耦合模式。
- **混合路径（默认 CH，"立即刷新"按钮同步采集）**：被拒。实现复杂度高于收益；30 秒延迟对 processlist 场景足够。

## Consequences

- 被监控 MySQL 的 processlist 压力恒定（每实例每 30 秒 1 次 query），不随 DBA 页数放大。
- DBA 获得 7 天内任意时刻的 processlist 历史回放能力——lepus 只能靠 `mysql_connected` 分组反推，不精确。
- 被监控实例 hang 时监控页仍显示最后一个快照，是定位问题的关键信息。
- kill 端点必须独立实现实时连接路径；见 ADR-0006。
- 该模式被确立为通用规则，后续 OS/SQLServer/Oracle 的类似视图不需要重新回答数据流问题，直接套用。
- ClickHouse 存储预算：100 实例 × 30s × 平均 50 连接 ≈ 每天 1.4 亿行 × 7 天 ≈ 10 亿行量级；MergeTree 可应付，若后续爆量可加 `COMMAND='Sleep'` 过滤——这是可逆动作。
