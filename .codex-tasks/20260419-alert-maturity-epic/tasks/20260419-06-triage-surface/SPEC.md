# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 API、OpenAPI、typed client 与 Web 页面暴露新的值班工作流
- 保证前端 triage 行为建立在后端事实源之上，而不是在 UI 里拼业务逻辑
- 形成最小可用的 on-call triage surface

## Non-Goals

- 不重做整套前端设计系统
- 不把 workflow 逻辑下沉到 UI 本地状态管理

## Constraints

- API 契约变更必须通过 OpenAPI/client 同步暴露
- Web 页面只能消费 typed client 与 server actions，不持有业务真相
- triage surface 必须等待 backend semantics 稳定后再展开

## Deliverables

- alert workflow API surface
- typed client contract updates
- Web triage pages and interaction coverage

## Final Validation Command

```bash
uv run pytest tests/api/alerting && pnpm --filter web test && pnpm --filter web typecheck && pnpm --filter web build
```
