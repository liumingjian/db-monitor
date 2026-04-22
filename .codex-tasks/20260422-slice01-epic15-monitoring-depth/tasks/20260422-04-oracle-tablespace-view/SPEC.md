# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 Oracle 实例的 tablespace 使用率成为可采、可看、可回溯的运维面：采集 `dba_tablespace_usage_metrics` → ClickHouse 专表 → API → web 实例 detail 新增 Tablespaces tab + 24h mini-sparkline + 30d 全屏图

## Key Decisions (Inputs)

- `docs/adr/0008-multi-dimensional-metrics-dedicated-tables.md`
- `CONTEXT.md` Slice 1 scope 第 4 条

## Schema

- 新 ClickHouse 表 `oracle_tablespaces`（列见 CONTEXT.md / ADR-0008；TTL 30 天；`ORDER BY (instance_id, collected_at, tablespace_name)`）
- 采集频次 300 秒（5 分钟）；不与 processlist / slow query 同频

## Collector Query

```sql
SELECT
    tablespace_name,
    used_space    AS used_blocks,
    tablespace_size AS total_blocks,
    used_percent   AS used_rate_percent,
    status
FROM dba_tablespace_usage_metrics m
JOIN dba_tablespaces t USING (tablespace_name)
```

（Oracle 的 `used_space`/`tablespace_size` 单位是 block；按 `SELECT block_size FROM dba_tablespaces` 或 `SELECT value FROM v$parameter WHERE name='db_block_size'` 归一到 bytes；autoextend 的 datafile 已经被 `tablespace_size` 包含）

## API Contract

- `GET /instances/{instance_id}/tablespaces`
  - 默认返回最新一次采集；支持 `collected_after?`/`collected_before?` 历史回放
  - response: `{ snapshot_at, entries: [{tablespace_name, status, used_bytes, total_bytes, used_rate_percent, autoextensible}] }`
- `GET /instances/{instance_id}/tablespaces/{tablespace_name}/history`
  - query: `from`, `to`（最长 30 天）
  - response: `{ entries: [{collected_at, used_bytes, total_bytes, used_rate_percent}] }`
- Permission: 复用 `INSTANCES_READ`

## Web

- `apps/web/app/instances/[instanceId]/tablespaces/page.tsx` 作为 Tablespaces 子路由（ADR-0011 D1 子路由模型）；`layout.tsx` 中 tab 入口按 `instance.engine==oracle` 条件渲染
- 列表：tablespace_name / status / used / total / used_rate%（带颜色条，>=85% 黄，>=95% 红） / 24h sparkline
- 默认按 used_rate_percent 降序
- 点 tablespace 行 → 跳"30 天趋势"全屏图（ECharts area + 95% 阈值线）

## Non-Goals

- 不做 datafile 明细（留到 Slice 6）
- 不做 tablespace 告警规则（留到 Slice 2，需要 rule schema 扩 label_selector）
- 不做 AWR、历史容量预测、session 深度（留到 Slice 6）

## Final Validation Command

```bash
uv run pytest tests/worker_oracle/test_tablespace_collector.py tests/api/runtime/test_oracle_tablespaces.py \
  && pnpm openapi:check \
  && pnpm --filter web typecheck
```
