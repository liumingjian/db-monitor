# Epic Specification

## Goal

- 把当前仍围绕 MySQL 指标名与 MySQL 运维语义组织的 rule / alert contract，推进到真正可承载多引擎运营的语义基线，同时不回退 Epic 08 刚收口的 mixed-engine overview baseline

## Why This Epic Is Next

- Epic 08 已证明 mixed-engine fleet overview 与 diagnostics baseline 可以诚实成立，因此当前主误差不再是 overview 语义，而是 alert / rule contract 仍明显绑定 MySQL metric names
- 当前仓库 truth 仍显式保留以下 gap：
  - `packages/ui/src/index.ts` 的 `RULE_FORM_FIELDS` placeholder 仍是 `mysql_replication_lag_seconds`
  - `tests/api/alerting/test_alerting_contract.py`、`tests/integration/alert_pipeline/test_alert_pipeline.py`、`tests/rule_engine/test_rule_engine_contract.py`、`tests/rule_engine/test_rule_engine_evaluate.py` 仍主要围绕 MySQL metric names 和 MySQL 运维语义组织
  - notifier / noise-control / on-call workflow 仍没有一个明确的 engine-aware alert baseline
- 相比之下，overview baseline 已经完成 root signoff，因此继续停留在 overview 层只会重复已闭环的工作

## Scope

- 冻结 multi-engine rule / alert contract baseline，包括最小 engine-aware metric selection、rule semantics 与 explicit non-goals
- 在 alerting service / API contract / rule-engine evaluation 中实现第二引擎最小可运营语义
- 让 web rule / alert surface、workflow messaging 与 notifier / noise-control 语义停止依赖隐式 MySQL-only 假设
- 为本 epic 形成 root signoff 与 Oracle live coverage 证据链

## Non-Goals

- 不追求所有引擎、所有指标的一次性 parity
- 不重写整个 alert maturity stack
- 不在没有清晰运营语义前引入复杂 DSL
- 不回退 Epic 08 已关闭的 overview baseline 与 Epic 07 已关闭的 Oracle data-plane

## Done-When

- 团队可以用统一但诚实的方式为多引擎配置最小规则与告警语义
- MySQL 现有 alert maturity 主链未被回退
- Oracle 或第二引擎最小 alerting baseline 能通过 root signoff 与 live gate 收口

## Close-Out Review

- Epic 08 证明了什么：
  - overview payload、web surface、coverage boundary 与 presets 已经形成 mixed-engine baseline
  - OpenAPI、analytics/integration、web、smoke 与 Oracle live gate 可以在同一轮 signoff 中同时成立
  - 当前真正剩余的引擎扩展主误差已经从 “看不见 fleet baseline” 转移到 “无法用统一告警语义运营多引擎”
- Epic 08 没证明什么：
  - rule contract 是否已能表达第二引擎指标
  - alert pipeline / notifier / noise-control / on-call semantics 是否已准备好承载第二引擎
  - web 规则表单和 alerts surface 是否已具备 engine-aware 的选择与解释能力
- 默认下一个 epic：
  - `Epic 09: Multi-Engine Alerting and Rule Semantics`
- 为什么是它：
  - 当前仓库最显式的剩余共享契约主误差正是 alert / rule semantics 仍然 MySQL-specific
  - 这比再继续扩 overview 更接近当前真实阻塞，也更适合做最小连续扩展
- 什么证据才会支持不直接走它：
  - 如果新的 root signoff 或真实运行证据表明 runtime / release / governance 出现更重回退，则应先回到对应层级处理
  - 如果新的产品证据表明真实阻塞仍然不在 alert/rule semantics，而是在 overview baseline 或 data-plane 稳定性，则应重新排序 roadmap

## Child Deliverables

- 冻结 multi-engine rule / alert contract baseline
- 实现 engine-aware rule catalog 与 alert API contract
- 扩展 rule engine evaluation 与 alert pipeline 的第二引擎基线
- 实现 engine-aware web rule / alert surface 与 workflow messaging
- 收敛 notifier、noise-control 与 on-call semantics
- 运行 multi-engine alerting root signoff 与 Oracle live coverage

## Dependency Notes

- 子任务 `#1` 是后续 alerting / web / signoff 的 contract baseline
- 子任务 `#2` 依赖 `#1`
- 子任务 `#3` 依赖 `#1;#2`
- 子任务 `#4` 依赖 `#1;#2`
- 子任务 `#5` 依赖 `#3;#4`
- 子任务 `#6` 依赖 `#2;#3;#4;#5`

## Child Task Types

- `single-full`
