# Progress

## Summary

- Task shape: single-full
- Goal: 让审计日志成为 PostgreSQL 持久化、可查询的正式产品能力

## Recovery

- 任务: 已进入 child `#2` 的 boundary-freeze 阶段，当前需要先冻结审计持久化的最小范围
- 形态: single-full
- 进度: 0/4
- 当前: step `#1` `Freeze audit persistence boundary`
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/tasks/20260421-02-audit-persistence/TODO.csv`
- 下一步: 明确哪些现有 audit actions 必须进入 PostgreSQL 真相、最小 read path 应该挂在哪个 router，以及当前 schema/bootstrap seam 在哪里

## Control Contract

- Primary Setpoint: 审计日志不再停留在 `InMemoryAuditRepository` 运行时 seam，而是进入 PostgreSQL 持久化与最小查询面
- Acceptance: bootstrap/runtime/audit service 的真相源切换明确，schema gate 能通过，最小查询面可验证
- Guardrails: 不回退当前 auth/session/RBAC 主链；不把审计能力扩成新的日志平台；不在没有 schema gate 的情况下宣称完成
- Sampling Plan: 先冻结 write/read boundary，再进入 repository/schema，再补 focused API/integration tests
- Constraints: 这是 schema-sensitive child；L0 通过不等于 PostgreSQL gate 通过

## Latest Evidence

- `apps/api/src/db_monitor_api/bootstrap.py` 当前仍直接实例化 `InMemoryAuditRepository`
- `apps/api/src/db_monitor_api/auth/repository.py` 目前只有内存型 audit repository，没有 PostgreSQL 持久化实现
- 现有 audit write path 已分散在：
  - `auth.login` / `auth.logout`
  - `auth.permission_denied`
  - `instances.create` / `instances.validate`
  - `settings.write`
  - `rules.create` / alert workflow actions

## Notes

- 当前 child 先冻结最小持久化边界，不直接进入 schema 变更

## Notes

- 当前 repo 的显式 gap 是 `InMemoryAuditRepository` 仍是主要 runtime seam
