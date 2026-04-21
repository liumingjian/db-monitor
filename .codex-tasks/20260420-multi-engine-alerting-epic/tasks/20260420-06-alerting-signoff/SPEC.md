# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为 multi-engine alerting epic 形成根级 signoff gate
- 证明第二引擎 alert baseline 与既有 MySQL / Oracle data-plane / overview 主链可以同时成立

## Non-Goals

- 不扩大产品边界

## Final Validation Command

```bash
pnpm openapi:check \
  && uv run pytest tests/api/alerting tests/alerting_contract tests/rule_engine tests/integration/alert_pipeline tests/alerting_delivery tests/alerting_noise tests/alerting_workflow tests/recovery tests/integration/control_plane \
  && pnpm --filter web test \
  && pnpm --filter web typecheck \
  && pnpm --filter web build \
  && pnpm smoke \
  && pnpm test:control-plane:oracle
```
