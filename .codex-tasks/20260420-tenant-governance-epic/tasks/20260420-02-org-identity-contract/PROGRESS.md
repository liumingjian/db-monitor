# Progress

## Summary

- Task shape: single-full
- Goal: 冻结组织身份与活动组织会话的最小契约

## Recovery

- 任务: 当前正在实现 auth/session 的 active-organization baseline
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260420-tenant-governance-epic/tasks/20260420-02-org-identity-contract/TODO.csv`
- 下一步: 进入子任务 `#3`，为 organizations / memberships 建立 Postgres schema baseline

## Notes

- 当前 auth/session 仍隐含“全局唯一工作区”
- 本任务已完成：
  - auth domain 中新增 active organization 与 organization membership 契约
  - seed user 现在显式挂到默认组织 `org-internal`
  - `/auth/login` 与 `/auth/me` 现在返回 active organization 与 membership 列表
  - typed client / OpenAPI snapshot 已同步
- 本任务只把组织上下文变成显式事实，不处理资源隔离和组织切换行为

## Latest Validation

- `uv run pytest tests/api/auth tests/api/rbac`
- `pnpm openapi:update`
- `pnpm openapi:check`
- `pnpm typecheck`
