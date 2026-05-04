# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 建立 Notifier 抽象层：`Notifier` Protocol + pluggable factory + channel registry
- 落地 `notify_history` 表（PG），作为所有 channel 送达状态的单一真相
- 暴露 `alert_channel_bindings` 的最小关系（rule → channel）

## Scope

- 新包 `api/app/alerting/notification/`（目录可沿既有风格调整）
  - `protocol.py`：`NotifyPayload`、`NotifyResult`、`Notifier` Protocol
  - `registry.py`：`register_channel(name, factory)`、`get_notifier(name)`
  - `service.py`：业务入口 `dispatch(rule_hit_event) -> list[NotifyResult]`
- PG 迁移：`notify_history`
  - 列: `id UUID PK`, `rule_id FK`, `instance_id FK NULL`, `channel VARCHAR`, `status VARCHAR`, `attempt INT`, `attempted_at TIMESTAMPTZ`, `delivered_at TIMESTAMPTZ NULL`, `error TEXT NULL`, `payload_hash VARCHAR`, `organization_id FK`
  - 索引: `(rule_id, attempted_at DESC)`, `(status)` 用于失败重放查询
- PG 迁移：`alert_channel_bindings`（若不存在）
  - 列: `rule_id FK`, `channel VARCHAR`, `config JSONB`, PK (rule_id, channel)
- 契约: 新增 `/api/admin/notify-history` list 端点（最小）用于 web 观察
- OpenAPI 快照 + typed client 重新生成

## Non-Goals

- 具体 channel 实现（飞书 #2、SMTP #3）
- 告警抑制 / 模板引擎 / 升级链
- 通道配置的 web 编辑 UI（本子任务仅后端 + 查询）

## Final Validation Command

```bash
pnpm test:schema:bootstrap && uv run pytest tests/api/alerting/test_notifier_registry.py -q && pnpm openapi:check
```
