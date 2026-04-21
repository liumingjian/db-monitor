# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 深化 mixed-engine fleet 的 diagnostics baseline，并把 preset semantics 收敛到 engine-aware 但不伪装 parity 的状态

## Non-Goals

- 不在本 task 中做 multi-engine alerting
- 不扩大为通用报表系统

## Final Validation Command

```bash
pnpm --filter web test \
  && pnpm --filter web build
```
