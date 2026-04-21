# Progress

## Summary

- Task shape: single-full
- Goal: 把告警与审计收敛到组织上下文

## Recovery

- 任务: 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 子任务已收口，父 epic 已可切换到 API / web surface 子任务
- 文件: `.codex-tasks/20260420-tenant-governance-epic/tasks/20260420-05-org-scoped-alerting-audit/TODO.csv`
- 下一步: 进入子任务 `#6 Expose organization governance semantics in API and web surfaces`

## Evidence

- alerting domain 现在显式携带 `organization_id`：
  - `AlertRule.organization_id`
  - `AlertRecord.organization_id`
  - `AlertHistoryEvent.organization_id`
- alerting repository 现在显式支持两种读取模式：
  - 组织视图：`organization_id=<active-org>`
  - 系统视图：`organization_id=None`
- alerting routes/service/workflow 现在都通过 active organization 读取规则、告警与历史
- create-rule 流程会校验 `instance_ids` 是否属于当前组织，阻断跨组织实例引用
- Postgres alerting repository 与 schema 已升级到 `v6`：
  - `alert_rules.organization_id`
  - `alert_records.organization_id`
  - `alert_history.organization_id`
  - v5 旧表可通过 bootstrap 收敛到新字段
- 新增组织隔离证据：
  - API contract 测试证明外部组织规则/告警不会泄露到默认组织视图
  - API contract 测试证明不能用外部组织实例创建默认组织规则
  - PostgreSQL live gate 证明真实仓储下也保持同样隔离

## Validation

- `uv run python -m compileall apps/api/src tests`
- `uv run pytest tests/schema/test_schema_bootstrap.py tests/alerting_contract tests/alerting_workflow tests/alerting_delivery tests/alerting_noise tests/notifier tests/rule_engine tests/recovery/test_alert_recovery.py tests/api/alerting/test_alerting_contract.py tests/integration/alert_pipeline/test_alert_pipeline.py`
- `uv run pytest tests/api/alerting tests/integration/alert_pipeline tests/recovery`
- `uv run pytest tests/integration/control_plane/test_control_plane_postgres.py`
