# Progress

## Summary

- Task shape: epic
- Goal: 把平台从隐式单组织约定推进到显式组织治理边界，并保持当前默认路径可运行

## Recovery

- 任务: Epic 06 已完成
- 形态: epic
- 进度: 7/7
- 当前: 所有已批准子任务均已完成
- 文件: `.codex-tasks/20260420-tenant-governance-epic/SUBTASKS.csv`
- 下一步: 无。当前 epic 已签收，后续如需继续应先根据 roadmap / 用户指令选择下一边界

## Notes

- 本 epic 不是 roadmap 默认 next，而是由用户显式批准激活
- 当前路线图中只剩 `Epic 06`；激活前的决策门已记录在 `.codex-tasks/20260420-post-epic05-transition-review/`
- 这次激活只代表“可以进入组织治理实现”，不代表要一次性做成完整多租户 SaaS
- 全部已批准 child task skeleton 已一次性落盘，满足 planning completeness 规则
- 子任务 `#2` 已完成：
  - auth domain / seed user / session 上下文已显式携带 active organization
  - `/auth/login` 与 `/auth/me` 已返回 active organization 与 organization memberships
  - OpenAPI snapshot 与 typed client 已同步到新的 auth contract
- 子任务 `#3` 已完成：
  - Postgres schema version 提升到 `4`
  - bootstrap / verify 现在要求 `organizations` 与 `organization_memberships`
  - 现有 schema/runtime/control-plane Postgres regression 仍然通过
- 子任务 `#4` 已完成：
  - control-plane domain / repository / routes / services 现在显式使用 `organization_id`
  - Postgres schema version 提升到 `5`，让 control-plane 表支持 organization-aware 读写与旧表收敛
  - in-memory 与 PostgreSQL live gate 都证明外部组织资源不会泄露到默认组织视图
- 子任务 `#5` 已完成：
  - alerting rules / alerts / history 现在显式使用 `organization_id`
  - Postgres schema version 提升到 `6`，让 alerting 表支持 organization-aware 读写与旧表收敛
  - API contract、alerting recovery bundle 与 PostgreSQL live gate 都证明外部组织规则/告警不会泄露到默认组织视图
- 子任务 `#6` 已完成：
  - typed auth session 中的 active organization 已映射进 web session model
  - web shell 与 settings 页面现在显式展示 active organization 与 membership scope
  - web tests / typecheck / build 全部保持 green
- 子任务 `#7` 已完成：
  - 根级 signoff bundle 通过，覆盖 auth、schema、control-plane、alerting、web、ops 与 smoke
  - Epic 06 现在同时具备 organization-awareness 证据链和默认单组织路径未回归的护栏证据
