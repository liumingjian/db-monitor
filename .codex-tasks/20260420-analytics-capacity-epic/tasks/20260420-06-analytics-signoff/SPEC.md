# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 汇总 Epic 04 的 analytics API / web / live ClickHouse 证据

## Final Validation Command

```bash
pnpm openapi:check && uv run pytest tests/api/analytics tests/integration/analytics_queries && pnpm --filter web test && pnpm --filter web typecheck && pnpm --filter web build && pnpm test:analytics:clickhouse && pnpm smoke
```
