# Progress

## Summary

- Task shape: single-full
- Goal: 冻结 fleet metric parity 的 contract baseline，避免 analytics / web 在后续 child 中各自发明不同边界

## Recovery

- 任务: child `#2` 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 已关闭；frozen contract 已被 child `#3-#5` 实际消费且未发生边界漂移
- 文件: `.codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-02-parity-contract-baseline/TODO.csv`
- 下一步: 无。进入 parent epic，由 child `#3` 及后续 child 复用该 frozen baseline

## Control Contract

- Primary Setpoint: child `#3` 开始前，团队已经明确知道这轮 parity 支持哪些 Oracle fleet metrics、哪些 leader semantics，以及哪些仍然在 parity 之外
- Acceptance: `SPEC.md` 与 `PROGRESS.md` 显式写出当前 seam、批准的 Oracle metric family、signal leaders 边界与 child `#3` 的实现入口
- Guardrails:
  - 不把 cards / charts parity 偷换成 full engine equivalence
  - 不在 signal leaders 尚未定义前就让 web 宣称 full parity
  - 不动 alerting / runtime / schema family
- Sampling Plan:
  - 先记录当前 seam，再冻结批准范围，然后把 child `#3` 的实现入口写清

## Current Seam Inventory

- analytics service:
  - `OVERVIEW_METRIC_ENGINES` 与 `OVERVIEW_INSTANCE_METRIC_ENGINES` 仍显式锁在 `mysql`
  - overview cards / charts 仍只包含 MySQL throughput、threads、buffer-pool、replication lag
- web:
  - mixed-engine overview capability boundary 仍是 `Mixed-engine baseline`
  - diagnostics 仍用 `Metrics scoped` 和 MySQL-centric leaders 解释当前范围
- tests / previews:
  - analytics contract / overview tests 仍期望 `overview_metric_engines == ["mysql"]`
  - dashboard preview 仍把 mixed-engine 场景解释为 “fleet metrics partially covered”

## Latest Evidence

- 当前 seam inventory 已完成，并有静态命令验证：
  - `rg -q 'OVERVIEW_METRIC_ENGINES' apps/api/src/db_monitor_api/analytics/service.py`
  - `rg -q 'Mixed-engine baseline' apps/web/src/monitoring-ui.ts`
  - `rg -q 'overview_metric_engines' tests/api/analytics/test_analytics_contract.py`
- frozen baseline 已被实现验证：
  - `apps/api/src/db_monitor_api/analytics/domain.py` / `router.py` 已把 overview instance snapshot 切到通用 `metrics[]`
  - `apps/api/src/db_monitor_api/analytics/service.py` 已对 MySQL + Oracle 同时开放 `OVERVIEW_METRIC_ENGINES` 与 `OVERVIEW_INSTANCE_METRIC_ENGINES`
  - `apps/web/src/monitoring-ui.ts` 已按该 contract 呈现 engine-specific leaders，而没有再发明新的跨引擎统一字段

## Approved Boundary Draft

- 本 epic 批准的 Oracle fleet metric family：
  - `oracle_sessions_total`
  - `oracle_sessions_active`
  - `oracle_session_waits`
  - `oracle_user_calls_total`
  - `oracle_physical_reads_total`
- 本 epic 批准的 overview instance contract 调整：
  - 用通用 `metrics[]` 取代当前固定的 `qps` / `threads_connected` / `threads_running` / `replication_lag_seconds`
  - 每个 instance snapshot 只暴露本引擎批准的 overview metric values，不再伪造跨引擎同名字段
- 本 epic 批准的 signal leaders 边界：
  - MySQL leaders 继续围绕 `mysql_queries_per_second`、`mysql_threads_running`、`mysql_replication_lag_seconds`
  - Oracle leaders 围绕 `oracle_user_calls_per_second`、`oracle_sessions_active`、`oracle_session_waits`
  - mixed-engine fleet 允许并列呈现 engine-specific leaders，不把不同引擎指标强行压成一个假统一单位
- 本 epic 需要收敛的用户可见面：
  - overview cards / charts
  - coverage readout
  - capability boundary
  - signal leaders
  - diagnostics / preset semantics
- 本 epic 明确保留在 parity 之外的内容：
  - Oracle full BI / deep-dive analytics
  - runtime / live-gate productionization
  - alerting / rule semantics 变化

## Handoff Gate

- child #3 的入口条件：
  - Oracle fleet metric family 已冻结
  - `overview_metric_engines` 与 `overview_instance_metric_engines` 的目标语义已写明
  - overview instance contract 已明确切换到通用 `metrics[]`
  - signal leaders 的批准边界已经明确，不再允许 API 与 web 分别猜测

## Notes

- child `#2` 的价值不是单独产出代码，而是保证后续 analytics / web parity 在同一边界上收敛
- 当前 frozen boundary 已被 child `#3-#5` 证明可实现，因此本 child 无残留 open question
