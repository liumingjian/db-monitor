# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在 analytics service / router / typed contract 中实现 mixed-engine overview aggregation baseline

## Non-Goals

- 不在本 task 中完成整个 web overview surface
- 不引入 alerting / rule-engine 改动

## Final Validation Command

```bash
uv run pytest tests/api/analytics tests/integration/analytics_queries \
  && pnpm openapi:check
```
