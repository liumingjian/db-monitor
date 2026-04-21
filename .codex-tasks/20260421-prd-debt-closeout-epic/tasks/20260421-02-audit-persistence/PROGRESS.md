# Progress

## Summary

- Task shape: single-full
- Goal: 让审计日志成为 PostgreSQL 持久化、可查询的正式产品能力

## Recovery

- 任务: child `#2` 已完成，审计日志已进入 PostgreSQL 持久化与最小查询面
- 形态: single-full
- 进度: 4/4
- 当前: 已关闭，等待 parent epic 切换到 child `#3`
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/tasks/20260421-02-audit-persistence/TODO.csv`
- 下一步: 把剩余控制误差转移到 child `#3` 的用户/角色管理产品面

## Control Contract

- Primary Setpoint: 审计日志不再停留在 `InMemoryAuditRepository` 运行时 seam，而是进入 PostgreSQL 持久化与最小查询面
- Acceptance: bootstrap/runtime/audit service 的真相源切换明确，schema gate 能通过，最小查询面可验证
- Guardrails: 不回退当前 auth/session/RBAC 主链；不把审计能力扩成新的日志平台；不在没有 schema gate 的情况下宣称完成
- Sampling Plan: 先冻结 write/read boundary，再进入 repository/schema，再补 focused API/integration tests
- Constraints: 这是 schema-sensitive child；L0 通过不等于 PostgreSQL gate 通过

## Latest Evidence

- `apps/api/src/db_monitor_api/auth/postgres_repository.py` 新增 `PostgresAuditRepository`，把 `audit_entries` 作为 PostgreSQL 真实状态面
- `apps/api/src/db_monitor_api/bootstrap.py` 现在在 `RuntimeMode.POSTGRES` 下显式接线 `PostgresAuditRepository`，local runtime 仍保留 `InMemoryAuditRepository`
- `apps/api/src/db_monitor_api/auth/domain.py` 与所有现有写路径现在都带 `organization_id`，避免用户管理 child 继续建立在无组织归属的 audit seam 上
- `apps/api/src/db_monitor_api/auth/router.py` 新增 admin-only `/auth/audit-entries`，用当前 session 的 active organization 作为 read scope
- `apps/api/src/db_monitor_schema/postgres.py` 新增 `audit_entries` 表并将 PostgreSQL schema contract 升到 `v8`
- `tests/integration/control_plane/test_control_plane_postgres.py` 证明：
  - 审计记录跨 runtime 重建后仍可读取
  - `/auth/audit-entries` 只返回当前 organization 的审计记录
  - 外部 organization 的注入审计记录不会泄漏进当前管理面
- `tests/api/auth/test_auth_session.py` 证明：
  - admin 可以读取最近审计
  - 非 admin 会被 `settings:write` guard 拒绝，并记录 `audit.denied`
- focused gates 实际通过：
  - `uv run pytest tests/api/auth tests/integration/control_plane/test_control_plane_postgres.py tests/schema/test_schema_bootstrap.py -q`
  - `pnpm openapi:update`
  - `pnpm openapi:check`
  - `uv run pytest tests/api/rbac -q`

## Notes

- 本 child 刻意没有把审计扩成新的日志平台，只补了 PRD closeout 所需的持久化与最小查询面
- 共享状态面的主误差已从 “audit in-memory seam” 转移到 “user/role management 仍是 seed-user-only”
