# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为平台管理员补齐最小可运营的用户、角色和权限管理产品面

## Non-Goals

- 不把当前系统扩成复杂 IAM 平台
- 不引入新的多组织治理模型

## Final Validation Command

```bash
uv run pytest tests/api/auth tests/api/rbac \
  && pnpm openapi:check \
  && pnpm --filter web test \
  && pnpm --filter web typecheck
```
