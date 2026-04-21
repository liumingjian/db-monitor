# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 Oracle data-plane epic 形成根级 signoff gate
- 证明 Oracle data-plane 进展与现有 MySQL / governance 主链可以同时成立

## Non-Goals

- 不扩大产品边界

## Final Validation Command

```bash
pnpm openapi:check \
  && uv run pytest tests/schema/test_schema_bootstrap.py tests/api/analytics tests/integration/metrics_pipeline tests/integration/analytics_queries tests/integration/control_plane \
  && pnpm --filter web test \
  && pnpm --filter web typecheck \
  && pnpm --filter web build \
  && pnpm smoke
```
