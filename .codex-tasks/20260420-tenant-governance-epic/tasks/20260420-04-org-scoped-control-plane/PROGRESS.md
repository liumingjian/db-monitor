# Progress

## Summary

- Task shape: single-full
- Goal: 把控制面资产与设置挂到组织上下文

## Recovery

- 任务: 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 子任务已收口，父 epic 已可切换到告警 / 审计子任务
- 文件: `.codex-tasks/20260420-tenant-governance-epic/tasks/20260420-04-org-scoped-control-plane/TODO.csv`
- 下一步: 进入子任务 `#5 Scope alerting workflow and audit trails to organization context`

## Evidence

- control-plane domain 现在显式携带 `organization_id`：
  - `MonitoredInstance.organization_id`
  - `SystemSetting.organization_id`
- control-plane repository 现在显式区分两种读取模式：
  - 组织视图：`organization_id=<active-org>`
  - 系统视图：`organization_id=None`
- Postgres control-plane schema 提升到 `v5`，并支持从旧表收敛：
  - `control_mysql_instances.organization_id`
  - `control_settings.organization_id`
  - `control_settings` 主键升级为 `(organization_id, key)`
  - bootstrap 会确保默认组织 `org-internal` 存在
- control-plane routes/services 现在统一通过 `context.active_organization.organization_id` 做实例与设置读写
- 新增隔离证据：
  - in-memory repository 组织隔离测试
  - control-plane route 只暴露 active org 资源的集成测试
  - PostgreSQL live gate 验证外部组织资源不会泄露到默认组织视图

## Validation

- `uv run python -m compileall apps/api/src tests`
- `uv run pytest tests/schema/test_schema_bootstrap.py tests/api/analytics/test_analytics_overview.py tests/scheduler/test_scheduler_contract.py tests/scheduler/test_scheduler_dispatch.py tests/recovery/test_pipeline_recovery.py tests/integration/metrics_pipeline/test_metrics_pipeline.py`
- `uv run pytest tests/api/assets tests/integration/control_plane`
- `uv run pytest tests/api/auth tests/api/rbac`
- `pnpm openapi:check`
