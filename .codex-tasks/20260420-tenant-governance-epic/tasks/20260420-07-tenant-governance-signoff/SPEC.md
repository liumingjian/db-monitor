# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 形成 Epic 06 的根级治理 signoff gate

## Final Validation Command

```bash
pnpm openapi:check \
  && uv run pytest tests/api/auth tests/api/rbac tests/api/assets tests/api/alerting tests/integration/control_plane tests/integration/alert_pipeline tests/schema/test_schema_bootstrap.py tests/ops \
  && pnpm --filter web test \
  && pnpm --filter web typecheck \
  && pnpm --filter web build \
  && pnpm smoke
```
