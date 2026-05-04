# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 把 rule-engine 命中事件 → Notifier 异步送达 → `notify_history` 写入串起来
- 保证 Notifier 的任何延迟 / 失败**不**回压 rule-engine 评估循环
- 落地 Feishu 主 → SMTP 降级的路由策略

## Scope

- 在 `rule-engine` 命中路径上发布 `RuleHitEvent`（不改评估核心；加一个 sink）
- `notification.service.dispatch(event)`:
  - 解析 rule → bindings（按 channel 排序：feishu 优先，smtp 次之）
  - 异步 fire-and-forget：用 `asyncio.create_task` 或独立任务队列（若已有 dramatiq，走 dramatiq）
  - 每个 binding 独立 goroutine/task；互不阻塞
  - 每次尝试写 `notify_history`
- 降级策略: feishu 连续 3 次失败（含重试耗尽）→ 自动触发 smtp binding（若配置）；**只**在同一事件内降级，不做跨事件状态机
- Timeout 硬约束: rule-engine 评估 loop 中 dispatch 调用必须 ≤100ms 返回（实际发送在后台完成）
- 回归测试: 模拟 Notifier sleep 10s，验证 rule-engine p95 不受影响
- 端到端契约测试: mock 飞书 webhook + SMTP server，断言 `notify_history` 两条记录（feishu failed + smtp success）

## Non-Goals

- 告警抑制 / 去重窗口（Slice 3）
- 告警升级（Slice 3）
- 通道配置 UI（Slice 4）

## Final Validation Command

```bash
uv run pytest tests/api/alerting/notification/test_e2e_dispatch.py -q && uv run pytest tests/rule_engine/test_dispatch_backpressure.py -q
```
