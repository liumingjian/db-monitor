# Progress

## Summary

- Task shape: single-full
- Goal: MySQL processlist 采集 → ClickHouse mysql_processlist → list API → web Processes tab

## Recovery

- 任务: Epic 15 child #1
- 形态: single-full
- 进度: 6/6 DONE
- 当前: CLOSED
- 文件: `.codex-tasks/20260422-slice01-epic15-monitoring-depth/tasks/20260422-01-mysql-processlist-list/TODO.csv`
- 下一步: Epic 15 child #2（kill 端点 + UI）启动

## Reference

- ADR-0005（数据流）
- ADR-0008（多维指标专表规则）
- lepus-v3.8/web/application/controllers/lp_mysql.php（`process` action 仅作领域参考，不复用代码）

## Notes

- 本任务的 child #2（kill）会复用这里的实例连接路径和 web tab 结构；child #2 必须在 child #1 完成后再动工

## Latest Evidence (2026-04-22 subagent 1)

### Validation Runs

| TODO | 命令 | 结果 |
| --- | --- | --- |
| #1 | `pnpm test:schema:bootstrap` (`gates/schema/test_schema_bootstrap_live.py`) + `pytest tests/schema/test_clickhouse_schema.py` | 1 + 2 passed |
| #2 | `pytest tests/worker_mysql/test_processlist_collector.py` | 9 passed |
| #3 | `pytest tests/api/runtime/test_mysql_processlist.py` | 8 passed |
| #4 | `pnpm openapi:check` | snapshot matches |

Regression sweep over `tests/api tests/schema tests/worker_mysql`: 65 passed.

### Changed Files

- `apps/api/src/db_monitor_schema/contract.py` — PG version 8→9, CH version 2→3
- `apps/api/src/db_monitor_schema/clickhouse.py` — add `mysql_processlist` DDL + include in required tables
- `apps/api/src/db_monitor_schema/postgres.py` — add `instance_parameters` JSONB table + required tables tuple
- `apps/api/src/db_monitor_pipeline/sink.py` — add `CLICKHOUSE_MYSQL_PROCESSLIST_TABLE`, `write_processlist`, in-memory dual-sink
- `apps/api/src/db_monitor_pipeline/processlist.py` **(new)** — `ProcesslistEntry/Snapshot/Worker`, `PyMySQLProcesslistCollector`, `resolve_processlist_interval_seconds` (default 30, min 10)
- `apps/api/src/db_monitor_api/control_plane/instance_parameters.py` **(new)** — `InstanceParameterRepository` Protocol + InMemory + Postgres impls (generic JSONB reader; child #3/#4 can reuse)
- `apps/api/src/db_monitor_api/runtime_views/` **(new package)** — `domain.py`/`repository.py`/`service.py`/`router.py`; mounts `GET /instances/{instance_id}/processlist` with `Permission.INSTANCES_READ`
- `apps/api/src/db_monitor_api/runtime.py` — add `processlist_service: ProcesslistService`
- `apps/api/src/db_monitor_api/bootstrap.py` — inject processlist repository/service; seed users extracted to `auth/seed_users.py` to respect 300 line limit
- `apps/api/src/db_monitor_api/auth/seed_users.py` **(new)** — extracted `default_seed_users()`
- `apps/api/src/db_monitor_api/app.py` — register `build_runtime_router()`
- `gates/schema/test_schema_bootstrap_live.py` — drop new tables (`instance_parameters`, `mysql_processlist`) during reset
- `tests/schema/test_schema_bootstrap.py` — new CH DDL assertions + updated PG required table list
- `tests/schema/test_clickhouse_schema.py` **(new)** — per-TODO CH schema assertions
- `tests/worker_mysql/test_processlist_collector.py` **(new)** — collector/worker/sink/interval resolver suite
- `tests/api/runtime/test_mysql_processlist.py` **(new)** — FastAPI contract suite (8 cases)
- `contracts/openapi.snapshot.json` — +238 lines, pure additive (processlist endpoint + schemas)
- `packages/api-client/src/index.ts` — `ProcesslistEntryResponse`, `ProcesslistSnapshotResponse`, `ListProcesslistFilters`, `getInstanceProcesslist`

### Handoff to Subagent 2 (TODO #5 + #6)

1. **Runtime package name**: Boss 的 prompt 指定 "新建 `runtime/` 包"，但 `apps/api/src/db_monitor_api/runtime.py` 已是 `AppRuntime` 的模块（会发生 package-vs-module 冲突）。采用 `runtime_views/` 命名；child #2/#3/#4 后续继续扩本包（processlist kill / slow queries / tablespaces）。
2. **Instance parameter pattern**: `control_plane/instance_parameters.py` 的 `InstanceParameterRepository` 是**通用 JSONB bag reader**；child #3 的 `slow_threshold_seconds`、future OS/SNMP 参数直接复用。读路径规则：缺行 / 缺键 → 返回 `{}`；API 层显式套默认值（ADR-0011 D3）。**写路径尚未建立**（upsert + audit `instances.parameters.upsert`），由第一个需要 UI/API 修改参数的 child（大概率 child #2 或 slice 2）承担；当前对 child #1 只读展示链路足够。
3. **OpenAPI snapshot current state**: `pnpm openapi:check` 绿；新增端点 `GET /instances/{instance_id}/processlist` + 3 个 schema（ProcesslistEntryResponse / ProcesslistSnapshotResponse / HTTPValidationError 扩展若有）。TypeScript client：`createApiClient(...).getInstanceProcesslist(id, filters)` 已可直接调用。
4. **Web tab 尚未建**: `apps/web/app/instances/[instanceId]/` 目前是单 SSR `page.tsx`，**没有** `layout.tsx`；ADR-0011 D1 要求 subagent 2 顺带建 `layout.tsx`（客户端 tab 条）+ `processes/page.tsx`（Processes tab）。API 已就绪，使用 TanStack Query + `@db-monitor/api-client` 的 `getInstanceProcesslist`。
5. **Smoke 路由**: `apps/web/tests/smoke.test.ts::buildSmokeRouteSet()` 要追加 `/instances/:id/processes`，scenario 见 TODO #6 的 notes。smoke 运行入口 `pnpm smoke:web`。
6. **Scheduler 调度未接入**: 本轮未把 `ProcesslistWorker.collect_once` 接到实际 scheduler / Redis queue（`apps/api/src/db_monitor_pipeline/scheduler.py` 和 `apps/worker-mysql` 的 entrypoint 保持不动），仅通过单测验证能力单元。真实数据写入 `mysql_processlist` 的调度链路是后续工作；UI 可在空态下验证"尚未采集"路径（`snapshot_at: null` + `entries: []` 渲染）。subagent 2 不必补这一层，可作为 child #6 smoke 结束后给 Boss 的遗留清单项。
7. **Schema version bump 已完成**: PG 8→9, CH 2→3；任何依赖 `POSTGRES_SCHEMA_VERSION` / `CLICKHOUSE_SCHEMA_VERSION` 常量的下游不需要改，但跨环境部署需要重跑 `bootstrap-runtime`。
8. **Boundary 未触碰项**: 未改 `Permission` 枚举、未改 `alert_rules`、未动 notifier、未动 `INSTANCES_WRITE` 语义、未改现有 `/control/instances` 端点 schema、未新增 docker-compose 服务。

## Latest Evidence (2026-04-22 subagent 2)

### Validation Runs

| TODO | 命令 | 结果 |
| --- | --- | --- |
| #5 | `pnpm --filter web typecheck` | 0 errors |
| #5 | `pnpm --filter web test` | 12 files / 28 tests passed (+8 new in `tests/processlist-ui.test.ts`) |
| #6 | `pnpm smoke:web` | Playwright `phase-one.spec.ts` 1 passed (2.0s); next build 列出新路由 `/instances/[instanceId]/processes` |

### Changed Files

- `apps/web/src/processlist-ui.ts` **(new)** — `buildProcesslistFilterValues` / `toProcesslistApiFilters` / `buildProcesslistViewModel`，三档空态判定（validation / no-snapshot / no-match），limit clamp 至 `PROCESSLIST_MAX_LIMIT=500`
- `apps/web/src/components/instance-tab-nav.tsx` **(new)** — `"use client"` tab 栏，基于 `usePathname()` 激活 Overview/Processes，纯 Link（ADR-0011 D1 子路由模型，无 useState Tabs）
- `apps/web/app/instances/[instanceId]/layout.tsx` **(new)** — SSR layout，承载 `AppChrome` + `InstanceTabNav`
- `apps/web/app/instances/[instanceId]/processes/page.tsx` **(new)** — Server Component；`createServerApiClient().getInstanceProcesslist()` + `getInstance()` 并发前拉，SSR 渲染筛选 form、表格、空态
- `apps/web/app/instances/[instanceId]/_components/processlist-filter-form.tsx` **(new)** — 原生 HTML form GET，字段 user/host/command/minTimeSeconds/collectedAfter/collectedBefore
- `apps/web/app/instances/[instanceId]/_components/processlist-table.tsx` **(new)** — 8 列（PID/User/Host/DB/Command/Time/State/Info）；Info 单元格用原生 `<details>` 悬浮展开 full sql（无 Tooltip 库）
- `apps/web/app/instances/[instanceId]/_components/processlist-empty-state.tsx` **(new)** — 空态 banner
- `apps/web/app/instances/[instanceId]/page.tsx` — 去掉 `AppChrome` 包裹（已由 layout 接管），其余业务渲染 model 完全不变
- `apps/web/src/monitoring-ui.ts` — `buildSmokeRouteSet()` 追加 `/instances/inst-prod-primary/processes`
- `apps/web/tests/smoke.test.ts` — 断言新增路由
- `apps/web/tests/processlist-ui.test.ts` **(new)** — 8 cases 覆盖过滤归一化、limit clamp、三档空态
- `smoke/phase-one.spec.ts` — Processes tab 场景：点 tab → URL → 填 User=root → Apply filters → 校验 URL 与表单回显
- `.codex-tasks/20260422-slice01-epic15-monitoring-depth/tasks/20260422-01-mysql-processlist-list/TODO.csv` — #5/#6 → DONE
- `.codex-tasks/20260422-slice01-epic15-monitoring-depth/SUBTASKS.csv` — #1 → DONE，#2 → READY
- `.codex-tasks/20260422-slice01-epic15-monitoring-depth/PROGRESS.md` — 进度 1/6，下一 child #2

### Handoff Notes

- Scheduler 集成未接入（subagent 1 遗留），smoke 走 InMemoryProcesslistRepository 空快照路径，UI 渲染"尚未采集"成立；真实采集链路接入仍是独立决策项
- `apps/web/src/monitoring-ui.ts` 文件已 1072 行（历史债），processlist UI 故意落在新独立文件 `processlist-ui.ts`，未让 monitoring-ui.ts 继续膨胀
- 未改 api-client、OpenAPI snapshot、后端任何文件；未引 shadcn/react-hook-form/zod/新 UI 库；未改 `apps/web/app/instances/page.tsx`
- Child #2 需要在 Processes 表格新增 kill 按钮（UI 层已有行结构可复用），后端 kill 端点仍需新建
