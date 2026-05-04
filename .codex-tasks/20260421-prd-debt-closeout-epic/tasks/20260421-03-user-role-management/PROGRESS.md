# Progress

## Summary

- Task shape: single-full
- Goal: 补齐用户、角色和权限的最小产品管理面

## Recovery

- 任务: child `#3` 已完成
- 形态: single-full
- 进度: 4/4
- 当前: 无。用户管理产品面与 child 级 signoff 已完成
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/tasks/20260421-03-user-role-management/TODO.csv`
- 下一步: 回到 parent epic，激活 child `#4` 实例详情语义收口

## Control Contract

- Primary Setpoint: 让平台管理员不再只能依赖 seed users 和代码内角色常量，而是能通过正式产品面查看用户、角色和有效权限，并对现有用户角色做最小管理
- Acceptance: contract 明确限制在 organization-scoped admin surface；后端提供 user list 与 role update；管理写路径会进入持久化 audit；web shell 提供最小可用管理入口
- Guardrails: 不重写现有 session/auth 主链；不扩成完整 IAM；不引入新的多组织切换模型；不回退现有 RBAC permission semantics
- Sampling Plan: 先冻结 contract，再收 backend，再补 web surface 与 signoff
- Constraints: child `#2` 已经收口 audit persistence，因此本 child 的管理写路径必须复用该审计真相，而不能落回内存 seam

## Latest Evidence

- 后端 contract 已收口：
  - `apps/api/src/db_monitor_api/auth/router.py` 新增 admin-only `/auth/users`、`/auth/roles`、`/auth/users/{id}/roles`
  - `apps/api/src/db_monitor_api/auth/service.py` 与 `repository.py` 现在支持 organization-scoped user listing、role catalog 和 existing-user role update
  - 管理写路径会记 `users.roles.update` 审计，并复用 child `#2` 已落地的持久化 audit truth
- Web surface 已收口：
  - `packages/api-client/src/index.ts` 新增 user-management typed contract
  - `apps/web/app/settings/page.tsx` 在现有 settings shell 中提供最小 server-rendered 用户列表、有效权限 readout 和角色更新表单
- Focused gates 已通过：
  - `uv run pytest tests/api/auth tests/api/rbac -q`
  - `pnpm openapi:check`
  - `pnpm --filter web test`
  - `pnpm --filter web typecheck`

## Notes

- 本 child 保持在 organization-scoped admin surface，不扩到用户创建、密码重置、邀请流或复杂 IAM
