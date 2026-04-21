# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 analytics API 不再只为 MySQL detail route 服务
- 为 Oracle 暴露最小可测试的趋势读取路径和 typed contract

## Non-Goals

- 不在本任务中追求 overview 层的全引擎统一 ranking
- 不把 Oracle analytics 伪装成与 MySQL 完全同构

## Final Validation Command

```bash
uv run pytest tests/api/analytics tests/integration/analytics_queries \
  && pnpm openapi:check
```
