# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 冻结组织身份、成员关系和活动组织会话的最小契约
- 让 auth/session API 显式暴露 active organization，而不是继续依赖全局默认工作区假设
- 保持当前单组织默认路径稳定，不引入切组织 UI 或资源 scoping 复杂度

## Non-Goals

- 不在本任务中落地 Postgres 组织表和资源 scoping
- 不实现组织切换器或组织管理页面
- 不改变现有权限字符串集合

## Constraints

- 现有 `admin/operator/viewer` 角色仍保持可用
- 新契约必须以“默认单组织 + 显式组织上下文”方式演进，而不是直接变成多组织行为
- 变更如果触及 `/auth/*` 契约，必须同步 OpenAPI 与 typed client

## Deliverables

- auth domain / seed user / session contract 中的显式组织身份
- `/auth/login` 与 `/auth/me` 的 active organization 响应基线
- 对应的 auth / RBAC / API client 契约测试

## Final Validation Command

```bash
uv run pytest tests/api/auth tests/api/rbac \
  && pnpm openapi:check \
  && pnpm typecheck
```
