# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 冻结告警生命周期状态契约，避免后续 workflow 各自发明局部真相
- 扩展 repository / persistence boundary，使其能够承载 ack、owner、note、suppression 等值班语义
- 为后续 noise controls、notifier delivery 与 Web triage 提供稳定基础

## Non-Goals

- 不在本任务中完成完整 Web triage 交互
- 不提前实现复杂通知升级策略

## Control Contract

- **Primary Setpoint**
  - alert domain 与 PostgreSQL persistence 可以无歧义表达后续 on-call workflow 的核心状态与事实字段
- **Acceptance**
  - domain/repository/API/integration contract tests 通过，且不破坏既有 alert pipeline gate
- **Guardrails**
  - 不破坏现有 open/resolved 行为；新增状态必须显式落到历史与持久化事实源
- **Boundary**
  - 允许修改 alerting domain、repository、postgres adapter、schema contract、相关 tests/gates
- **Risks**
  - 状态字段扩展可能导致 schema drift 或 detail/history 语义分裂

## Constraints

- 真实状态必须以 PostgreSQL repository 为准
- 不允许为了兼容旧模型而保留双真相或影子实现
- schema-sensitive 行为必须在后续 live gate 中被覆盖

## Current State Estimate

- 当前 `AlertStatus` 只有 `OPEN` 与 `RESOLVED`，无法区分“已有人接手但尚未恢复”的状态
- 当前 `AlertEventType` 只覆盖 opened/notified/notification_failed/resolved，无法表达值班动作与责任归属
- 当前 repository 只有 `find/list/get/upsert/history/rule` 边界，尚无显式 workflow mutation contract
- 当前 Web 与 API 只提供只读告警浏览，不具备 on-call action surface

## Target Contract Freeze

- 最小状态机：
  - `OPEN`
  - `ACKNOWLEDGED`
  - `RESOLVED`
- 最小 alert record 字段扩展：
  - `acknowledged_at`
  - `acknowledged_by_user_id`
  - `owner_user_id`
  - `owner_assigned_at`
- 最小 history 事件扩展：
  - `ACKNOWLEDGED`
  - `OWNER_ASSIGNED`
  - `NOTE_ADDED`
- 决策边界：
  - 备注先作为 history event 持久化，而不是单独引入 note table
  - suppression 不在本任务里落成最终策略对象，但 repository contract 需要为后续 child task 预留显式入口
  - notifier 继续只消费 alert workflow 事实，不拥有独立状态机

## Deliverables

- alert state contract
- repository/persistence evolution plan
- schema-sensitive tests
- targeted contract validation

## Final Validation Command

```bash
uv run pytest tests/alerting_contract tests/api/alerting tests/integration/alert_pipeline
```
