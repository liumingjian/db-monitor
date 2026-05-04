# Progress

## Summary

- Task shape: epic
- Goal: 用一轮有边界的 closeout epic，把原始 PRD 剩余的控制面欠账收口成可验证状态

## Recovery

- 任务: Epic 10 已完成
- 形态: epic
- 进度: 5/5
- 当前: 无 active child；所有 closeout child 与 root signoff 已完成
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/SUBTASKS.csv`
- 下一步: 无。若后续继续开发，先回到 roadmap close-out / extension 流程

## Control Contract

- Primary Setpoint: 把 `docs/prd-closeout.md` 中的 remaining gaps 从“文档说明”推进到“代码与验证已成立”
- Acceptance: 新 epic truth artifacts 与所有 child skeleton 已落盘；当前 active child 能持续关闭剩余 PRD gaps；后续 child 仍可从磁盘恢复
- Guardrails: 不回退现有 auth、organization、alerting、analytics 与多引擎基线；不把 closeout 扩成新的产品 phase
- Sampling Plan: 先做无 schema 风险的筛选面，再进入 audit persistence / user management 等共享状态子任务，最后用 signoff 收口
- Constraints: 只有 `SUBTASKS.csv` 中列出的 child 能进入实现；未进入 `IN_PROGRESS` 的 child 不允许提前写产品代码

## Latest Evidence

- child `#1` 已关闭实例/告警筛选 gap：
  - `/control/instances` 与 `/alerts` 都具备显式 filter contract、typed client 支持和 server-rendered filter surface
- child `#2` 已关闭审计持久化 gap：
  - `audit_entries`、`PostgresAuditRepository` 与 admin-only `/auth/audit-entries` 已成为最小审计真相
- child `#3` 已关闭用户/角色管理 gap：
  - admin-only `/auth/users`、`/auth/roles`、`/auth/users/{id}/roles` 已落地
  - `/settings` 现在能显式查看用户、角色和有效权限，并更新现有用户角色
- child `#4` 已关闭 detail semantics gap：
  - MySQL detail cards 现在显式包含 TPS
  - 实例详情页现在显式展示 validation、server role、server version readout
- child `#5` 已完成 root signoff：
  - `pnpm openapi:check`
  - `uv run pytest tests/api/auth tests/api/rbac tests/api/alerting/test_alerting_contract.py tests/api/analytics tests/integration/control_plane/test_control_plane.py tests/integration/control_plane/test_control_plane_postgres.py tests/schema/test_schema_bootstrap.py -q`
  - `pnpm --filter web test`
  - `pnpm --filter web typecheck`
- `docs/prd-closeout.md` 已更新为“PRD closeout gaps 已完成收口”
- `EPIC_ROADMAP.md` 已将 Epic 10 标记为 `Done`，roadmap 01-10 当前全部完成

## Notes

- 这是 closeout epic，不是新的产品扩展 epic
- Oracle live gate 没有在这轮 debt pass 中重跑；既有 live baseline 仍保留在 `.codex-tasks/20260420-oracle-live-gate/`
