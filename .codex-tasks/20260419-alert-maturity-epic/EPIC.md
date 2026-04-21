# Epic Specification

## Goal

- 把当前基础规则告警提升为可被值班团队长期使用的告警系统
- 让告警从“触发并发通知”演进到“可去噪、可认领、可追踪、可恢复”的一致工作流

## Non-Goals

- 不扩展第二种数据库引擎
- 不把告警成熟度问题误解为单纯增加通知渠道数量
- 不引入复杂 DSL 或 silent fallback 伪装告警可靠性

## Control Contract

- **Primary Setpoint**
  - 值班人员可以围绕同一条告警完成 `触发 -> 去噪 -> ack/owner/note -> 恢复` 的一致处理闭环
- **Acceptance**
  - 告警状态契约测试、值班动作 API 测试、Web 告警页面测试，以及 PostgreSQL alert live gate 与 epic signoff 全部通过
- **Guardrail Metrics**
  - 不破坏 Epic 02 已建立的 runtime readiness、schema bootstrap、recovery gate 与 smoke baseline
- **Sampling Plan**
  - 先跑 L0 的 domain/repository/unit，再跑 L1 的 API/Web/integration，最后跑 L2 的 PostgreSQL live gate 与 root signoff
- **Known Delays / Delay Budget**
  - notification retry、scheduler/rule evaluation 与前端 revalidate 存在天然时滞，必须以持久化状态为准，而不是瞬时 UI 结果
- **Recovery Target**
  - 若新 workflow 破坏告警主链，应在一次 signoff 周期内回退到当前 open/resolved 基线并保留失败证据
- **Rollback Trigger**
  - 出现告警丢失、重复通知失控、ack/owner 状态漂移，或任一 hardening/live gate 回归时立即停止推进
- **Constraints**
  - 真实状态只能以 PostgreSQL 告警事实源为准；禁止引入 UI 本地真相源或 notifier 假成功路径
- **Boundary**
  - 允许修改 `apps/api/src/db_monitor_api/alerting`、相关 schema/runtime/router、OpenAPI/client、`apps/web/app/alerts`、相关 tests/gates/scripts/docs
- **Coupling Notes**
  - 本 epic 同时耦合 alert domain、PostgreSQL state、notification delivery、typed client 与 Web triage flow
- **Approximation Validity**
  - in-memory repository 只证明语义，不证明 schema/persistence/live gate；任何状态字段新增都必须经过 PostgreSQL gate
- **Actuator Budget**
  - 本轮允许修改 domain、repository、schema contract、API、Web、tests、live gates 与运行文档
- **Risks**
  - 状态机扩展可能打穿既有 persistence contract
  - 去噪策略若不显式留痕，容易演化为 silent drop
  - Web/API 契约扩展可能与 typed client 生成节奏失配

## Close-Out Review

- Epic 02 已证明：
  - 平台具备显式 runtime readiness、schema bootstrap、后台进程入口、retry/recovery guards 与 release/signoff baseline
  - PostgreSQL、ClickHouse、Redis 的 live gates 已形成稳定最小门禁，不再是下一波开发的首要不确定性
- Epic 02 未证明：
  - 告警是否具备去噪、确认、认领、备注、抑制与值班流转语义
  - 通知失败后的值班行为是否可持续，而不只是技术上可重试
  - 值班团队是否能用当前 `/alerts` 列表和详情页完成真实处置
- Roadmap 默认裁决：
  - 从 `EPIC_ROADMAP.md` 激活 `Epic 03: Alert Maturity and On-Call Workflow`
- 选择理由：
  - 运行时稳定性和恢复基线已建立，当前最大的真实缺口不再是“系统能否跑起来”，而是“告警是否值得长期信任和使用”
  - 现有告警域模型只有 `open/resolved` 与基础通知历史，无法支撑值班流程
- 什么证据会支持跳到 `Epic 04`
  - 如果真实用户主要痛点变成分析深度、容量趋势和查询颗粒度，而不是告警噪音与处理成本，才应跳过当前 epic

## Child Deliverables

- 完成 Epic 02 close-out，并把 Alert Maturity epic 激活为新的 truth source
- 冻结告警生命周期状态契约与 persistence boundary
- 建立显式的 dedupe / suppression / grouping 噪音控制语义
- 实现 ack / owner / note / workflow 处理动作
- 建立 notifier delivery evidence、failure handling 与值班交接语义
- 扩展 API / OpenAPI / typed client / Web triage surface
- 汇总 alert maturity signoff gates 作为阶段签收入口

## Dependency Notes

- 子任务 `#1` 负责 close-out review 与 epic 激活
- 子任务 `#2` 是所有后续值班语义的状态基础
- 子任务 `#3` 与 `#4` 都依赖 `#2`
- 子任务 `#5` 依赖 `#2;#3;#4`，因为通知策略必须服从新的状态机与噪音控制
- 子任务 `#6` 依赖 `#2;#3;#4;#5`
- 子任务 `#7` 依赖 `#2;#3;#4;#5;#6`

## Child Task Types

- `single-full`

## Done-When

- [ ] `SUBTASKS.csv` 中所有激活子任务达到其 validation command
- [ ] 告警从触发、去噪、认领到恢复具备一致语义，并以 PostgreSQL 事实源为准
- [ ] 值班 API 与 Web 页面能够支撑最小处理闭环
- [ ] Alert maturity root signoff gate 可从仓库根目录复现
