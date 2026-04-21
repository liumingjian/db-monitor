# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 overview page、dashboard model 与 fleet messaging 诚实承载 mixed-engine fleet semantics

## Non-Goals

- 不新增 Oracle 专属 overview 页面家族
- 不在本 task 中重写 alerting surface

## Final Validation Command

```bash
pnpm --filter web test \
  && pnpm --filter web typecheck
```
