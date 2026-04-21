# Progress

## Summary

- Task shape: single-full
- Goal: 补齐用户、角色和权限的最小产品管理面

## Recovery

- 任务: child `#3` 已激活，当前进入 backend contract 落点阶段
- 形态: single-full
- 进度: 1/4
- 当前: step `#2` `Implement user and role management backend semantics`
- 文件: `.codex-tasks/20260421-prd-debt-closeout-epic/tasks/20260421-03-user-role-management/TODO.csv`
- 下一步: 在现有 auth/session/RBAC 之上确认最小后端 contract，把 user list / role update 的状态面与 audit 写路径收口到可验证实现

## Control Contract

- Primary Setpoint: 让平台管理员不再只能依赖 seed users 和代码内角色常量，而是能通过正式产品面查看用户、角色和有效权限，并对现有用户角色做最小管理
- Acceptance: contract 明确限制在 organization-scoped admin surface；后端提供 user list 与 role update；管理写路径会进入持久化 audit；web shell 提供最小可用管理入口
- Guardrails: 不重写现有 session/auth 主链；不扩成完整 IAM；不引入新的多组织切换模型；不回退现有 RBAC permission semantics
- Sampling Plan: 先冻结 contract，再收 backend，再补 web surface 与 signoff
- Constraints: child `#2` 已经收口 audit persistence，因此本 child 的管理写路径必须复用该审计真相，而不能落回内存 seam

## Latest Evidence

- 当前 repo 已有：
  - `auth.login/logout/me`
  - role 常量与 permission 解析
  - organization membership readout
  - RBAC enforcement
- 当前 repo 缺少：
  - 用户列表 API
  - 角色更新 API
  - 管理产品面
- 冻结后的最小交付边界：
  - API: admin-only organization-scoped user list + existing-user role update
  - UI: 放在现有 settings / governance shell 里，用最小 server-rendered 表单完成
  - 审计: 管理写路径必须记录用户角色变更 action，挂到 PostgreSQL audit truth
- 明确排除：
  - 用户创建 / 删除
  - 密码重置
  - 自定义 permission authoring
  - 复杂 IAM / invitation / org transfer 流程

## Notes

- 当前 repo 已有 session、permissions、roles、RBAC enforcement，但没有完整管理面
