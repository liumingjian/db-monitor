# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在现有 analytics API 上补更深的 MySQL workload / engine-health 信号

## Final Validation Command

```bash
uv run pytest tests/api/analytics tests/integration/analytics_queries && pnpm openapi:check && pnpm test:analytics:clickhouse
```
