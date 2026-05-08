# Task Specification — Slice 2 child #1: WeCom (企业微信) Channel

## Task Shape

- **Shape**: `single-full`

## Goals

- 把 WeCom（企业微信）作为第三条 Notifier 通道接入 `ChannelRegistry`
- 走群机器人 webhook + markdown 消息 + 内嵌 `<@userid>` @user + 可选 text fallback @mobile
- 与飞书重试策略对齐（3 次指数退避；429/5xx 可重试，4xx 非 429 不重试）
- `dispatch_with_fallback` 路径覆盖 `wecom → smtp` 降级（feishu 走老路径不变）

## Scope

- 新文件 `apps/api/src/db_monitor_api/alerting/notification/channels/wecom.py`
  - 类 `WeComNotifier`，实现 `Notifier` Protocol（`channel_name = "wecom"`）
  - HTTP 客户端 `httpx.AsyncClient`，单次请求超时 ≤5s
  - 配置 schema（来自 `binding_config`）：
    - `webhook_url: str`（必填，形如 `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=<KEY>`）
    - `at_user_ids: Sequence[str]`（可选，markdown 内嵌 `<@userid>`）
    - `at_mobile_list: Sequence[str]`（可选，触发额外 text 消息携带 `mentioned_mobile_list`）
    - `at_all: bool`（可选，markdown 内嵌 `<@all>`）
  - 主消息（markdown 类型），content 字段：
    - 标题行：`**[{SEVERITY}] {rule_name}**`
    - 列表段：`- 实例：{instance_id_or_unbound}` / 引擎 / 指标 / 命中值 / 阈值 / 时间（ISO）
    - 链接行：`[查看详情]({web_link})`（仅当 `web_link` 非空）
    - @ 段：`<@all>` 或 `<@uid1><@uid2>`，置于 content 末尾
  - 可选追加消息（仅当 `at_mobile_list` 非空且主消息成功）：
    - msgtype = `text`，content = `[{SEVERITY}] {rule_name}`，`mentioned_mobile_list = at_mobile_list`
    - 失败 best-effort，不影响主消息 `NotifyResult`
- 重试：与飞书一致 — 3 次（指数退避 1s/2s/4s）；`429` + `>=500` + `httpx.TimeoutException` + `httpx.TransportError` 可重试；其他 4xx + `errcode != 0` 不重试
- 注：`alert_channel_bindings` 仍走 `InMemoryBindingRepository`，不引入 schema 迁移（schema v11→v12 与 PostgresBindingRepository 一并落到 Slice 2 child #3 / Slice 3+）
- 单元测试 `tests/alerting_notification/test_wecom.py`：
  - `test_wecom_markdown_payload_shape`：内容字段 / 标题 / @ 内嵌
  - `test_wecom_success_returns_delivered`：mock webhook 返 `{"errcode":0}`，单次请求即返回 DELIVERED
  - `test_wecom_retries_on_429_then_succeeds`：第 1 次 429，第 2 次成功，attempt=2
  - `test_wecom_stops_on_4xx_non_retryable`：400 + errcode!=0，不重试
  - `test_wecom_stops_when_attempts_exhausted`：连续 5xx 直到 max_attempts
  - `test_wecom_handles_timeout_as_retryable`：raise `httpx.TimeoutException` 后第 2 次成功
  - `test_wecom_invalid_json_response`：返回非 JSON body 不重试，标 FAILED
  - `test_wecom_at_user_rendering`：`at_user_ids=["a","b"]` → content 末尾 `<@a><@b>`
  - `test_wecom_at_all_rendering`：`at_all=True` → `<@all>`
  - `test_wecom_at_mobile_triggers_text_followup`：mock 双请求，第二个 body 含 `mentioned_mobile_list`
  - `test_wecom_mobile_followup_failure_does_not_fail_primary`：主消息成功 + mobile 失败 → DELIVERED
  - `test_wecom_missing_webhook_url_returns_failed`：config 无 webhook_url → FAILED
- Fallback 集成 `tests/alerting_notification/test_fallback.py` 增 1-2 个用例：
  - `test_dispatch_falls_back_from_wecom_to_smtp`：wecom 失败 → smtp 成功，记录两条 history

## Non-Goals

- 不接 WeCom 应用消息 / 自建应用消息中心 API（仅 webhook）
- 不做自定义 markdown 模板（固定模板，模板自定义留 Slice 5+）
- 不做 mobile 解析为 userid（业务侧若有 userid 直接配 `at_user_ids`）
- 不动 bootstrap.py 的 channel registration（feishu 也是同状态；wiring 与 feishu/smtp 一并落到 Slice 2 child #5 收尾）
- 不动 schema（PostgresBindingRepository 落 Slice 3+）
- 不实现 dedup / suppression（Slice 2 child #3）

## Risks

- WeCom webhook 速率限制：单 webhook 20 次/min。本 child 不引入节流；DispatchCoordinator(cap=128) 已是上游守门人。生产端在 child #5 signoff 时观察 4xx 比例
- markdown 类型 @ 必须用 `<@userid>` 内嵌；@mobile 必须用 text 类型——双消息模型已在 Scope 内反映
- 阿里云 SMS（child #2）模板审批延迟与本 child 无依赖

## Final Validation Command

```bash
uv run pytest tests/alerting_notification -q
uv run ruff check apps/api/src/db_monitor_api/alerting/notification/channels/wecom.py tests/alerting_notification
uv run mypy apps/api/src/db_monitor_api/alerting/notification/channels/wecom.py
```
