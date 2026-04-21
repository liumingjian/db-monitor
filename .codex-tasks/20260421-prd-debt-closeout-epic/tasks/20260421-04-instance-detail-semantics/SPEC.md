# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为实例详情补齐 TPS 与角色/版本显式展示，同时保持当前 analytics coverage boundary 诚实

## Non-Goals

- 不把 detail 页面扩成新的深度分析产品
- 不扩大当前 engine-aware analytics 范围

## Final Validation Command

```bash
uv run pytest tests/api/analytics \
  && pnpm --filter web test \
  && pnpm --filter web typecheck
```
