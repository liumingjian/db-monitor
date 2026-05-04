# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 用 targeted gate 与 Oracle live coverage 为 Epic 11 收口

## Non-Goals

- 不在本任务中新增产品功能
- 不把 live gate 失败静默降级成离线 green

## Constraints

- 必须在 child `#3`、`#4`、`#5` 完成后再运行
- 必须明确记录 Oracle live gate 是否真实重跑，若未重跑必须说明原因

## Deliverables

- parity signoff 证据
- 对 epic parent 的完成回写

## Final Validation Command

```bash
pnpm openapi:check \
  && uv run pytest tests/api/analytics tests/integration/analytics_queries tests/integration/metrics_pipeline \
  && pnpm --filter web test \
  && pnpm --filter web typecheck \
  && pnpm --filter web build \
  && pnpm smoke \
  && pnpm test:control-plane:oracle
```
