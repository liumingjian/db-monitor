# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为告警建立显式的 dedupe、suppression 与 grouping 语义
- 降低噪音，同时保留根因定位所需的实例与规则证据
- 让 notifier 与值班流程建立在同一份 noise-control 事实源之上

## Non-Goals

- 不在本任务中实现完整值班页面
- 不用 silent drop 假装噪音被治理

## Constraints

- 抑制必须可审计，不能只是“不发送通知”
- grouping 不能抹掉实例级根因信息
- 去噪策略必须服从已冻结的 alert state contract

## Current Decision Freeze

- group key 固定为 `rule_id + instance_id`
- 不做跨实例聚合，也不新增 grouped parent alert
- active alert 已存在且再次命中时：
  - 不再创建新 alert
  - 继续刷新 `current_value` 与 `last_evaluated_at`
  - 只有当 suppression window 到期时，才追加一条 `SUPPRESSED` history evidence
- suppression evidence 必须带上当前 group key 与触发值，防止降噪变成 silent drop
- notifier 仍然服从自己的 retry contract；只有“不需要本次通知动作”时，才进入 suppressed evidence 分支

## Deliverables

- noise-control policy contract
- suppression/grouping behavior tests
- PostgreSQL-backed alert pipeline evidence

## Final Validation Command

```bash
uv run pytest tests/alerting_noise tests/integration/alert_pipeline && powershell -ExecutionPolicy Bypass -File ./scripts/test-alert-pipeline-postgres.ps1
```
