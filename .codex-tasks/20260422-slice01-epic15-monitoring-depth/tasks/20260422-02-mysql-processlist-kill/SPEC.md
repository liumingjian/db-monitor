# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 MySQL processlist 补齐 kill 端点：从 web 上对某个 process_id 发起 kill 请求，走新权限 `Permission.INSTANCES_ACTION`，审计 `instances.process.kill`，带最小安全网（不允许 kill 监控用户自身、validation 失败的实例禁用按钮）

## Key Decisions (Inputs)

- `docs/adr/0006-runtime-action-permission-and-safety.md`

## API Contract

- `POST /instances/{instance_id}/processlist/{process_id}/kill`
- Request body: 可选 `{ reason?: string }`
- Response: `{ killed: bool, checked_at, notes?: string }`
- Permission: `INSTANCES_ACTION`（新增枚举）
- 成功：审计 action `instances.process.kill`，outcome `success`，resource 含 instance_id + process_id
- 失败：4xx 返回明确错误（connection failed / permission denied / blocked by safety net）；审计 outcome `failure`

## Safety Net (minimal for slice 1)

- 禁止 kill 监控用户（从 instance.connection.username）自身建立的连接
- 实例 `validation_status != PASSED` 时前端按钮禁用，后端也拒绝（双保险）
- 系统/复制连接保护**不做**本 slice（ADR-0006 已注明推到 Slice 5）

## Connection Strategy

- 不经过 ClickHouse；从 PostgreSQL `control_mysql_instances` 读取连接 config，临时 `pymysql.connect` → `cursor.execute("KILL %s", (process_id,))` → close
- 超时 5 秒；失败明确上抛

## Web

- Processes tab 每行增加 `Kill` 按钮（admin/operator 可见；viewer 不可见）
- 点击弹确认框，必填 reason（传给审计）
- 按钮在 validation!=PASSED 或该连接是监控用户自身时禁用 + 提示

## Permission Matrix Update

- `Permission` 枚举新增 `INSTANCES_ACTION`
- 默认角色矩阵：admin, operator 持有；viewer 不持有
- 迁移路径：无现存用户受影响（纯新权限）

## Scheduler Integration（Boss 2026-04-22 G1=a 决议，child #1 遗留）

- child #1 落地了 `ProcesslistWorker.collect_once()` / `PyMySQLProcesslistCollector` / `ClickHouseMetricSink.write_processlist()` 但**未挂调度**，`mysql_processlist` 表无真实数据源
- 本 child 顺带接入：
  - 在 `apps/worker-mysql/` 调度循环（或 `apps/api/src/db_monitor_pipeline/` 的 scheduler 注册表）里注入 processlist 采集周期
  - 采集间隔从 `instance_parameters.parameters->>'processlist_interval_seconds'` 读（ADR-0011 D3；subagent 1 已落 reader；缺行/缺键套 30s 默认、下限 10s）
  - 失败必须显式：采集失败走现有 `WorkerRunResult(error=..., status="failed")` JSON 日志，**禁止静默吞**（EPIC Control Contract Guardrail）
  - 复用已有 pymysql 连接路径；**注意与 kill 端点共用连接管理函数的机会**（同一 instance 的 processlist 采集和 kill 可共享临时连接工厂，不需各自 new）

## Non-Goals

- 不做 bulk kill
- 不做基于状态/user pattern 的批量筛选 kill
- 不保护 binlog dump / replication channel / system threads（留到 Slice 5）
- 不做 processlist 采集间隔的 UI 编辑入口（`instance_parameters` 写路径由后续 child 承接，Boss 2026-04-22 G2 延后决议）

## Final Validation Command

```bash
uv run pytest tests/api/runtime/test_mysql_processlist_kill.py tests/api/auth/test_permission_matrix.py \
  && pnpm openapi:check \
  && pnpm --filter web typecheck
```
