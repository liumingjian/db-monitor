# ADR-0008: Multi-dimensional metrics go to dedicated ClickHouse tables, not the unified metrics table

Status: accepted (2026-04-22)

统一 `metrics` 表（`(engine, instance_id, metric_name, metric_value, collected_at)`）只承载"每实例每时间一个标量值"的指标。任何一次采集产生 N 条维度行的指标（Oracle tablespace per tablespace_name、OS disk per partition、OS net per interface、SQLServer per database、Redis per keyspace 等）必须开**专表**，schema 里包含该维度 key 作为 `ORDER BY` 组件。第一个专表是切片 1 的 `oracle_tablespaces`；后续 OS/SQLServer 将套用。

## Why not stuff multi-dim into the unified table

- **编码 metric_name**（如 `oracle_tablespace_used_rate.USERS`）：查询时要字符串反解 → 聚合脏、查询不 sargable、UI 侧要维护编解码对
- **扩 labels Map 字段**（`labels Map(String, String)`）：需要改所有现有指标写入路径；已有 MySQL throughput/qps/threads 等单值指标的写入代码要同步改；且 ClickHouse Map 类型查询有 known 性能坑
- **专表**：schema 清晰、TTL 可按维度独立定（多维指标往往做"月级容量趋势"，TTL 30 天；单值 TTL 7 天即可）、查询 sargable；代价是跨维度 JOIN 聚合（"CPU top 10 + 磁盘 top 10 联合排序"）做不了——接受此代价，极少场景需要

## Concrete rule

新增维度指标时遵循：

1. 如果一次采集只产出单实例单时间一个数字（如 `threads_connected`、`qps`、`replication_lag_seconds`）→ 写入统一 `metrics` 表，`metric_name` 一个字符串常量
2. 如果一次采集产出多条维度行（如 `oracle_tablespaces` 表里 USERS / SYSTEM / SYSAUX 各一行）→ 开专表，维度 key 进 `ORDER BY` 和 `PARTITION BY`（如果需要）
3. 专表命名规则：`<engine>_<concept_plural>`（`oracle_tablespaces`、`os_disks`、`sqlserver_databases`）
4. 专表默认 TTL 30 天；若后续证明需要更长，单个 ADR 调整

## Considered Options

- **统一 metrics 表 + metric_name 编码维度**：被拒，见上
- **统一 metrics 表 + labels Map 扩展**：被拒，见上
- **每个维度独立成统一 metrics 表的行，维度 key 塞进 instance_id 字段**：被拒，语义扭曲严重

## Consequences

- 每加一类多维指标要开新 ClickHouse 表和对应 analytics query 层代码。成本略高于统一表扩列，但隔离性强、返工风险低。
- `metrics` 表保持轻量；后续引擎单值指标继续走它，不污染。
- API 层的 analytics service 需要路由到对应表；建议按 "core metrics service"（查统一 metrics 表）+ "tablespace/disk/database/... dedicated service"（查专表）分层，不强行 union。
- web 面对应"多维指标"就是"列表 + 排序 + trend per 维度 key"这个模式，可以沉淀为通用 UI 组件（切片 3 OS 再做时可以复用）。
