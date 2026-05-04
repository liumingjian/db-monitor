# Epic — Slice 2: Alert Maturity & Notification Surface Expansion

> Status: **Active**（由 post-Slice-1 planning materialization 激活）
> Slice: 2 / 8
> 前置依赖: Slice 1 关闭（Epic 15 + Epic 16 代码侧 DONE，演练 deferred 不阻塞）
> 后置继任: Slice 3 — OS/SNMP 第三引擎（planned）
> 估时: 2-3 周
> 决策来源: `CONTEXT.md` Slice sequence（2026-04-22 locked）+ ADR-0013 / 0014 / 0015（draft，本 epic 启动前 Boss 决议）

## Goal

把告警从 Slice 1 收尾的"飞书 + SMTP 两通道、相同事件可能反复打扰"的现状，推进到：

- 通道面：覆盖 DBA 团队主流通讯（飞书 + 企业微信 + SMTP + SMS 四通道）
- 噪音面：相同事件不再无脑重复（rule × instance × severity 三元组 dedup + 抑制窗口）
- 可审计面：所有规则改动 / 实例改动 / binding 改动都有可追溯链

不引入新引擎、不重写 rule-engine 评估核心、不做完整 DSL。

## Why This Epic Is Next

Slice 1 关闭后的 Slice 2 是默认下一个，依据：

- Epic 16 已让"规则命中→真到达"成立；下一层缺口已转移到"通道覆盖不全 + 告警吵 + 改动无审计"
- ChannelRegistry / DispatchCoordinator 抽象一次成立、N 次复用，扩 WeCom / SMS 是无架构返工的最小新通道
- lepus `alarm_temp` 历史方案是去重 + 抑制的成熟参考；本 epic 用 `notify_history` 复用而非新表
- 客户验收前 Slice 2 完成可让"告警链路真正能值班"，不再需要靠人盯飞书

## Scope — In

1. **WeCom（企业微信）通道**（child #1）
   - `apps/api/.../channels/wecom.py`
   - webhook + markdown 卡片 + @user/@mobile + 3 次指数退避
   - `alert_channel_bindings.channel` 枚举扩值
   - 详见 ADR-0013

2. **SMS 通道（阿里云）**（child #2）
   - `apps/api/.../channels/sms.py` + `SmsProvider` Protocol（YAGNI：单 provider，不预埋多家）
   - 模板 + sign_name 配置 + `DB_MONITOR_ALIYUN_SMS_*` env 注入
   - 1 次重试（计费谨慎）+ fallback SMTP
   - 详见 ADR-0013

3. **告警去重 + 抑制窗口**（child #3）
   - dedup key = `(rule_id, instance_id, severity)`
   - 默认 10 分钟抑制窗口；`alert_rules.suppression_window_seconds` 字段做 per-rule override
   - `notify_history.status='suppressed'` + `suppressed_for` 字段；不新增并行表
   - DispatchCoordinator 入口判定，不下放到 channel
   - schema v11 → v12
   - 详见 ADR-0014

4. **审计范围扩展**（child #4）
   - `audit_entries.target_type` + `diff_summary` 字段
   - 新增 11 个 action 枚举（rule.create/update/delete、override.upsert/delete、instance.create/update/delete、validation.update、channel_binding.create/delete）
   - service 层 explicit `audit_service.log(...)` 注入
   - web Audit 页加 4 维过滤
   - schema v12 → v13
   - 详见 ADR-0015

5. **离线 signoff + 新能力 smoke**（child #5）
   - 新增 `pnpm test:slice02:signoff` gate（lint + typecheck + ruff + mypy + pytest + 4 通道烟测 + dedup smoke）
   - 不含真人演练（仍归客户验收前窗口）
   - `CONTEXT.md` Slice 2 状态从 Active → Done
   - `EPIC_ROADMAP.md` 更新

## Scope — Out（明确推后）

- **告警升级链 / on-call 轮询**：推 Slice 3（告警生命周期专切片）
- **"告警自动恢复后通知"语义**：推 Slice 3
- **PostgresBindingRepository（binding 持久化）**：推 Slice 3；当前仍 in-memory
- **跨 rule 的去重 / 内容相似度去重**：本 epic 显式不做；只做 (rule × instance × severity) 三元组
- **SMS 多 provider 抽象 / 国际短信 / 群发**：YAGNI 先单 provider
- **WeCom 富卡片 / 应用消息 API**：仅 webhook 路径，不接消息中心
- **新引擎（OS/SNMP/SQLServer/Redis）**：推 Slice 3-7
- **审计 TTL / 归档策略**：推 Slice 3+

## Done-When（Close-Out Gate）

所有条件 **AND**：

- `pnpm test:slice02:signoff`（新 gate）全绿
- `pnpm test:notifier:signoff` + `pnpm test:hardening:signoff`（离线段）仍全绿（无回归）
- `notify_history.status='suppressed'` 在 dedup smoke 中真正命中
- `audit_entries` 11 个新 action 至少各被一次集成测试覆盖（target_type + diff_summary 字段断言）
- WeCom + SMS 两通道都有"无凭据 → 自动跳过；有凭据 → 真投递"的 unit + integration 双段测试
- `EPIC_ROADMAP.md` Slice 2 状态从 Active → Done
- `CONTEXT.md` Slice sequence 更新

## Project Control Topology

- 本 epic 目录：`.codex-tasks/20260504-slice02-alert-maturity-epic/`
- Child 目录数：5
- 并行度：child #1 ∥ #2（两通道独立）→ #3（dedup 用到 binding 抽象）→ #4（audit 用到 channel binding action）→ #5
- 关键路径：#3 dedup 是用户感知最强的能力；#5 是收口闸门

## Control Contract

- 同一时间 **≤1** 个 child IN_PROGRESS
- Non-goal 变动必须经 ADR 或回写本 EPIC.md Scope
- 不破坏 Epic 16 的 fire-and-forget 边界（rule-engine p95 不受 dedup / 通道扩张拖累）
- 不重新激活 Slice 1 child #5 演练（演练仍 deferred，由客户验收前窗口承担）

## Complexity Transfer Ledger

| 字段 | 说明 |
| --- | --- |
| 复杂性原位置 | DBA 侧人脑去重："这条飞书 5 分钟前我已经看到了，不用再看" |
| 新位置 | `DispatchCoordinator` 入口的 dedup 判定 + `notify_history.suppressed_for` 持久化 |
| 收益 | 告警噪音从"靠人忽略"变成"系统集中决定"；可通过 `notify_history` 审计判断"为什么没收到第二条" |
| 新成本 | dedup 判定路径成为 Notifier 关键路径；判定 bug 会让"应该触发的告警被吞" |
| 失效模式 | 抑制窗口配置过宽 → 真事故被静音；dedup key 误把不同事件归并；`notify_history` 查询慢 → 影响投递 p95 |

## ADR References

- ADR-0013 WeCom + SMS 通道（child #1/#2 实现依据）
- ADR-0014 告警去重 + 抑制窗口（child #3 实现依据）
- ADR-0015 审计范围扩展（child #4 实现依据）
- ADR-0009 Notifier dynamic control discipline（仍生效；本 epic 不改 anti-windup 边界）

## Child Deliverables

见 SUBTASKS.csv。

## Dependency Notes

- **硬依赖**：Slice 1 Epic 15 + Epic 16 代码侧 DONE（已满足）
- **共享组件**：复用 ChannelRegistry / DispatchCoordinator / NotifyHistory / audit_entries
- **数据库**：schema v11 → v13（child #3 + child #4 各跳一版）
- **不依赖**：客户演练、Lighthouse Perf 重跑（这两件归客户验收前窗口）
