# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在 analytics service / API contract 中实现批准范围内的 mixed-engine overview metric parity
- 让 overview cards / charts / coverage 语义不再只对 MySQL 成立

## Non-Goals

- 不在本任务中完成 web messaging 收口
- 不扩展到 alerting 或 runtime family

## Constraints

- 必须遵守 child `#2` 冻结的 Oracle fleet metric family 与 parity 边界
- 必须保住现有 MySQL overview 行为
- 必须同步更新 OpenAPI / typed client

## Deliverables

- analytics contract 代码
- 对应 API / integration tests
- OpenAPI snapshot 与 typed client 对齐

## Final Validation Command

```bash
uv run pytest tests/api/analytics tests/integration/analytics_queries \
  && pnpm openapi:check
```
