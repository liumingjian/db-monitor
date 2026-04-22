# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 实现飞书 webhook 通道作为 Slice 1 **主**告警渠道
- 签名校验 + 富卡片 + @群成员 + 指数退避重试
- 失败时把记录写入 `notify_history`，触发 SMTP 降级（降级逻辑在 #4 端到端整合时串起）

## Scope

- 新 `api/app/alerting/notification/channels/feishu.py`
  - 实现 `Notifier` Protocol；通过 registry 注册为 `"feishu"`
  - 请求使用 `httpx.AsyncClient`，超时 ≤5s
  - 卡片字段（固定内建模板，本切片不做自定义）:
    - title: `[{severity}] {rule.name}`
    - content: instance_name、指标名、命中值、阈值、命中时间、web 跳转 URL
  - `@` 逻辑: 从 `alert_channel_bindings.config.at_user_ids` 读取；支持 `@all`
  - 签名: 按飞书 open-platform 规范（timestamp + secret → HMAC-SHA256 base64）
- 重试策略: 3 次；退避 `1s, 2s, 4s`；429/5xx 重试，4xx（非 429）不重试
- `notify_history` 每次尝试都写一行（`attempt` 递增）
- 单元测试: mock webhook 端点，覆盖成功 / 429 重试 / 签名错误 / at_user 解析

## Non-Goals

- 自定义卡片模板（切到 Slice 3）
- 自动解析 `@` 用户 id（本切片显式用 id 列表，不做姓名解析）
- 多机器人路由（一个 org 一个 webhook，切到 Slice 4 多租户）

## Final Validation Command

```bash
uv run pytest tests/api/alerting/notification/test_feishu_channel.py -q
```
