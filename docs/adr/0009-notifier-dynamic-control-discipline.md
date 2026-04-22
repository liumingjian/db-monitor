# ADR-0009: Notifier dynamic control discipline (anti-chatter, anti-windup, retry bounds)

Status: accepted (2026-04-22)

Epic 16 的 Notifier 链路要在**不回压 rule-engine 评估循环**的前提下把规则命中送达飞书/SMTP。现实里这条链路天然有四类动态控制病可能发作：飞书/SMTP 瞬时抖动触发重试风暴、同一规则短时间反复命中触发通道降级 chatter、fire-and-forget 任务无界累积 windup、同一 rule-hit 被多条控制路径同时处理的控制器冲突。本 ADR 锁定这条链路的**动态控制纪律**，作为 Epic 16 child `#1` / `#4` 实施的硬约束；不 supersede ADR-0003（监控先通知后）。

## Decisions

### 1. Retry bounds（指数退避 + 单事件总预算）

每条 `(rule_hit, channel)` 投递：

- 最大尝试次数：**3**（首次 + 2 次重试）
- 退避序列：**1s → 3s → 9s**
- 单事件单通道最长总时长：**20s**（防止最后一次退避后仍超时）
- 每次尝试都写一行 `notify_history`（`attempt`、`attempted_at`、`status`、`error`）

**禁止**把退避次数或间隔写成静态常量后再也不审视；本 ADR 的 `3 / 1-3-9 / 20s` 视为启动值，若演练（Epic 16 child `#5`）观察到失败分布不符合此假设，须开新 ADR 调整，不允许热改 settings 静默消化。

### 2. Anti-chatter（降级冷却窗口）

ADR-0003 Scope #4 描述了"飞书 3 次失败→同一事件内降级 SMTP"，本 ADR 补充冷却纪律：

- 降级动作只在**单事件内**发生；不跨事件维护"通道健康度"状态机（那是 Slice 3 告警生命周期的范围，本切片显式不做）
- 同一 `(rule_id, instance_id)` 的连续命中**默认不合并**；若演练观察到飞书群被刷屏，合并策略在 Slice 2 告警成熟度切片统一解决
- 本切片**禁止**在 Notifier 层做"同规则 X 秒内只发一条"的抑制——抑制属于告警链路治理，放进 Notifier 会让控制器职责模糊

### 3. Anti-windup（task 队列硬上界）

fire-and-forget 的 `asyncio.create_task` 或 dramatiq 队列必须设硬上界：

- 进程内 pending dispatch 任务上限：**500**（按 100 实例 × 平均 5 规则活跃 × 未送达可接受积压 1 轮估算）
- 达到上限后的行为：**显式拒绝新 dispatch 并写 `notify_history` with `status='dropped'`**；不静默丢弃、不阻塞 rule-engine 评估
- 达到上限即视为 rollback trigger：`pnpm test:alert-maturity:signoff` 必须检测到此信号并让 gate 失败

**禁止**在执行器（飞书 webhook / SMTP）已饱和时继续累积"应该再加一把力"的重试——一旦某通道连续 N 次失败（ADR 默认 N=10，运行期可配），暂停该通道**60s** 再恢复，期间 dispatch 直接走降级。

### 4. Single controller per knob

同一 rule-hit 的 dispatch 只能有**一个**主控制器：`notification.service.dispatch`。

- **禁止**在 rule-engine 内部再开一条并行投递路径"以防万一"
- **禁止**在 channel adapter（飞书 / SMTP）内部自作主张重试——重试次数由上层统一控制
- **禁止**将 dramatiq 默认重试与 Notifier 手动重试并开

如果后续要加 on-call 升级链（Slice 3），通过显式仲裁接入主控制器，而不是另开控制器。

### 5. 默认值与运行期可配性

本 ADR 锁定的所有数字（3 / 1-3-9 / 20s / 500 / 60s / 10 次）都是**启动值**：

- 进入 `settings` / `ConfigMap`，运行期可配；不写死成字面常量
- 每一次运行期变更必须同步写一条 audit log `notifier.control.discipline.change`
- 默认值调整必须同步更新 `docs/slice1-control-knobs.md` 的第 4 行

## Considered Options

- **无限重试 + 外部限流**：被拒。外部限流（飞书 webhook 速率）到达时再退避已经太晚，且会把 rule-engine 评估带进外部速率影响面。
- **把抑制/去重放进 Notifier**：被拒。抑制属于告警链路治理（Slice 3），放在 Notifier 会让"我没收到告警"变成"不知道是规则没命中、是 Notifier 压下了、还是外部没收到"——故障归因面扩大。
- **dramatiq 默认重试 + Notifier 层不再重试**：被拒。dramatiq 的失败语义是"任务执行失败"，但飞书/SMTP 的"4xx 客户端错误" vs "5xx 服务端错误"必须由 Notifier 自己判断是否重试；依赖 dramatiq 默认会把 4xx 也重试，污染外部服务。

## Consequences

- Epic 16 child `#1` 的 `Notifier` Protocol 必须暴露可测试的 `pending_dispatch_count`、`per_channel_health` 读取接口，否则 anti-windup / 通道暂停逻辑无法验证
- Epic 16 child `#4` 的回归测试 `tests/rule_engine/test_dispatch_backpressure.py` 必须覆盖：
  - Notifier 全失败时 rule-engine p95 不回归
  - pending 达到 500 时新 dispatch 返回 `dropped`
  - 通道连续失败 10 次后进入 60s 暂停
- `notify_history.status` 枚举扩展：至少包含 `delivered | failed | dropped | paused_channel`
- Slice 3（告警成熟度）必须回顾本 ADR 的"本切片不做合并"承诺，决定是否升级
- 本 ADR 的所有数字在演练后必须回写真实观察；如果默认值严重不匹配，开 ADR-00XX supersede 相关条款
