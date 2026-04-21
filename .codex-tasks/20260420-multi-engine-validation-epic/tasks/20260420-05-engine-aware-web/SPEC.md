# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在不打破当前 MySQL UX 的前提下，把 inventory / detail / onboarding surface 提升到 engine-aware

## Final Validation Command

```bash
pnpm --filter web test && pnpm --filter web typecheck && pnpm --filter web build
```
