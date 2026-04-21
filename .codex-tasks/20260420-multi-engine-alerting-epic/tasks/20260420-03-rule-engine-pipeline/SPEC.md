# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把 rule engine evaluation、alert pipeline、noise-control 与 recovery 语义推进到第二引擎的最小可运营基线

## Non-Goals

- 不在本 task 中重写整个 workflow stack
- 不追求所有指标的 evaluation parity

## Final Validation Command

```bash
uv run pytest tests/rule_engine tests/integration/alert_pipeline tests/alerting_noise tests/recovery
```
