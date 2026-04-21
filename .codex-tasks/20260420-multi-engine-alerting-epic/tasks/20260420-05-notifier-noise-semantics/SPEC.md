# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 深化 mixed-engine alerting 的 notifier、delivery、noise-control 与 on-call baseline

## Non-Goals

- 不在本 task 中做全渠道重构
- 不扩大为通用 incident 平台

## Final Validation Command

```bash
uv run pytest tests/alerting_delivery tests/alerting_workflow tests/notifier \
  && pnpm --filter web test
```
