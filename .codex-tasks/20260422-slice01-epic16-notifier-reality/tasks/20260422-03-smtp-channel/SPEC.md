# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 实现 SMTP **备**通道：HTML 模板 + 基础配置 + 成功/失败落 `notify_history`
- 为 #4 端到端的"Feishu 不可达 → SMTP 接管"提供可插件对象

## Scope

- 新 `api/app/alerting/notification/channels/smtp.py`
  - 实现 `Notifier` Protocol；通过 registry 注册为 `"smtp"`
  - SMTP server / port / user / password / from_addr / use_tls 从 `settings`（`.env`）读取；**不**入库
  - 收件人: `alert_channel_bindings.config.to_addrs`（列表）
- HTML 模板:
  - 内建单一模板（不做自定义），字段对齐 Lepus `lepus_alarm_mail_content`（title / metric / value / threshold / instance / rule / time / web link）
  - 模板用 Jinja2（复用项目已有依赖；如未引入再评估）
  - 纯文本回退（SMTP `multipart/alternative`）
- 错误处理:
  - 连接 / 认证 / 超时异常都写 `notify_history.status='failed'` + `error`
  - 本子任务**不**实现降级逻辑；降级在 #4 整合

## Non-Goals

- 模板可配置（Slice 3）
- DKIM / 发件速率限制 / 白名单（不在 Slice 1）
- 批量告警合并（Slice 3 告警生命周期）

## Final Validation Command

```bash
uv run pytest tests/api/alerting/notification/test_smtp_channel.py -q
```
