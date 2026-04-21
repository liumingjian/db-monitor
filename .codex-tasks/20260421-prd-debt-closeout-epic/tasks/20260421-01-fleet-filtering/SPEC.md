# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为实例列表与告警列表增加最小但显式的筛选 contract，并把它打通到 typed client、Web filter surface 和 focused tests

## Non-Goals

- 不引入分页、排序、saved filters 或复杂搜索 DSL
- 不修改组织治理、告警 workflow 或 analytics 主链语义
- 不把实例筛选扩成 overview 级联过滤系统

## Final Validation Command

```bash
uv run pytest tests/integration/control_plane/test_control_plane.py tests/api/alerting/test_alerting_contract.py \
  && pnpm openapi:check \
  && pnpm --filter web test \
  && pnpm --filter web typecheck
```
