# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把当前 multi-engine rule / alert baseline 的 MySQL-specific seam 写清并冻结成最小可实现边界
- 先明确什么 rule / alert semantics 可以 engine-aware，什么仍必须保留非 parity 边界

## Non-Goals

- 不在本 task 中完成整个 alerting implementation
- 不在本 task 中引入全指标 DSL 或全引擎 parity

## Final Validation Command

```bash
uv run pytest tests/api/alerting/test_alerting_contract.py tests/rule_engine/test_rule_engine_contract.py \
  && pnpm openapi:check
```
