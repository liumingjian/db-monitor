# Epic Roadmap

## Purpose

这个文件定义产品级的 epic 路线图，解决两个问题：

- 当前 `mysql phase-one epic` 完成后，团队默认该往哪里走
- 哪些后续 epic 现在只需要顶层边界，哪些必须等到激活时再细化

它遵循 `taskmaster` 的执行理念：只有 `active epic` 会展开为完整的
`EPIC.md + SUBTASKS.csv + child task` 结构；未来 epic 在未激活前，只保留
顶层 brief、激活条件和延后理由。

## Planning Policy

- `Active`: 当前正在执行的 epic，必须拥有完整执行骨架和验证命令
- `Done`: 已完成并通过 signoff 的历史 epic，保留为路线图与 close-out review 的证据锚点
- `Default Next`: 当前 epic 默认交接到的下一个 epic
- `Conditional Next`: 存在明确价值，但是否优先取决于当前 epic 完成后的真实证据
- `Later`: 已确认方向，但不应早于前置能力稳定
- `Deferred`: 有潜在业务价值，但当前阶段不应投入

切换规则：

- 关闭当前 epic 时，先做一次显式 `epic close-out review`
- close-out review 只允许在已有 roadmap 中调整优先级，不允许临时发明新大方向
- 被激活的 future epic 才能创建自己的 `.codex-tasks/<epic-name>/EPIC.md` 与 `SUBTASKS.csv`
- 如果 roadmap 中所有 epic 都已 `Done`，则必须先基于显式 repo gap 扩展 roadmap，再激活新的 epic

## Roadmap Snapshot

| Order | Epic | State | Why this position |
|---|---|---|---|
| 01 | MySQL-First Phase One Control Plane | Done | phase-one 的控制面、数据面和前端主路径已跑通并完成根级签收 |
| 02 | Operational Hardening and Delivery Readiness | Done | runtime、schema、recovery、release 和 hardening signoff 已闭环 |
| 03 | Alert Maturity and On-Call Workflow | Done | alert lifecycle、suppression、on-call actions、triage 与 signoff 已闭环 |
| 04 | Analytics and Capacity Insight Expansion | Done | MySQL analytics depth、capacity semantics、presets 与 signoff 已闭环 |
| 05 | Multi-Engine Expansion and Abstraction Validation | Done | Oracle onboarding / validation 与 engine-aware seam 已证明成立，但 data-plane parity 仍开放 |
| 06 | Tenant and Organization Governance | Done | 用户显式批准的组织治理边界已收敛到 auth、control-plane、alerting 与 web |
| 07 | Oracle Data Plane and Minimum Insights | Done | Oracle 已不再停留在 validation-only，最小 collector / analytics / web detail / signoff 闭环已完成 |
| 08 | Engine-Aware Overview and Fleet Diagnostics | Done | engine-aware overview payload、web surface、presets 与根级 signoff 已闭环，mixed-engine fleet baseline 已成立 |
| 09 | Multi-Engine Alerting and Rule Semantics | Done | multi-engine rule contract、API、pipeline、web、notifier 与 root signoff 已闭环；当前 roadmap 已耗尽，后续必须先做 close-out 与 roadmap extension |

## Current Status

- 截至 `2026-04-21`，roadmap 中 01-09 已全部 `Done`
- 当前没有 active epic；如果继续进入产品实现，必须先基于显式 repo gap 扩展 roadmap
- 本轮 close-out 额外补了一份 [docs/prd-closeout.md](docs/prd-closeout.md)，用于解释：
  - 原始 `PRD.md` 的 phase-one 需求哪些已经完成
  - 哪些能力已经明显超出原始 PRD
  - 当前仍未补齐的 repo gap 是什么

## Epic 01: MySQL-First Phase One Control Plane

### Goal

- 跑通 `登录 -> MySQL 实例接入 -> dashboard -> 实例详情 -> 告警/规则 -> 设置`
  的最小内部产品闭环

### Why This Epic Exists

- 它建立整个系统的核心边界：`FastAPI` 业务 API、`PostgreSQL` 控制数据、
  `ClickHouse` 分析数据、`Redis` 任务分发、`scheduler + worker + rule-engine + notifier`

### Exit Signals

- 主路径 smoke 通过
- OpenAPI 契约、集成测试和根级质量门禁通过
- 控制面、数据面和前端主路径已经可被内部用户验证

### What It Does Not Prove Yet

- 发布/升级/恢复是否足够稳
- 告警是否足够成熟且不会造成噪音
- 当前统一指标模型是否真的可以支撑多引擎
- 更深层分析和容量洞察是否已满足用户

## Epic 02: Operational Hardening and Delivery Readiness

### Goal

- 把系统从“能跑通 phase-one”提升到“可持续运行、可发布、可恢复”

### Why This Epic Should Be Default Next

- 大多数新平台在第一阶段之后，真正暴露的问题不是“缺更多页面”，而是：
  发布是否稳定、迁移是否安全、worker 是否幂等、任务失败如何恢复、平台自身如何被监控

### Activation Gates

- Epic 01 已完成或接近完成，主路径已可用
- 团队已经掌握真实运行问题，而不是假设性担忧
- 当前系统的主要风险开始集中在运维稳定性、发布流程、恢复与可观测性

### Top-Level Scope

- 部署与环境管理基线
- 数据迁移/版本演进策略
- worker/scheduler 的重试、幂等与失败恢复
- 平台自监控、日志、追踪和关键 SLO
- 发布前检查与回滚演练

### Non-Goals

- 不扩展多引擎
- 不新增复杂业务功能
- 不把问题伪装成 fallback 或 silent degradation

### Done-When

- 平台具备明确的发布、升级、失败恢复和自监控能力
- 核心运行链路出现故障时，团队知道怎么发现、定位、恢复

## Epic 03: Alert Maturity and On-Call Workflow

### Goal

- 把基础告警能力提升为可被值班团队长期使用的告警系统

### Why It Is Conditional Next

- 如果 Epic 01 结束后，最大痛点是告警过多、恢复语义混乱、通知不可用或值班成本高，
  那么它应该优先于更深分析或多引擎扩展

### Activation Gates

- 基础规则、告警记录和 notifier 已存在
- 团队已经通过真实使用，确认主要问题来自告警质量而非平台稳定性
- 告警噪音、抑制、分级或值班流转已经成为主要产品阻塞

### Top-Level Scope

- 告警去重、抑制、分级与聚合策略
- 告警确认、恢复、备注和处理流程
- 通知渠道可靠性与失败重试策略
- 值班视图和面向处理流程的告警交互

### Non-Goals

- 不引入复杂 DSL 作为第一优先级
- 不把告警成熟度问题误解为“多加几个通知渠道”

### Done-When

- 告警能被运维团队长期使用，而不会快速沦为噪音源
- 值班链路从触发到恢复具备一致语义

## Epic 04: Analytics and Capacity Insight Expansion

### Goal

- 在稳定核心监控的基础上，增强查询深度、趋势洞察和容量判断能力

### Why It Is Conditional Next

- 如果内部用户已经认可基本监控闭环，但开始强烈要求更深趋势分析、
  资源画像和容量视角，那么该 epic 的价值会显著上升

### Activation Gates

- Epic 01 的 overview 和 instance detail 已经被实际使用
- 团队确认用户主要缺口是“看得不够深”，而不是“系统不够稳”
- ClickHouse 查询模型已足够稳定，值得向上扩查询能力

### Top-Level Scope

- 更丰富的时间窗口、聚合粒度和对比视图
- 容量趋势、增长斜率和资源风险提示
- 更稳定的 saved views / dashboard presets
- 面向 MySQL 运维的深入但仍聚焦 phase-two 的分析视图

### Non-Goals

- 不变成通用 BI 平台
- 不在数据模型不稳定时盲目堆报表页面

### Done-When

- 用户能用系统回答“现在怎样”和“未来一段时间可能怎样”这两类问题
- 分析能力建立在稳定数据模型上，而不是页面层拼装

## Epic 05: Multi-Engine Expansion and Abstraction Validation

### Goal

- 验证当前平台边界是否真的支持第二种数据库引擎，而不是停留在 MySQL 假设下的伪抽象

### Why It Must Be Later

- 在 MySQL 之外扩展前，必须先确认统一指标模型、worker 契约、控制面资产模型和告警模型
  已经在第一引擎上稳定成立。否则第二引擎只会暴露抽象失真。

### Activation Gates

- Epic 01 已完成并稳定运行一段时间
- Epic 02 至少已解决最关键的可运维性问题
- 团队已选定一个明确的第二引擎，而不是“都支持”
- 经过架构复盘，确认需要的是扩展，不是重写 MySQL 特化设计

### Top-Level Scope

- 第二引擎的资产模型扩展
- 指标统一模型的有效性复盘
- 第二类 worker 与规则映射
- 前端对多引擎差异的可控承载方式

### Non-Goals

- 不追求一次性全引擎覆盖
- 不在抽象未稳定前追求平台“通用性表面正确”

### Done-When

- 第二引擎作为真实试金石，验证平台是否具备可持续扩展能力
- 团队知道哪些抽象是成立的，哪些必须维持引擎特化

## Epic 06: Tenant and Organization Governance

### Goal

- 在业务明确需要时，引入租户、组织、隔离和治理能力

### Why It Is Deferred

- `PRD.md` 已明确 phase-one 是内部单租户；过早引入多租户会污染权限模型、
  配置模型、告警模型和前端边界，且当前没有收益

### Activation Gates

- 单租户模型已经成为真实业务阻塞，而不是架构焦虑
- 产品方向确认需要组织/租户隔离
- 团队准备接受权限、配置、数据边界和运行模型的系统性变化

### Top-Level Scope

- 组织/租户边界
- 权限与资源隔离
- 配置和告警归属模型
- 数据隔离与查询边界

### Non-Goals

- 不为了“以后可能会用”而预埋复杂多租户结构
- 不在当前内部单租户阶段引入额外抽象负担

### Done-When

- 多租户能力由明确产品需求驱动，而不是由抽象洁癖驱动

## Epic 07: Oracle Data Plane and Minimum Insights

### Goal

- 把 Oracle 从当前“能接入、能校验”推进到“能采集、能查询、能最小呈现”的真实第二引擎 data-plane baseline

### Why It Is Active Next

- 原始 roadmap 01-06 已全部完成，继续开发前必须先基于真实 repo gap 扩展路线图
- Epic 05 与 Oracle live gate 已证明 control-plane onboarding / validation baseline 成立
- 当前仓库内最持续、最显式的剩余 gap 已集中在：
  - Oracle telemetry 未进入 scheduler / worker / sink 闭环
  - ClickHouse metrics state-plane 仍是 mysql-only 语义
  - analytics API 和 web detail 仍只承载 MySQL trend semantics

### Activation Gates

- Epic 05 与后续 Oracle live gate 已关闭 control-plane 层的“只靠 static validator”缺口
- Epic 06 已完成，不再是当前主误差
- MySQL 主链与治理主链已经足够稳定，可以承受第二引擎最小 data-plane 扩展

### Top-Level Scope

- engine-aware metric sample / ClickHouse schema baseline
- Oracle collector / worker / dispatch 的最小闭环
- Oracle instance trends 的最小 analytics API
- web detail flow 的最小 Oracle trend 呈现
- root signoff 与 live gate 收口

### Non-Goals

- 不追求 Oracle 全量产品 parity
- 不在这一轮扩展 Oracle alerting / rule-engine parity
- 不把 overview fleet semantics 一次性强行做成跨引擎完全一致

### Done-When

- 已验证的 Oracle 实例可以进入真实采集链路并产出最小 telemetry
- analytics API 与 web detail 不再把 Oracle 停留在 validation-only
- MySQL 主链、组织治理主链和现有根级门禁不回归

## Epic 08: Engine-Aware Overview and Fleet Diagnostics

### Goal

- 把当前 Oracle “detail 已最小可见、overview 仍 MySQL-first”的断层推进为一个真实的 mixed-engine fleet overview 与 diagnostics baseline

### Why It Is Active Next

- Epic 07 已证明 Oracle 最小 data-plane 成立，因此当前主误差不再是“是否能采到数据”，而是“采到的数据能否被 fleet-level product semantics 诚实承载”
- 当前仓库中最显式的剩余 seam 已集中在：
  - `OverviewResponse` / `OverviewInstanceResponse` 仍没有 `engine` 维度
  - overview cards / leaders / presets / copy 仍主要围绕 MySQL throughput、replication lag、buffer-pool pressure 叙述
  - web 上已明确写出 Oracle overview semantics 和 deeper diagnostics remain `MySQL-first`
- 相比之下，multi-engine alerting 仍涉及更重的共享契约改动，不应早于 overview semantics 的收敛

### Activation Gates

- Epic 07 已完成，Oracle live gate 与 root signoff 已通过
- MySQL 主链和组织治理主链在同一轮 signoff 中保持 green
- 仓库中对“overview 仍 MySQL-first”的显式文案与 contract seam 已可直接定位

### Top-Level Scope

- 为 overview payload、instance snapshot 与 dashboard model 增加真实 `engine-aware` 语义
- 把 overview aggregation / cards / charts 从“只对 MySQL 自洽”推进到“对 mixed-engine fleet 诚实可读”
- 让 web overview surface、fleet messaging、leaders 与 presets 不再把已支持的 Oracle 数据面表述成隐式 MySQL-only
- 增加更深但仍克制的 engine-aware diagnostics 说明，不伪装成 full parity
- 为本 epic 形成 root signoff 与 live Oracle coverage 证据链

### Non-Goals

- 不在本 epic 中完成 multi-engine alerting / rule-engine parity
- 不追求 Lepus 级别的 Oracle 全量报表或 deep-dive 诊断
- 不把 engine-aware overview 扩成通用 BI 平台
- 不回退 Epic 07 已关闭的 Oracle data-plane 主链

### Done-When

- overview payload 与 web surface 能诚实表达 mixed-engine fleet state，而不是继续把 Oracle 支持面藏在 detail-only 路径里
- Oracle / MySQL fleet overview 的已支持语义不再显式停留在 `MySQL-first`
- MySQL detail / alerting 现有语义未因 overview 扩展发生回退

## Epic 09: Multi-Engine Alerting and Rule Semantics

### Goal

- 把当前仍围绕 MySQL 指标名与 MySQL 运维语义组织的 rule / alert contract，推进到真正可承载多引擎运营的语义基线

### Why It Is Next

- 当前仓库已显式暴露这条 gap：
  - rule form placeholder 仍是 `mysql_replication_lag_seconds`
  - alerting contract tests 与 integration pipeline 仍主要围绕 MySQL replication-lag 语义组织
- Epic 08 已完成后，这类改动不再被 overview baseline 不稳定所阻塞
- 但这类改动仍会同时触碰 rule semantics、API contract、UI form、notifier expectations 与值班语义，因此必须先以最小可验证变更方式 materialize 成一个完整 active epic

### Activation Gates

- Epic 08 已把 mixed-engine fleet overview 与 diagnostics baseline 收敛到稳定语义
- 团队确认下一阶段主误差已从“fleet-level insight 不一致”转移到“rule / alert semantics 无法表达第二引擎”
- 已有足够证据选定最小 Oracle alerting surface，而不是盲目扩大全引擎范围

### Top-Level Scope

- 规则 contract 与 metric selection 从 MySQL-only 语义推进到 engine-aware baseline
- Oracle 最小告警 surface、API contract、web form 与 notifier 语义
- 多引擎告警链路的 root signoff

### Non-Goals

- 不追求所有引擎、所有指标的一次性 parity
- 不重写整个 alert maturity stack
- 不在没有清晰运营语义前盲目引入复杂 DSL

### Done-When

- 团队可以用统一但诚实的方式为多引擎配置最小规则与告警语义
- MySQL 现有 alert maturity 主链未被回退

## Close-Out Review Template

每个 active epic 结束时，都要回答以下问题，再决定是否按默认顺序推进：

1. 当前系统最大的真实风险是在稳定性、告警质量、分析深度，还是引擎扩展？
2. 哪个问题如果不先解决，会让下一波开发明显返工？
3. 当前数据模型、API 契约和运行模型，哪些已经稳定，哪些仍在抖动？
4. 是否存在足够强的证据，支持跳过 `Default Next` 而进入某个 `Conditional Next`？

如果没有强证据，默认进入 `Epic 02: Operational Hardening and Delivery Readiness`。

如果 01-06 都已 `Done`，则默认动作不再是“自动跳到下一个旧 epic”，而是：

1. 先写明旧 roadmap 已经耗尽
2. 再基于显式 repo gap 扩展 roadmap
3. 最后激活新的 active epic
