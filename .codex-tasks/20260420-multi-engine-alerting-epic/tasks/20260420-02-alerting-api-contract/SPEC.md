# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在 alerting service / router / typed contract 中实现 engine-aware rule catalog 与 alert API baseline

## Non-Goals

- 不在本 task 中完成整个 rule-engine evaluation pipeline
- 不引入完整 alert DSL

## Final Validation Command

```bash
uv run pytest tests/api/alerting tests/alerting_contract \
  && pnpm openapi:check
```
