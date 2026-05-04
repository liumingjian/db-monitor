# ADR-0013: WeCom (企业微信) and SMS Channel Expansion

> Status: Accepted
> Date: 2026-05-04
> Accepted: 2026-05-04（Boss 在 PR #2 合并后显式锁定）
> Supersedes: 无
> Related: ADR-0009（Notifier dynamic control discipline）

## Context

Epic 16 已落地 Notifier 抽象层（`ChannelRegistry` + pluggable factory）+ 飞书 + SMTP 两条通道。`CONTEXT.md` Slice 2 范围明确包含两条新通道：

- **企业微信**（WeCom，对标飞书的同等级渠道；优先级 = 飞书的并行后续补丁）
- **SMS**（短信，对标 lepus 历史飞信链路；飞信废弃不复刻）

约束：

- WeCom 必须复用 ChannelRegistry 的 pluggable 抽象，不引入新的 Notifier core 修改
- SMS 服务商必须从单一抽象出发（不预埋多家服务商，YAGNI）；初版只接一家（阿里云 SMS / 腾讯云 SMS / 二选一）
- 飞信永不复刻（`CONTEXT.md` "永不复刻" 已锁）
- 告警内容生成必须走 Notifier 已有的 `NotifyPayload`，不允许通道侧自造模板

## Decision

### 1. WeCom 通道

- 路径：`apps/api/src/db_monitor_api/alerting/notification/channels/wecom.py`
- 通道类型：`webhook`（与飞书一致），不接 SDK，不接消息中心 API
- 配置 schema（`alert_channel_bindings.config` JSON）：
  ```json
  {
    "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=<KEY>",
    "at_user_ids": ["UserA", "UserB"],
    "at_mobile": ["13800000000"]
  }
  ```
- 卡片格式：`markdown` 类型（WeCom webhook 仅支持 text / markdown / news / image / file；卡片用 markdown 充当）
- 重试：与飞书一致 — 3 次指数退避（500ms / 1s / 2s）
- 失败降级：`dispatch_with_fallback` 已支持任意通道 → SMTP 降级；WeCom 失败 fallback SMTP

### 2. SMS 通道

- 路径：`apps/api/src/db_monitor_api/alerting/notification/channels/sms.py`
- 服务商：**阿里云 SMS**（决议依据：内部 DBA 团队已有阿里云账号 + lepus 历史短信也是阿里云）
- 抽象：`SmsProvider` Protocol；当前只一个实现 `AliyunSmsProvider`；不预留多 provider 抽象层（避免 YAGNI）
- 配置 schema：
  ```json
  {
    "phone_numbers": ["13800000000"],
    "template_id": "SMS_xxx",
    "sign_name": "DB-Monitor"
  }
  ```
- 凭据：`DB_MONITOR_ALIYUN_SMS_*` 环境变量（access_key_id / access_key_secret / region）；与 SMTP 同样的 env 注入模式
- 模板：阿里云 SMS 强制使用预审模板；模板字段映射 `${rule_name}` / ${severity}` / `${instance}` / `${value}` / `${threshold}`
- 重试：1 次（SMS 计费、不允许重复轰炸）；失败直接 fallback SMTP
- **不做**：群发、长文本、富媒体、彩信、国际短信

### 3. 配置 / Binding

- `alert_channel_bindings` 表新增两个 channel 枚举值：`wecom` / `sms`
- 单事件可同时绑定多通道（rule × channel 多对多已是当前设计）
- bindings 注入方式仍是 `InMemoryBindingRepository`（PostgresBindingRepository 仍归 Slice 3+）

## Consequences

### Positive

- 通知覆盖面从飞书 + SMTP → 飞书 + 企业微信 + SMTP + SMS，覆盖了内部 DBA 主流通讯习惯
- ChannelRegistry / DispatchCoordinator 一次成立、N 次复用的设计假设被这次扩张验证
- SMS 仅 1 个 provider 不引入虚抽象，未来需要加第二家时再 refactor 为多 provider

### Negative / Tradeoff

- 阿里云 SMS 计费模型 + 模板预审是新的运维负担；运维方需要建立模板申请 / 审批 SOP
- WeCom webhook 卡片排版能力弱于飞书富卡片；同事件在 WeCom 看到的信息密度更低
- `alert_channel_bindings.channel` 枚举从 `feishu/smtp` 扩到 4 值，schema 迁移 v11 → v12

### Risks

- WeCom webhook 速率限制：单 webhook 20 次/分钟。当前 DispatchCoordinator(cap=128) 不会触发，但需要在监控里看 4xx 比例
- 阿里云 SMS 模板审批延迟（行业惯例 1-3 工作日）；上线时序需要把模板申请放在最前面

## Decision Window

- 2026-05-04 起草
- 2026-05-04 Boss 在 PR #2（kickoff）合并后显式 Accept；child #1（WeCom）随即解锁开工
- SMS（child #2）锁定的实现路径：阿里云单 provider + `AliyunSmsProvider`；模板审批走 child #1 完成前的并行准备
