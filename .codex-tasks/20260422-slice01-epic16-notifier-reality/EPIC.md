# Epic 16 — Notifier Reality & Slice-1 Production Rehearsal

> Status: **planned**（由 post-Epic-15 transition review 激活）
> Slice: 1 / 8（最后一个子 epic）
> 前置依赖: Epic 15 关闭（offline signoff 通过）
> 后置继任: Slice 2 planning materialization（OS 指标 + 多实例分组）

## Goal

让 Slice 1 从"功能接近 Lepus 的演示态"跨到"真能替代 Lepus 值一次班的投产态"：

- 告警不再只是"规则命中 → 落库"，而是**真的送达飞书/邮件**
- 真人（DBA）**跑一次值班演练**，在 4 种典型故障下走完 观测 → 告警 → 响应 → 关闭 的完整链路
- 把 Slice 1 的投产许可以证据的形式写回 `CONTEXT.md` Slice sequence

## Why This Epic Is Next

Slice 1 在 Epic 15 之后的状态：

- 监控深度已补齐（processlist、slow query、tablespace、per-instance overrides）
- 但规则命中后**没有任何外部感知**——只有库里一条记录
- 以 Lepus 对标：Lepus 的告警链路本身是其核心价值（飞信短信 + 邮件模板），我们不做完这一段不能说"Slice 1 能替 Lepus"

Epic 16 是 Slice 1 的**事实上的上线门**——在这之前所有工作都是"代码可运行"，Epic 16 之后才是"业务可依赖"。

## Scope

1. **Notifier 抽象层**
   - 统一的 `Notifier` Protocol：`async def send(payload: NotifyPayload) -> NotifyResult`
   - 按 channel 注册的 pluggable factory；规则 → channel 的绑定走 `alert_channel_bindings`
   - 超时 / 重试 / 失败降级独立于 rule-engine（见 ADR-0003 Notifier 边界）

2. **飞书通道（主）**
   - Webhook 发送（签名校验）
   - 富卡片格式（title + 指标 + 命中值 + 跳转链接）
   - @群成员（at_user_ids 配置）
   - 重试 3 次，指数退避；全部失败时降级到 SMTP + 记 `notify_failures`

3. **SMTP 通道（备）**
   - 基础 HTML 模板（对齐 Lepus `lepus_alarm_mail_content` 字段但**不**抄实现）
   - SMTP server 配置从 `.env` / settings 取，**不**入库
   - Feishu 不可达时自动接手

4. **端到端集成**
   - Rule-engine 命中 → NotifyPayload → Notifier 发送
   - Notifier 超时（默认 5s）**不**回压 rule-engine 评估循环；采用 fire-and-forget + 异步追踪
   - `notify_history` 表：rule_id, instance_id, channel, status, attempted_at, delivered_at, error

5. **Slice 1 投产值班演练（signoff）**
   - 1 名 DBA 真人值 4 小时，覆盖 4 种故障场景：
     a) MySQL 连接数打满（max_connections 触发）
     b) MySQL 从库复制延迟（pt-heartbeat > 阈值）
     c) MySQL 慢查询阻塞（kill 回路验证）
     d) Oracle 表空间 > 85%（override 过的阈值）
   - 每场景必须走完：**飞书告警送达 → DBA 在 web 上看到 → 采取动作 → 告警自动 / 手动消除**
   - 演练报告写入 `.codex-tasks/20260422-slice01-epic16-notifier-reality/REHEARSAL_REPORT.md`

## Non-Goals

- WeCom（企业微信）通道 —— 切到 Slice 2 或按需
- SMS 通道 —— Slice 2+；本切片显式不做
- 告警抑制 / 静默窗口 —— Slice 3（告警生命周期专切片）
- 告警升级链 / 轮询值班表 —— Slice 3
- 告警模板全字段自定义 —— Slice 3；本切片只做内置飞书卡 + SMTP HTML
- 多租户通道配置 UI —— Slice 4（多租户切片）

## Done-When（Close-Out Gate）

所有条件 **AND**：

- `pnpm test:notifier:signoff`（新 gate）全绿
- `pnpm test:hardening:signoff` 仍全绿（无回归）
- `notify_history` 表上线，`test:schema:bootstrap` 覆盖
- 4 个场景演练报告全部 PASS，`REHEARSAL_REPORT.md` 由值班 DBA 签字（txt 签字即可）
- `CONTEXT.md` 的 Slice sequence 将 Slice 1 状态从 `in-progress` 改为 `done`
- `EPIC_ROADMAP.md` Epic 15 + 16 都标 DONE，Slice 2 planning materialization 已开

## Project Control Topology

- 本 epic 目录: `.codex-tasks/20260422-slice01-epic16-notifier-reality/`
- Child 目录数: 5
- 并行度: child #1 → (#2 ∥ #3) → #4 → #5
- 关键路径: #1 Notifier 抽象 → #4 端到端 → #5 演练 signoff

## Complexity Transfer Ledger

本 Epic 主要做一次复杂性"从人工值班链路 → 系统自动通知链路"的转移。记账如下：

| 字段 | 说明 |
| --- | --- |
| 复杂性原位置 | DBA 侧人工值班：规则命中→自行看 lepus 后台/SSH→判断是否真故障→人工通知同事 |
| 新位置 | db-monitor 内部：rule-engine 命中 → `notification.service.dispatch` → 飞书/SMTP channel → `notify_history` 状态面 |
| 收益 | 告警从"人轮询"变成"push 到群"，响应时延从分钟级降到秒级；告警送达成为可审计事实（`notify_history`），而不是靠人回忆 |
| 新成本 | 新增 `notify_history` PG 表与迁移；新增 Notifier Protocol + 飞书/SMTP adapter 的长期维护；飞书 webhook / SMTP 凭据成为运行期依赖；rule-engine → Notifier 的异步边界必须持续被 anti-windup 保护（见 ADR-0009） |
| 失效模式 | 飞书服务抖动导致告警静默；SMTP 发件信誉被外部评级下调；Notifier task 堆积反压 rule-engine 评估循环；单事件内降级策略误触发导致重复投递；签字演练用的测试规则在真实环境被遗忘留作"告警源" |

### 次级复杂性转移：Rule-Engine 评估循环 → Fire-and-Forget

| 字段 | 说明 |
| --- | --- |
| 复杂性原位置 | rule-engine 评估循环内部直接 `await notifier.send(...)`，同步等待外部网络 |
| 新位置 | `asyncio.create_task` / dramatiq 任务队列（child `#4` 决定哪个）+ `notify_history.attempt` 显式记录每次投递 |
| 收益 | rule-engine p95 不受外部服务拖累；可独立重试失败投递；送达状态持久化 |
| 新成本 | 需要引入 task 队列上界（anti-windup）；失败重放需要依赖 `notify_history.status` 而非内存状态；调试链从"同步堆栈"变为"事件序列" |
| 失效模式 | 无界 task 创建导致内存膨胀；task 失败静默吞；重放逻辑与"单事件内降级"冲突导致双投 |

## Complexity Decomposition Ledger

本 Epic 内部的复杂性下放路径（child 分工）：

- Notifier 超时策略下放 child `#4`
- 飞书签名 / 卡片格式下放 child `#2`
- SMTP HTML 模板下放 child `#3`
- 4 场景演练剧本下放 child `#5`（由 SPEC.md 提供分场景 runbook）
- anti-chatter / anti-windup / 退避上界由 ADR-0009 统一锁定，child `#1`/`#4` 的实施必须遵守

## Control Contract

- 同一时间 **≤1** 个 child IN_PROGRESS
- Non-goal 变动必须经 ADR 或回写本 EPIC.md Scope
- Notifier 故障不得阻塞 rule-engine p95（硬边界）
- 演练签字后不可回撤——Slice 1 DONE 一旦写入 `CONTEXT.md` 就进入 Slice 2 planning materialization，不走"重开 Slice 1"这条路

## Close-Out Review 模板（填写于收尾时）

1. Slice 1 投产能力 vs Lepus 的实际覆盖率（按 `CONTEXT.md` never-reimplement list + slice sequence 对照）
2. 演练中暴露的未覆盖场景 → 决定进 Slice 2/3 哪个切片
3. Notifier 抽象是否需要调整（WeCom / SMS 接入前的预留点）
4. ADR 是否需要更新或新增（例如演练暴露的新边界）

## Child Deliverables

见 SUBTASKS.csv。

## Dependency Notes

- **硬依赖**: Epic 15 全部 DONE（监控深度 + per-instance overrides + offline signoff）
- **共享组件**: 复用既有 `alerting.evaluation.RuleEngine` 的 hit event 产出；**不**改评估核心
- **数据库**: 新增 `notify_history`（PG）；迁移脚本纳入 `test:schema:bootstrap`
