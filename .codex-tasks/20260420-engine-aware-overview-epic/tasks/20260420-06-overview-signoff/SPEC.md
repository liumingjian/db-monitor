# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 engine-aware overview epic 形成根级 signoff gate
- 证明 mixed-engine fleet overview 进展与现有 MySQL / Oracle data-plane / governance 主链可以同时成立

## Non-Goals

- 不扩大产品边界

## Final Validation Command

```bash
pnpm openapi:check \
  && uv run pytest tests/api/analytics tests/integration/analytics_queries tests/integration/metrics_pipeline tests/integration/control_plane \
  && pnpm --filter web test \
  && pnpm --filter web typecheck \
  && pnpm --filter web build \
  && pnpm smoke \
  && pnpm test:control-plane:oracle
```
