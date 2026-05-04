# ADR-0014: Alarm Deduplication and Suppression Window

> Status: Draft（Slice 2 Epic 起步前 Boss 决议后转 Accepted）
> Date: 2026-05-04
> Supersedes: 无
> Related: ADR-0009（Notifier dynamic control discipline）；lepus `alarm_temp` 历史表语义参考

## Context

Epic 16 已让"规则命中 → 飞书/SMTP 真投递"成立，但告警链路缺少"同事件不要重复打扰"的语义。lepus 历史方案是 `alarm_temp` 表 + 时间窗：相同 rule × host 在 N 分钟内只发第一条，期间状态变化只更新但不再发。

`CONTEXT.md` Slice 2 范围："告警去重/抑制深化（对标 `alarm_temp`）"。

约束：

- 不做完整 DSL（保持最小可验证语义；CONTEXT.md "Non-goals" 已锁）
- 不做告警升级链 / on-call 轮询（推 Slice 3）
- 必须复用 Epic 16 的 `notify_history` 表，不新增并行状态表
- 不破坏现有 rule-engine 评估循环的 fire-and-forget 边界（ADR-0009）

## Decision

### 1. 去重 Key

- **Dedup key** = `(rule_id, instance_id, severity)` 三元组
- 同 key 在同一抑制窗口内：
  - 第 1 次评估命中 → 投递 + 写 `notify_history.status='delivered'` / `'failed'` 等
  - 第 2..N 次评估命中 → 不投递 + 写 `notify_history.status='suppressed'` + `notify_history.suppressed_for=<dedup_key>`
- 不同 severity 视为不同事件（warning → critical 升级会投第一条 critical）

### 2. 抑制窗口

- **默认窗口** = 10 分钟，从 dedup key 第一次投递成功开始计时
- **per-rule override**：`alert_rules` 表新增 `suppression_window_seconds INT NULL`（NULL = 用全局默认）
- 抑制不依赖 rule.enabled / rule.threshold；仅按 dedup key 时间窗工作
- 窗口结束后下一次命中重新投递并启动新窗口

### 3. 状态机

```
命中 ──┬─→ [无活跃 dedup key] → 投递 → 写 dedup state (key, first_at=now)
       └─→ [有活跃 dedup key] ──┬─→ now < first_at + window → 抑制 + suppressed 记录
                                 └─→ now ≥ first_at + window → 投递 + 重启窗口
```

- 状态持久化：在 `notify_history` 上加 view / 索引，**不**新增 `alarm_temp` 风格表
- 查询当前活跃 dedup key：`SELECT (rule_id, instance_id, severity), MAX(attempted_at) FROM notify_history WHERE status='delivered' GROUP BY ...`
- 窗口判断在 `DispatchCoordinator` 入口做，不下放到 channel
- 与 ADR-0009 anti-windup 不冲突：anti-windup 防 task 堆积，dedup 防业务投递重复，两者职责正交

### 4. Schema 变更

- `alert_rules.suppression_window_seconds INT NULL` （default NULL）
- `notify_history.status` 新增枚举值 `'suppressed'`
- `notify_history.suppressed_for TEXT NULL` （记录 dedup_key 字符串，用于排障）
- 索引：`(rule_id, instance_id, severity, attempted_at DESC)` 加速 dedup 查询
- schema version v11 → v12

### 5. UI 呈现

- Notify history Feed 新增 `suppressed` 状态过滤
- Alert Drawer 显示"本次评估窗口内已抑制 N 次"counter
- Rules 页 detail 新增"抑制窗口"字段（数字输入 + 单位 = 分钟，默认显示"10 (全局默认)"）

### 6. 不做

- 不做基于内容相似度的去重（only 三元组 key）
- 不做跨 rule 的去重（不同 rule_id 仍各自独立）
- 不做"恢复后通知"（auto-resolve notification 推 Slice 3）
- 不做时间分段抑制（晚上更宽 / 白天更紧）

## Consequences

### Positive

- 飞书/SMTP/WeCom/SMS 四通道都自动获得去重保护，无需通道侧改造
- 抑制由后端集中决定，UI 只读，避免"前端记忆 / 后端记忆"双重事实源
- per-rule override 让运维可以按规则等级灵活调（业务低敏感规则放宽、磁盘满之类紧急规则收紧）

### Negative / Tradeoff

- 抑制状态依赖 `notify_history` 查询；高频规则会让 dedup 判定本身有开销（但仍 < 1ms/judge，承受）
- `notify_history.status='suppressed'` 写入会让表行数增长加快；TTL 仍是 30 天，需要观察容量增长曲线
- 用户可能误以为"被抑制 = 没事"，UI 必须显式标记"抑制窗口剩余 X 分钟"

### Risks

- 抑制窗口与"告警升级（warning → critical）"语义边界：本 ADR 选择 severity 进 dedup key，意味着同 rule × instance 但 severity 升级会另起窗口；运维需明确这一点
- DBA 误把"抑制"理解成"已确认"：UI 必须用不同视觉语义区分（确认 = 用户主动；抑制 = 系统自动）

## Decision Window

- 2026-05-04 起草
- Slice 2 Epic 起步前 Boss 决议；锁定后转 Accepted
