# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 db-monitor 能以采集-展示模式承载 MySQL processlist：worker 按 30 秒快照 `SHOW PROCESSLIST` 写入 ClickHouse 专表；控制面提供 list API 支持筛选 + 历史回放；web 实例 detail 新增 Processes tab

## Key Decisions (Inputs)

- `docs/adr/0005-mysql-runtime-inspection-data-flow.md`
- `docs/adr/0008-multi-dimensional-metrics-dedicated-tables.md`

## Schema

- 新 ClickHouse 表 `mysql_processlist`（列与 TTL 见 ADR-0005）
- 采集频次通过新表 `instance_parameters` JSONB 载体存取：`parameters->>'processlist_interval_seconds'`（默认 30，下限 10；见 ADR-0011 D3）；collector 读不到该键时套默认值
- 新表 `instance_parameters` 的 DDL 与 migration 挂在本 child，供 child `#3` 复用

## API Contract

- `GET /instances/{instance_id}/processlist`
  - query: `user?`, `host?`, `command?`, `min_time_seconds?`, `collected_after?`, `collected_before?`, `limit?` (默认 200、上限 500)
  - response: `{snapshot_at, entries: [{process_id, user, host, db, command, time_seconds, state, info, trx_started_at}]}`
  - 默认返回最新一次快照；支持时间范围窗口回放
- Permission: 复用 `INSTANCES_READ`

## Web

- `apps/web/app/instances/[instanceId]/processes/page.tsx` 作为 Processes 子路由（ADR-0011 D1 子路由模型）；若 `layout.tsx` 尚未承载 tab 栏，本 child 顺带创建
- 表格列：process_id / user / host / db / command / time(s) / state / info (单元格悬浮展开 full sql)
- 顶部筛选：user / host / command 下拉 + min_time 输入 + 时间窗口选择
- 空态：实例 validation!=PASSED 时显示提示；最新快照为空时显示"尚未采集"

## Non-Goals

- 不实现 kill 端点（child `#2`）
- 不做 processlist 级告警
- 不过滤 `COMMAND='Sleep'`（全量采集是 ADR-0005 明定范围）

## Final Validation Command

```bash
uv run pytest tests/worker_mysql/test_processlist_collector.py tests/api/runtime/test_mysql_processlist.py \
  && pnpm openapi:check \
  && pnpm --filter web typecheck
```
