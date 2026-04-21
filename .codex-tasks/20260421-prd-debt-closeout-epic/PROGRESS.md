# Progress

## Summary

- Task shape: epic
- Goal: 用一轮有边界的 closeout epic，把原始 PRD 剩余的控制面欠账收口成可验证状态

## Recovery

- 任务: child `#1`、`#2` 已完成；当前 active child 已切换为 `#3` 用户/角色管理产品面
- 形态: epic
- 进度: 2/5
- 当前: child `#3` `Implement user and role management product surface`
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/SUBTASKS.csv`
- 下一步: 把 user-management backend contract 落成代码，避免管理面继续停留在 seed-user-only seam

## Control Contract

- Primary Setpoint: 把 `docs/prd-closeout.md` 中的 remaining gaps 从“文档说明”推进到“代码与验证已成立”
- Acceptance: 新 epic truth artifacts 与所有 child skeleton 已落盘；当前 active child 能持续关闭剩余 PRD gaps；后续 child 仍可从磁盘恢复
- Guardrails: 不回退现有 auth、organization、alerting、analytics 与多引擎基线；不把 closeout 扩成新的产品 phase
- Sampling Plan: 先做无 schema 风险的筛选面，再进入 audit persistence / user management 等共享状态子任务，最后用 signoff 收口
- Constraints: 只有 `SUBTASKS.csv` 中列出的 child 能进入实现；未进入 `IN_PROGRESS` 的 child 不允许提前写产品代码

## Latest Evidence

- child `#1` 已完成并通过 focused signoff：
  - `uv run pytest tests/integration/control_plane/test_control_plane.py tests/api/alerting/test_alerting_contract.py -q`
  - `pnpm openapi:check`
  - `pnpm --filter web test`
  - `pnpm typecheck`
- child `#1` 关闭的产品 gap：
  - `/control/instances` 现在支持 `name` / `environment` / `label` / `status`
  - `/alerts` 现在支持 `status` / `severity` / `instance` / `opened_after` / `opened_before`
  - `packages/api-client` 已提供对应 filter objects
  - `/instances` 与 `/alerts` 页面都已变成 server-rendered GET filter form
- child `#2` 已完成并通过 focused signoff：
  - `audit_entries` 已进入 PostgreSQL schema truth，schema contract 升到 `v8`
  - `RuntimeMode.POSTGRES` 现在显式使用 `PostgresAuditRepository`
  - `/auth/audit-entries` 已作为 admin-only 最小审计查询面落地
  - 审计写路径现在都带 `organization_id`
  - focused gates:
    - `uv run pytest tests/api/auth tests/integration/control_plane/test_control_plane_postgres.py tests/schema/test_schema_bootstrap.py -q`
    - `pnpm openapi:update`
    - `pnpm openapi:check`
    - `uv run pytest tests/api/rbac -q`
- `docs/prd-closeout.md` 现在应从 “4 项 remaining gaps” 收敛为 “3 项 remaining gaps”
- `EPIC_ROADMAP.md` 已把 `Epic 10: PRD Debt and Control-Plane Closeout` 设为当前 active epic
- `.codex-tasks/20260421-prd-debt-closeout-epic/` 及所有 child recovery skeleton 已创建完成，满足 `AGENT.md` 的 planning materialization 规则
- 当前新的主误差已转移到 child `#3`：
  - repo 仍没有正式的用户列表/角色更新产品面
  - settings / governance shell 还无法承担管理员管理现有用户的职责
  - 这是现在最合适的 control-plane closeout 收口点

## Notes

- 这是 closeout epic，不是新的产品扩展 epic
- child `#1` 已证明：列表筛选可以先在 service 层诚实收口，而不需要提前把 repository/query model 改成更重的 shared contract
- child `#2` 已证明：shared-state closeout 不一定要扩成大平台，只要把真相源、查询面和 focused gates 对齐即可
- child `#3` 仍会触碰共享状态与管理写路径，下一轮必须继续遵循 schema-sensitive gate
