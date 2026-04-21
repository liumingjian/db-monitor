# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把当前 mixed-engine fleet overview 的 MySQL-first contract seam 写清并冻结成最小可实现边界
- 先明确什么 overview / diagnostics 语义可以 engine-aware，什么仍必须保留非 parity 边界

## Non-Goals

- 不在本 task 中完成全部 web overview 实现
- 不在本 task 中引入 multi-engine alerting 语义

## Final Validation Command

```bash
uv run pytest tests/api/analytics/test_analytics_overview.py tests/api/analytics/test_analytics_contract.py \
  && pnpm openapi:check
```
