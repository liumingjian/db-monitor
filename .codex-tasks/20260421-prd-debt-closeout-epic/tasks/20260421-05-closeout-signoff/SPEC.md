# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 用 repo-root signoff 证明 PRD closeout epic 在关闭欠账的同时没有回退现有主链

## Non-Goals

- 不在本 task 中继续扩需求

## Final Validation Command

```bash
pnpm openapi:check \
  && uv run pytest tests/api/auth tests/api/rbac tests/api/alerting/test_alerting_contract.py tests/api/analytics tests/integration/control_plane/test_control_plane.py tests/integration/control_plane/test_control_plane_postgres.py tests/schema/test_schema_bootstrap.py \
  && pnpm --filter web test \
  && pnpm --filter web typecheck
```
