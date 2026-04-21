# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 形成 Epic 05 的根级 signoff gate

## Final Validation Command

```bash
pnpm openapi:check && uv run pytest tests/api/assets tests/integration/control_plane tests/scheduler tests/integration/metrics_pipeline && pnpm --filter web test && pnpm --filter web typecheck && pnpm --filter web build && pnpm smoke
```
