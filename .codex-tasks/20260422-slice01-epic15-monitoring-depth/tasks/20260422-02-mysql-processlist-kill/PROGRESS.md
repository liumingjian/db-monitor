# Progress

## Summary

- Task shape: single-full
- Goal: MySQL processlist kill 端点 + 新权限 + 审计 + 最小安全网 + scheduler 接入

## Recovery

- 任务: Epic 15 child #2
- 形态: single-full
- 进度: 8/8 CLOSED
- 当前: DONE
- 文件: `.codex-tasks/20260422-slice01-epic15-monitoring-depth/tasks/20260422-02-mysql-processlist-kill/TODO.csv`
- 下一步: 交棒 Epic 15 child #3 (MySQL slow query)

## Reference

- ADR-0006（权限与安全网）
- ADR-0011 D2 审计命名、D3 instance_parameters JSONB 读取
- child #1 的 web tab 与连接路径、ProcesslistWorker / PyMySQLProcesslistCollector

## Notes

- 系统/复制连接保护本 slice 不做，Slice 5 回补
- kill 端点**不复用** INSTANCES_WRITE；新 `Permission.INSTANCES_ACTION`，admin/operator 持有，viewer 不持有
- 监控用户自身保护在 pymysql 同一 session 内 `SELECT USER FROM information_schema.processlist WHERE ID = %s` 预检，规避快照陈旧带来的 race

## Latest Evidence (2026-04-22 Handoff to TODO #7-#8)

### Final validation output

- `uv run pytest tests/api/auth/test_permission_matrix.py -q` → 6 passed
- `uv run pytest tests/api/runtime/test_mysql_processlist_kill.py -q` → 7 passed
- `uv run pytest tests/api/runtime/test_mysql_processlist_kill_safety.py -q` → 3 passed
- `uv run pytest tests/api/audit/test_audit_trail.py -q` → 3 passed
- `uv run pytest tests/worker_mysql/test_processlist_scheduler.py -q` → 8 passed
- `pnpm openapi:check` → snapshot matches (kill endpoint + two new schemas added)
- Full regression `uv run pytest tests/ -q --ignore=tests/integration` → 140 passed

### File changes

- **Modified**
  - `apps/api/src/db_monitor_api/auth/domain.py` — append `Permission.INSTANCES_ACTION`; add it to `admin`/`operator` sets
  - `apps/api/src/db_monitor_api/runtime.py` — add `processlist_kill_service: ProcesslistKillService` field
  - `apps/api/src/db_monitor_api/bootstrap.py` — inject `ProcesslistKiller` + build `ProcesslistKillService`
  - `apps/api/src/db_monitor_api/runtime_views/router.py` — add `POST /instances/{instance_id}/processlist/{process_id}/kill`
  - `apps/api/src/db_monitor_pipeline/process_settings.py` — require `DB_MONITOR_POSTGRES_DSN` for worker-mysql (needed by scheduler)
  - `apps/api/src/db_monitor_pipeline/processes.py` — compose `ProcesslistScheduler` into `WorkerProcess.run_once()`; `_combine_worker_results()` aggregates queue + processlist cycles
  - `packages/api-client/src/index.ts` — add `KillProcesslistRequest`/`KillProcesslistResponse` types + `killProcess()` method; bump `API_CONTRACT_VERSION` 0.10.0 → 0.11.0
  - `contracts/openapi.snapshot.json` — regenerated (adds kill endpoint + schemas)
  - `tests/api/auth/test_auth_contract.py`, `tests/api/auth/test_auth_session.py` — extend expected permission arrays for new enum value
  - `tests/operations/processes/test_processes.py` — inject `DB_MONITOR_POSTGRES_DSN` into env fixture
- **Added**
  - `apps/api/src/db_monitor_api/runtime_views/kill.py` — `ProcesslistKiller` Protocol, `PyMySQLProcesslistKiller`, `ProcesslistKillService`, `ProcesslistKillBlocked` / `ProcesslistKillFailed` errors
  - `apps/api/src/db_monitor_pipeline/processlist_scheduler.py` — `ProcesslistScheduler` + `reduce_cycle_to_run_result()` aggregator
  - `tests/api/auth/test_permission_matrix.py` — permission matrix assertions for `INSTANCES_ACTION`
  - `tests/api/runtime/test_mysql_processlist_kill.py` — happy path, RBAC (admin/operator/viewer), 401, 404, 502 failure surfacing
  - `tests/api/runtime/test_mysql_processlist_kill_safety.py` — validation≠PASSED block, monitor-user block, failure-audit invariant
  - `tests/api/audit/test_audit_trail.py` — audit `instances.process.kill` success + failure + permission-denied path
  - `tests/api/audit/__init__.py`
  - `tests/worker_mysql/test_processlist_scheduler.py` — scheduling interval, default cadence, failure surfacing, min-floor enforcement, non-MySQL/non-PASSED skipping

### Handoff facts for TODO #7-#8 subagent

- **Typed client signature** (already shipped on `ApiClient`):

  ```ts
  killProcess(
    instanceId: string,
    processId: number,
    request?: KillProcesslistRequest,   // { reason?: string }
  ): Promise<KillProcesslistResponse>;  // { checked_at, killed, notes }
  ```

- **Endpoint**: `POST /instances/{instance_id}/processlist/{process_id}/kill`
  - 200 → `{ checked_at: ISO, killed: true, notes: null }`
  - 401 → missing session cookie
  - 403 → `{ detail: "Missing permission: instances:action" }`
  - 404 → unknown instance
  - 409 → safety net block (validation≠PASSED **or** target is monitor user)
  - 502 → pymysql / driver failure, detail carries root cause

- **RBAC visibility for UI**: show the Kill button iff `permissions.includes("instances:action")`. Admin/operator: yes. Viewer: hide entirely (not just disable).

- **Safety-net disabled-state for UI** (double insurance per SPEC):
  - `instance.validation.status !== "passed"` → disabled, tooltip: "实例验证未通过，无法 kill"
  - Target entry's `user === instance.connection.username` → disabled, tooltip: "监控用户自身连接不可 kill"
  - These are also enforced server-side (409), but frontend must preempt to avoid pointless 409s.

- **Confirmation dialog**: required per SPEC. Mandatory `reason` field in the UI; pass it as `{ reason }` body to `killProcess`. Note: server currently does not persist `reason` in audit (no `detail` column); the dialog input still matters for UX and for future audit.details extension — do not drop it.

- **Audit resource convention**: `instance:<instance_id>:process:<process_id>` — if TODO #8 smoke asserts audit entries, match this shape.

- **Scheduler wiring landing**: `apps/worker-mysql` main loop composes `ProcesslistScheduler` via `build_worker_process()`. Worker env now **requires** `DB_MONITOR_POSTGRES_DSN`. If TODO #8 smoke bootstraps worker-mysql in docker-compose, verify the env is set (already provided by `dev-up.ps1` style orchestration).

- **Files to touch for web (TODO #7)**:
  - `apps/web/app/instances/[instanceId]/processes/page.tsx` (or the child table)
  - `apps/web/src/processlist-ui.ts` (table row action rendering)
  - `apps/web/src/data-layer.ts` (delegate to `apiClient.killProcess`)
  - `apps/web/tests/processlist-ui.test.ts` (extend coverage)

- **Preexisting, unrelated failing test**: `tests/integration/control_plane/test_control_plane_postgres.py::test_postgres_repository_persists_multi_engine_instances_and_settings` errors with `DependentObjectsStillExist` on `instance_parameters` FK. Confirmed also failing on clean `main` branch (pre-our-work). Out of scope for this child.

## Latest Evidence (2026-04-22 TODO #7 + #8 close-out)

### Final validation output

- `pnpm --filter web typecheck` → 0 errors
- `pnpm --filter web test` → 12 files / 37 tests passed (processlist-ui.test.ts: 17 tests incl. 6 new for kill safety-net, 2 for permission gating, 3 for status code mapping)
- `pnpm smoke:web` → Playwright phase-one.spec.ts 1 passed (Processes tab loads under admin session; no stray enabled Kill button leaks into empty-snapshot DOM)

### File changes (TODO #7-#8 web only; no backend / api-client / OpenAPI touched)

- **Modified**
  - `apps/web/app/instances/[instanceId]/processes/page.tsx` — fetch `apiClient.me()` for permissions, pass `canKill` / `instanceId` / `monitorUsername` / `validationPassed` into ProcesslistTable
  - `apps/web/app/instances/[instanceId]/_components/processlist-table.tsx` — adds Actions column + Kill button rendering gated by `canKill`; renders safety-net disabled state per row (validation / monitor-user)
  - `apps/web/src/processlist-ui.ts` — adds `KILL_PERMISSION`, `KILL_BLOCK_*` messages, `KillRowState`, `resolveKillRowState()`, `hasKillPermission()`, `KillProcessErrorCode`, `KILL_ERROR_FALLBACK`, `mapKillStatusToCode()` — all pure
  - `apps/web/tests/processlist-ui.test.ts` — extends to 17 tests covering kill safety net, permission gating, HTTP status → UX code mapping
  - `smoke/phase-one.spec.ts` — asserts Processes tab empty-state path does not leak enabled Kill controls
- **Added**
  - `apps/web/app/instances/[instanceId]/_components/kill-process-dialog.tsx` — client component, native `<dialog>` with required reason textarea, `useActionState` server-action driver, surfaces success/error banner
  - `apps/web/app/instances/[instanceId]/_components/kill-process-action.ts` — `"use server"` action; fetches backend directly with cookie forwarding to preserve HTTP status semantics (api-client's `request()` only throws on !ok with body text, loses status code); translates 401/403/404/409/502 into user-facing Chinese messages; revalidates processes path on success

### Handoff facts for Epic 15 child #3

- `SessionUser.permissions` is the authoritative RBAC source; `hasKillPermission()` is the only web-side gate — no duplicate render + disable.
- Kill safety-net is double-enforced: backend returns 409 for validation≠passed or monitor-user target; web preempts via `resolveKillRowState()` returning `disabled + reason` to avoid pointless 409 roundtrips.
- API client's `request()` throws `new Error(await response.text())` on !ok → **status code is lost**. TODO #7 chose to implement the kill action as a direct `fetch` in the server action instead of extending api-client (guardrail: do not modify api-client). Future similar slow-query action endpoints can reuse the `mapKillStatusToCode`-style pure helper pattern or, cleaner, ask backend team to add a status-preserving error type to api-client (out of scope for this child).
- Smoke fixture in `apps/api/src/db_monitor_api/smoke_main.py` seeds zero processlist entries, so Playwright asserts empty-state path. True end-to-end kill UX has to be exercised manually against a seeded fixture or in `webapp-testing` skill run; child #3 inherits this limitation.
