# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把 analytics 结果提升成 capacity / risk insight，而不只是静态图表

## Final Validation Command

```bash
uv run pytest tests/api/analytics tests/integration/analytics_queries && pnpm --filter web test && pnpm --filter web build
```
