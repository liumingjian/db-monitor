# Progress

## Summary

- Task shape: epic
- Goal: 让 MySQL 与 Oracle 的产品级监控深度（processlist、slow query 短窗、tablespace、per-instance 阈值）落地，成为 DBA 能用 db-monitor 替代 lepus 做日常排障的工程基线

## Recovery

- 任务: Slice 1 / Epic 15 — Monitoring Depth & Rule Granularity
- 形态: epic
- 进度: 2/6
- 当前: child #3 待启动 (MySQL slow query)
- 文件: `.codex-tasks/20260422-slice01-epic15-monitoring-depth/SUBTASKS.csv`
- 下一步: 实施 child `#3`（`tasks/20260422-03-mysql-slow-query-shortwindow/SPEC.md`；独立于 child #1/#2）

## Control Contract

- Primary Setpoint: 让 DBA 的日常排障工作流能从 lepus 迁移到 db-monitor（监控面 ready，通知面由 Epic 16 补齐）
- Acceptance: 6 child 全部 DONE；`pnpm test:hardening:signoff` 绿；新 schema 在 `test:schema:bootstrap` 下成立；新 smoke 覆盖 4 个新 UI 面
- Guardrails: 不写 Notifier 调用（留给 Epic 16）；不压垮被监控实例（processlist 频次 >= 30s）；不复用 `INSTANCES_WRITE` 做 kill；不静默吞采集失败
- Sampling Plan: `#1→#2`（同族）；`#3/#4/#5` 并行；`#6` 最后 signoff
- Constraints: 只有 `SUBTASKS.csv` 中列出的 child 能进入实现；未进入 IN_PROGRESS 的 child 不允许提前写生产实现

## Reference Inputs

- `CONTEXT.md` — slice 1 scope、execution order、per-instance override 决议
- `docs/adr/0001-lepus-parity-pivot.md` — PRD 作废 + Option A/B
- `docs/adr/0002-slice-sequence-and-engine-scope.md` — 8 切片序列 + 永不复刻
- `docs/adr/0003-slice1-monitoring-before-notification.md` — 监控先通知后
- `docs/adr/0004-per-instance-threshold-overrides.md` — overrides schema
- `docs/adr/0005-mysql-runtime-inspection-data-flow.md` — processlist 采集→CH + kill 实时
- `docs/adr/0006-runtime-action-permission-and-safety.md` — INSTANCES_ACTION + 最小安全网
- `docs/adr/0007-mysql-slow-query-data-source.md` — PS 增量采集
- `docs/adr/0008-multi-dimensional-metrics-dedicated-tables.md` — 多维指标专表规则
- `lepus-v3.8/check_mysql.py`、`lepus-v3.8/check_oracle.py`、`lepus-v3.8/web/application/controllers/lp_mysql.php`、`lepus-v3.8/web/application/controllers/lp_oracle.php` — 领域参考（不复用代码/schema）

## Latest Evidence

- 2026-04-22 Epic 激活：`SUBTASKS.csv` 创建，child `#1` 标记 IN_PROGRESS；其余 `#2-#6` PENDING
- 2026-04-22 Pre-flight 审计闭环：3 路 Explore subagent（采集层 / 控制面 / 前端 + schema + gates）+ 1 路 targeted probe（rule-engine 评估路径）完成，结论落 `docs/adr/0011-slice1-epic15-preflight-decisions.md`（accepted）——锁 D1 子路由 tab / D2 audit 命名 `<resource_plural>.<sub>.<verb>` / D3 `instance_parameters` JSONB 载体 / D5 acceptance 换口径（取代原 p95≤10% 硬边界，因无 baseline 不可验证）；EPIC.md / SUBTASKS.csv / child `#1`/#2/#3/#4/#5 SPEC 与 TODO 同步更新；child `#1` 解冻，可进入 TODO `#1`（`mysql_processlist` DDL + `instance_parameters` 表 migration）
- 2026-04-22 child #1 CLOSED (6/6 TODOs DONE)：subagent 1 完成 schema / collector / API / OpenAPI snapshot（96 后端测试绿）；subagent 2 完成 web Processes tab（SSR 子路由 `app/instances/[instanceId]/layout.tsx` + `processes/page.tsx`、独立模型 `src/processlist-ui.ts`、8 列 + details info 悬浮、三档空态、筛选走 URL query）+ smoke (`pnpm smoke:web` 1 passed)；`pnpm --filter web typecheck` 0 errors；`pnpm --filter web test` 28/28；遗留：scheduler 集成未接入（真实采集链路独立决策项）
- 2026-04-22 child #2 CLOSED (8/8 TODOs DONE)：subagent A 完成 backend：Permission.INSTANCES_ACTION、POST `/instances/{instance_id}/processlist/{process_id}/kill` 端点 + `ProcesslistKillService` + `PyMySQLProcesslistKiller` + 审计 `instances.process.kill` + 双保险 safety net（validation + monitor user）+ scheduler 接入（`ProcesslistScheduler` 纳入 `WorkerProcess.run_once()`，`DB_MONITOR_POSTGRES_DSN` 列为 worker 必选环境）+ OpenAPI snapshot 升 `0.11.0`；后端 140 tests 绿。subagent B 完成 web：`_components/kill-process-dialog.tsx`（client 组件，原生 `<dialog>` + React 19 `useActionState`）+ `kill-process-action.ts`（server action，直 fetch 保留 HTTP 状态码，翻译 401/403/404/409/502 → 中文 UX）+ `processlist-table.tsx` 新增 Actions 列（RBAC 渲染 + 双保险 disabled state）+ `processes/page.tsx` 拉 `apiClient.me()` 取 permissions + `src/processlist-ui.ts` 扩 pure helpers（`resolveKillRowState` / `hasKillPermission` / `mapKillStatusToCode` / `KILL_ERROR_FALLBACK`）+ `tests/processlist-ui.test.ts` 覆盖到 17 tests；`pnpm --filter web typecheck` 0 errors；`pnpm --filter web test` 37/37；`pnpm smoke:web` 1 passed（Playwright phase-one.spec.ts 追加了"Processes tab 空态下不泄漏 enabled Kill 按钮"断言）。scheduler 集成由 child #2 顺带落地（child #1 遗留项 closed）。

## Notes

- Epic 16 骨架已预先 materialize 在 `.codex-tasks/20260422-slice01-epic16-notifier-reality/`，但保持 `planned`；Epic 15 关闭后再激活
- 本 Epic 结束不等于 Slice 1 关闭——切片 1 的真实演练 signoff 由 Epic 16 child `#5` 承接
