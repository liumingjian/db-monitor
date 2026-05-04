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
| 10 | PRD Debt and Control-Plane Closeout | Done | 原始 PRD 最后一批控制面欠账已通过 closeout epic 与 repo-root signoff 收口；若继续推进，需先进入新的 roadmap close-out / extension |
| 11 | Multi-Engine Fleet Metric Parity and Overview Convergence | Done | mixed-engine fleet overview 的 cards/charts/instance metrics/leaders 已收敛到诚实可验证的 parity baseline，并通过 root signoff |
| 12 | Oracle Runtime Reliability and Live-Gate Productionization | Done | Oracle runtime/live-gate 已收口为 doctor、signoff、operator baseline、diagnostics 与 rollback 的可复用基线 |
| 13 | Production Launch Readiness and Deployment Baseline | Done | release gate、deployment baseline、env/signoff contract 与 root launch signoff 已收口为内部单环境可投产基线 |
| — | **Roadmap reset**（2026-04-22） | Applied | Boss 显式将产品终极目标重置为"还原 legacy `lepus-v3.8/` 的全部能力"。原始 `PRD.md` 作废；Option B 按 slice 推进、Option A 终极。见 `docs/adr/0001-lepus-parity-pivot.md` 与 `docs/adr/0002-slice-sequence-and-engine-scope.md` |
| 15 | Slice 1 / Epic 15 — Monitoring Depth & Rule Granularity | Done | MySQL processlist+kill、slow query 短窗、Oracle tablespace、per-instance 阈值；离线 gate + smoke 已通过 |
| 16 | Slice 1 / Epic 16 — Notification Reality | Done | Notifier 抽象 + 飞书 + SMTP + dispatch fallback 已落地；真实值班演练 DEFERRED 至客户验收窗口（不阻断切片关闭） |
| 1.5 | Slice 1.5 — UI Redesign & Design System | Done | 10 张 Tier 1 页 + canonical template + 暗色主题 + 中文语言包；详见 `docs/adr/0012-ui-redesign-design-system-and-page-architecture.md` |
| S2 | Slice 2 — Alert Maturity & Notification Surface Expansion | Active | 企业微信 / 短信 / dedup+suppression / audit 扩展；详见 `.codex-tasks/20260504-slice02-alert-maturity-epic/EPIC.md`，ADR-0013/0014/0015 |
| S3 | Slice 3 — OS/SNMP 第三引擎 | Planned | SNMP 采集、host CPU/内存/磁盘/网络、per-host 阈值；6-8 周 |
| S4 | Slice 4 — SQLServer 第四引擎 | Planned | 连接/进程/等待/复制、最小告警与 web detail；3-5 周 |
| S5 | Slice 5 — MySQL 深度层 | Planned | pt-query-digest 风格 slow query 深度、bigtable、binlog auto-purge、备份监控；6-8 周 |
| S6 | Slice 6 — Oracle 深度层 | Planned | Oracle session 深入、tablespace 历史趋势；4-6 周 |
| S7 | Slice 7 — Redis 引擎 | **Conditional** | 仅在业务显式提出需求后激活；3-5 周 |
| S8 | Slice 8 — 大屏 + 报表 + 收官 | Planned | screen 大屏（overview 实时 AJAX 版）、报表邮件、admin_log 审计增强、永不复刻清单归档；3-4 周 |
| 14 | Scale, High Availability, and Disaster Recovery Hardening | Conditional（post-Slice-8） | 降级至 Slice 8 之后；只有在 Lepus Parity 达成且真实上线证据集中在容量/故障域/恢复时才激活 |

**永不复刻**：MongoDB 引擎、飞信短信、CodeIgniter widget/language/menu/license/profile/application/auth/error 控制器、`lp_mysql/awrreport` 页。

## Current Status

- 截至 `2026-05-04`，原始 roadmap 中 01-13、Slice 1（Epic 15 + Epic 16）与 Slice 1.5（UI redesign）均已 `Done`
- **2026-04-22 做了一次 roadmap reset**：Boss 把产品终极目标重置为 Lepus Parity（Option A），执行路径按 8 个 slice 推进（Option B）。原始 `PRD.md` 被显式作废，详见 `docs/adr/0001-lepus-parity-pivot.md`
- 当前 **active = Slice 2 / Alert Maturity**，骨架位于 `.codex-tasks/20260504-slice02-alert-maturity-epic/`
- Slice 1 关闭说明：Epic 15 / Epic 16 / Slice 1.5 代码侧 DONE 并通过离线 gate + smoke；**真实值班演练（4 类故障跑通）已显式 deferred 至客户验收窗口**，不阻断切片关闭；该决议见 `.codex-tasks/20260504-post-slice1-transition-review/PROGRESS.md`
- Slice 2 入口：3 个 ADR（0013 WeCom+SMS 通道 / 0014 dedup + suppression / 0015 audit scope expansion）已转 Accepted；child #1 (WeCom) `IN_PROGRESS`
- 原"Epic 14 Conditional Next"已降级为 Slice 8 之后的条件性方向
- 本轮 close-out 额外补了一份 [docs/prd-closeout.md](docs/prd-closeout.md)，用于解释：
  - 原始 `PRD.md` 的 phase-one 需求哪些已经完成
  - 哪些能力已经明显超出原始 PRD
  - 为什么后续开发已经不再是 PRD debt closeout，而是新的 roadmap extension（本次 reset 即是该 extension 的显式启动）
- Epic 11 已收口的 gap 包括：
  - overview fleet cards / charts 已可对 MySQL + Oracle 做 engine-aware 聚合
  - overview instance metrics / signal leaders 已不再依赖 MySQL-only snapshot 字段
  - full mixed-engine coverage 的 web capability boundary 已停止停留在 baseline-only 叙事
- Epic 12 已收口的 gap 包括：
  - Oracle runtime 已具备 root-level doctor/signoff 入口
  - operator 已拥有 Oracle runtime/live-gate baseline、checklists 与 rollback guidance
  - live-gate failure isolation 已具备 repo-local diagnostics surface
- Epic 13 已收口的 gap 包括：
  - `pnpm test:hardening:signoff` 已恢复为绿色，当前分支重新满足 repo-root hardening gate
  - `docs/operator-release-baseline.md` 已从最小 operator 说明升级为 internal production launch baseline，并补齐 environment / acceptance 资产
  - root-level `pnpm test:launch-readiness:signoff` 已存在并通过，能串联 hardening、Oracle runtime 与 diff hygiene
  - 当前仓库对“内部单环境可投产”的边界已收敛为 repo-local docs / scripts / tests / signoff，而不再依赖口头经验

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

## Epic 10: PRD Debt and Control-Plane Closeout

### Goal

- 把原始 `PRD.md` 仍然留在仓库里的 control-plane 欠账收口到可验证的产品面，同时不回退 01-09 已完成的多引擎、组织治理和运维闭环

### Why It Is Next

- `docs/prd-closeout.md` 已明确证明：当前主误差不是“phase-one 主链还没做出来”，而是少数 PRD 欠账仍然没有产品化收口
- 这些欠账集中在控制面与展示层，适合通过一轮有边界的 debt pass 关闭，而不需要重新发明新的产品方向
- roadmap 01-09 已全部完成，因此继续实现前必须先把 closeout gap materialize 成新的 active epic

### Activation Gates

- post-Epic-09 close-out review 已完成，并明确禁止在 roadmap 耗尽后直接进入新的实现
- `docs/prd-closeout.md` 已把 remaining gaps 收敛到实例/告警筛选、审计持久化、用户/角色管理、实例 detail semantics
- 当前仓库的多引擎与 organization baseline 已稳定，允许在不扩 scope 的前提下回补原始 PRD 欠账

### Top-Level Scope

- 为实例列表和告警列表提供显式 query contract、typed client 和 web filter surface
- 把审计日志从运行时内存钩子推进到 PostgreSQL 持久化与最小查询面
- 为用户、角色和权限补齐最小可运营的 API 与 UI
- 为实例详情补齐 TPS 以及角色/版本显式展示

### Non-Goals

- 不新增第三阶段产品方向
- 不重写现有 auth / organization / alert maturity / analytics 基线
- 不把 closeout 借机扩成分页、报表系统或复杂 IAM 平台

### Done-When

- `docs/prd-closeout.md` 里列出的 remaining gaps 都有明确代码与验证证据
- 原始 `PRD.md` 中剩余的 phase-one 控制面欠账已不再需要单独解释“为什么还没做”
- repo-root gate 能证明 closeout 没有回退现有主链

## Epic 11: Multi-Engine Fleet Metric Parity and Overview Convergence

### Goal

- 把 mixed-engine overview 从“baseline 已成立但核心 fleet metrics 仍偏 MySQL-only”推进到一个诚实、可验证的 parity baseline

### Why It Is Active Next

- `docs/prd-closeout.md` 已证明 phase-one 主线和原始控制面欠账都已收口，当前主误差不再是 PRD debt
- 当前仓库中最显式的剩余 gap 已集中在：
  - `apps/api/src/db_monitor_api/analytics/service.py` 仍把 `OVERVIEW_METRIC_ENGINES` 与 `OVERVIEW_INSTANCE_METRIC_ENGINES` 锁在 `mysql`
  - overview cards / charts 仍只聚合 MySQL throughput、threads、buffer-pool、replication 语义
  - web capability boundary 与 diagnostics 仍明确提示 mixed-engine fleet 只达到 baseline，而非 parity
- 相比之下，Oracle runtime reliability 是更偏 release / live-evidence 的 follow-up；当前更直接的产品误差仍在 fleet overview 语义层

### Activation Gates

- Epic 10 已完成，且 `docs/prd-closeout.md` 明确说明下一步应进入新的 roadmap extension
- Oracle detail analytics、engine-aware overview baseline 和 multi-engine alerting 已稳定，不再阻塞 overview parity
- 当前仓库中对 “overview parity 尚未完成” 的代码与文案 seam 已能直接定位

### Top-Level Scope

- 为 overview cards / charts 建立最小 engine-aware parity contract
- 把 overview instance metric coverage 与 signal leader semantics 从 MySQL-only 推进到 mixed-engine truth
- 收敛 web capability boundary、coverage readout、capacity insight 与 leader messaging
- 用 targeted gate 与 root signoff 证明 MySQL 主链和 Oracle detail path 未被回退

### Non-Goals

- 不追求 Oracle 全量 BI 报表或所有指标的一次性 parity
- 不重写 alerting、control-plane 或 auth / governance 主链
- 不引入第三引擎或新的报表家族

### Done-When

- mixed-engine fleet overview 的 cards / charts / signal leaders 不再显式停留在 MySQL-only 假设
- capability boundary 能诚实表达已支持的 parity 面，而不是继续把 Oracle 固定在 health-only / baseline 文案里
- MySQL overview semantics、Oracle detail semantics 与现有根级门禁不回退

## Epic 12: Oracle Runtime Reliability and Live-Gate Productionization

### Goal

- 在多引擎产品面进一步扩张之前，把 Oracle runtime 与 live-gate 证据链提升到更可持续、可重复的运维基线

### Why It Is Conditional Next

- 当前 repo 已有 Oracle live baseline，但并非每一轮后续 epic 都重跑；如果 Epic 11 收口后主误差转向“离线全绿但真实 Oracle 环境证据不够稳”，这会比继续扩产品面更优先
- 这个方向的价值取决于 Epic 11 结束后的真实证据；如果 parity 期间已经顺手把 live evidence 重新夯实，它就不必立刻激活

### Activation Gates

- Epic 11 已完成，且 mixed-engine fleet parity 不再是主要产品误差
- 离线门禁与 Oracle live gate 之间仍存在明显时滞、漂移或恢复成本
- 团队确认下一步主要风险在 runtime confidence，而不是产品 contract 缺口

### Top-Level Scope

- Oracle live-gate 的复跑策略、证据记录与失败恢复
- runtime prerequisites、operator runbook 与最小 smoke / signoff 收口
- 避免“测试全绿但真实 Oracle 依赖不可用”的假收敛

### Non-Goals

- 不扩展新的产品 surface
- 不在这一轮重写整体 release / deployment family
- 不把 runtime hardening 借机扩成新的多租户或多引擎 roadmap

### Done-When

- Oracle runtime / live-gate evidence 能稳定复用，不再依赖偶发性环境幸运
- 团队知道何时必须跑 live gate、失败时如何恢复，以及哪些离线 green 不能替代真实 gate

## Epic 13: Production Launch Readiness and Deployment Baseline

### Goal

- 把当前仓库从“产品与运行时能力基本齐备”推进到“可面向内部单环境投产的正式 launch baseline”

### Why It Is Active Next

- `docs/prd-closeout.md` 与 Epic 01-12 truth 已证明：当前主误差已经不再是产品功能缺口
- `docs/operator-release-baseline.md` 仍明确写着“最小 operator 发布基线”，并且刻意不覆盖完整 `CI/CD`
- 本轮 live evidence 表明：
  - `pnpm test:oracle-runtime:signoff` 已通过，说明 Oracle runtime 不再是最强阻塞
  - `pnpm test:hardening:signoff` 仍在 `pnpm lint` 处失败，当前分支还没达到仓库自己的 release gate
  - repo 中尚未形成一套正式的 internal production deployment baseline / env contract / launch signoff 资产
- 因此，下一轮最小而真实的价值不是继续加产品面，而是把“能不能稳妥上线”收口为可验证工程基线

### Activation Gates

- roadmap 01-12 已全部 `Done`，旧路线已经耗尽
- 用户当前目标已经从“继续扩功能”切换为“面向投产上线做决策”
- 当前 repo gap 已能明确定位到 release gate、deployment baseline、config/secrets contract 与 operator launch evidence

### Top-Level Scope

- 冻结内部单环境 production launch control contract
- 恢复 branch / root 级 release 与 hardening gates
- 交付 production deployment baseline、operator checklist、rollback/acceptance 资产
- 收敛 launch config / secrets / signoff contract，并用 root gate 验证

### Non-Goals

- 不建设完整 CI/CD 平台
- 不直接进入 Kubernetes、Terraform、多环境 promotion 或全自动发布编排
- 不把 launch epic 偷换成新的产品功能开发
- 不在没有真实上线需求的前提下提前扩成 HA/DR / 多地域课题

### Done-When

- repo-root release / hardening gates 回到可复用的绿色状态
- 内部单环境部署所需的 baseline、checklist、rollback 与 acceptance 资产齐备
- 团队知道要准备哪些环境变量、依赖、门禁和恢复动作，且这些要求已收敛到 repo-local truth source

## Epic 14: Scale, High Availability, and Disaster Recovery Hardening

### Goal

- 在单环境投产基线稳定后，把系统推进到能承载更高故障域和恢复要求的运行级别

### Why It Is Conditional Next

- 当前产品目标首先是内部单租户上线，而不是一开始就建设高可用平台
- 如果 Epic 13 完成后，真实阻塞开始集中在容量、备份恢复、故障域或节点级容错，这个方向才值得优先

### Activation Gates

- Epic 13 已完成，且 launch baseline 已被真实使用
- 团队已经有明确的恢复目标、RTO/RPO 或故障域要求，而不是纯假设性担忧
- 现有 deployment baseline 已不再是主要阻塞

### Top-Level Scope

- backup / restore / drill baseline
- 关键状态面的 failure-domain hardening
- 关键运行链路的 HA / recovery / load signoff
- 更明确的 operator escalation / incident baseline

### Non-Goals

- 不扩新的产品 surface
- 不在 launch baseline 还未稳定时直接叠加复杂架构
- 不把真实恢复演练替换成只看单次离线绿灯

### Done-When

- 团队对备份恢复、单点失效与关键负载有明确且可验证的运行基线
- 规模和故障域问题不再依赖口头经验，而有 repo-local signoff 与 operator 资产支撑

## Slice 2 — Alert Maturity & Notification Surface Expansion

### Goal

- 把告警链路从“有飞书 + SMTP 两条真实通道”推进到“双通道 + 去重抑制 + 审计写路径全覆盖”的告警成熟度基线，让 DBA 在真实值班场景里不会被噪音淹没

### Why It Is Active Next

- Slice 1（Epic 15 + Epic 16）已闭环：MySQL processlist+kill、slow query 短窗、Oracle tablespace、per-instance 阈值、Notifier 抽象 + 飞书 + SMTP 已落地，离线 gate + smoke 已通过
- Slice 1.5 已闭环：10 张 Tier 1 页 + canonical template + 暗色主题 + 中文语言包，UI 已具备承载更多通道与告警细分的视觉容量
- 当前最显式的剩余 gap 已集中在：
  - 仅有飞书 + SMTP 两条真实通道，无法覆盖企业微信生态与短信兜底场景
  - DispatchCoordinator 入口未做 (rule × instance × severity) 三元组去重，重复告警风险随规则数量线性放大
  - audit_entries 仅覆盖用户/角色 + kill，rule / instance / override / channel binding 写路径仍是黑盒

### Activation Gates

- Slice 1 与 Slice 1.5 已显式 `Done`；离线 gate 与 web smoke 不再阻塞
- 3 份 ADR（0013 WeCom + SMS / 0014 dedup + suppression / 0015 audit scope expansion）已转 `Accepted`
- 当前仓库对 Notifier 抽象、DispatchCoordinator 入口、audit_entries schema 的 seam 已可直接定位
- `.codex-tasks/20260504-slice02-alert-maturity-epic/EPIC.md` 与 `SUBTASKS.csv` 已 materialize

### Top-Level Scope

- WeCom（企业微信）作为第三条 Notifier 通道（webhook + markdown 卡片 + @user / @mobile + 失败 fallback SMTP）
- 阿里云 SMS 作为第四条 Notifier 通道（单 provider，YAGNI；1 次重试，计费谨慎；失败 fallback SMTP）
- DispatchCoordinator 入口 dedup（key = `rule_id × instance_id × severity`）+ 默认 10 分钟抑制窗口 + per-rule override（`alert_rules.suppression_window_seconds INT NULL`）
- audit_entries 写路径扩展到 rule / instance / override / channel binding 全写动作；新增 `target_type` + `diff_summary`；webhook secret / SMS access_key 走 SHA256 hash
- Slice 2 离线 signoff（lint / typecheck / ruff / mypy / pytest / 4 通道单元测试 / dedup integration / audit integration）
- schema 演进：v11 → v12（dedup + 通道 enum 扩展）→ v13（audit scope expansion）

### Non-Goals

- 不引入新的引擎（OS/SQLServer 留给 Slice 3/4）
- 不复刻飞信 / MongoDB
- 不做多 SMS provider 抽象层（YAGNI；只接阿里云）
- 不引入告警分级 / 路由 DSL；severity 仍只有 critical/warning 两级
- 不替换 audit_entries 表结构或迁移到外部审计平台
- 不在本切片内做真人值班演练（仍归客户验收前窗口）

### Done-When

- 4 条 Notifier 通道（飞书 / SMTP / 企业微信 / SMS）能在端到端测试中真到达，且失败时按 fallback 链路降级
- DispatchCoordinator 入口对重复 (rule × instance × severity) 命中能稳定抑制 10 分钟，且 per-rule override 生效
- rule / instance / override / channel binding 的写动作 100% 进入 audit_entries，敏感字段以 hash 形式落库
- Slice 2 离线 signoff（`scripts/test-slice02-signoff.ps1` + `pnpm test:slice02:signoff`）通过
- `EPIC_ROADMAP.md` Slice 2 = `Done`，`CONTEXT.md` 同步更新，Slice 3 planning materialization 触发

## Close-Out Review Template

每个 active epic 结束时，都要回答以下问题，再决定是否按默认顺序推进：

1. 当前系统最大的真实风险是在稳定性、告警质量、分析深度，还是引擎扩展？
2. 哪个问题如果不先解决，会让下一波开发明显返工？
3. 当前数据模型、API 契约和运行模型，哪些已经稳定，哪些仍在抖动？
4. 是否存在足够强的证据，支持跳过 `Default Next` 而进入某个 `Conditional Next`？

如果没有强证据，默认进入当前 roadmap 中已经冻结好的 `Default Next`；如果没有 `Default Next`，则先进入 roadmap extension。

如果当前 roadmap 已被全部关闭，则默认动作不再是“自动跳到下一个旧 epic”，而是：

1. 先写明旧 roadmap 已经耗尽
2. 再基于显式 repo gap 扩展 roadmap
3. 最后激活新的 active epic
