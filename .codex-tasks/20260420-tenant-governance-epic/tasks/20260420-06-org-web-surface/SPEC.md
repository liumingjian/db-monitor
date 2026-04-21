# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 在 API / OpenAPI / typed client / web shell 中暴露组织治理最小入口

## Final Validation Command

```bash
pnpm openapi:check && pnpm --filter web test && pnpm --filter web typecheck && pnpm --filter web build
```
