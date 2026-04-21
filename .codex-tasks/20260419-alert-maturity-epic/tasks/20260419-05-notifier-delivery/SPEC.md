# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让 notifier delivery 在新 workflow 下保持显式、可恢复、可审计
- 定义 suppression、ack、ownership 对 delivery 的影响边界
- 为值班交接保留足够的 delivery failure / retry 证据

## Non-Goals

- 不在本任务中接入大量外部通知供应商
- 不用隐藏失败的方式换取表面稳定

## Constraints

- delivery failure 必须继续显式暴露
- retry / escalation 语义必须服从 noise-control 与 on-call state
- 不允许让 notifier 反向成为 alert 的状态真相源

## Current Decision Freeze

- delivery suppression 只作用于“失败后本应 retry 的通知”
- 初次 open 时的 notifier failure 仍然必须显式报错，不允许被 ACK/owner 提前吞掉
- 如果 alert 已进入以下任一人工接管状态，则后续 retry 不再继续发送外部通知：
  - `ACKNOWLEDGED`
  - `owner_user_id` 已存在
- 当 retry 被 workflow 状态截断时，必须写入 `NOTIFICATION_SUPPRESSED` history evidence
- `NOTIFICATION_SUPPRESSED` 不替代 noise-control 的 `SUPPRESSED`
  - 前者表示“通知动作被 workflow 截断”
  - 后者表示“重复命中被 noise-control 聚合”

## Deliverables

- delivery policy contract
- retry/escalation behavior tests
- recovery and failure evidence under the new workflow

## Final Validation Command

```bash
uv run pytest tests/alerting_delivery tests/recovery && powershell -ExecutionPolicy Bypass -File ./scripts/test-recovery-paths.ps1
```
