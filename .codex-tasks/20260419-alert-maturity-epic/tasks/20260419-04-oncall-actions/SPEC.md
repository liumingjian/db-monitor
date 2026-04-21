# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 为告警引入 ack、owner、note 等值班处理动作
- 让处理动作写入持久化状态与历史，而不是只存在 UI 交互层
- 统一“谁接手了、做过什么、当前处置状态如何”的语义

## Non-Goals

- 不实现复杂工单系统
- 不引入额外租户/组织治理逻辑

## Constraints

- 所有值班动作都必须显式写入 alert history
- owner 与 ack 状态必须可通过 API 和 repository 复现
- 处理动作必须建立在新的 alert state contract 上

## Deliverables

- on-call action contract
- ack/owner/note behavior tests
- API mutation semantics for alert workflow actions

## Final Validation Command

```bash
uv run pytest tests/alerting_workflow tests/api/alerting
```
