# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 rules / alerts page、form 文案 与 workflow messaging 诚实承载 multi-engine alert baseline

## Non-Goals

- 不新增 Oracle 专属 alert 页面家族
- 不在本 task 中重写 notifier delivery surface

## Final Validation Command

```bash
pnpm --filter web test \
  && pnpm --filter web typecheck
```
