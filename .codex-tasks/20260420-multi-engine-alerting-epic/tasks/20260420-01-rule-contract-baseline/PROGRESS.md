# Progress

## Summary

- Task shape: single-full
- Goal: 冻结 multi-engine rule contract baseline

## Recovery

- 任务: child `#1` 已完成，multi-engine rule / alert baseline 已冻结为一个最小且真实的 engine-aware contract
- 形态: single-full
- 进度: 3/3
- 当前: 所有步骤已完成，等待 child `#2` 接手 rule catalog / API contract 实现
- 文件: `.codex-tasks/20260420-multi-engine-alerting-epic/tasks/20260420-01-rule-contract-baseline/TODO.csv`
- 下一步: 进入 child `#2 Implement engine-aware rule catalog and alert API contract`，把已冻结的 `engine`、catalog validation 与 schema/backfill boundary 落到 domain / router / client / OpenAPI

## Control Contract

- Primary Setpoint: 把 rule / alert baseline 冻结成一个显式可实现的 engine-aware contract，让后续 child 不再依赖 “metric_name 看起来像 mysql_* 就默认是 MySQL 规则” 这种隐式约定
- Acceptance: MySQL-specific seam 已明确记录；允许推进的 engine-aware fields、metric catalog boundary、instance-scope boundary 与 explicit non-goals 都已写入 truth artifact；focused validation 通过
- Guardrails: 不把本 child 扩成完整 alert DSL；不假装 Oracle 与 MySQL 告警语义已经 parity；不提前修改 web 规则页成新的 per-engine workflow family
- Sampling Plan: 先审计 `packages/ui/src/index.ts`、alerting domain/router/service/evaluation、focused API/rule-engine tests；再冻结 boundary；最后用 focused pytest + `pnpm openapi:check` 证明当前 contract baseline 没有被误写
- Constraints: 本 child 只冻结 boundary，不在这里完成 alert API / schema / client contract 全量实现；这些变更属于 child `#2`

## Observed Seams

- UI seam 仍很直白：`packages/ui/src/index.ts` 的 `RULE_FORM_FIELDS` placeholder 还是 `mysql_replication_lag_seconds`，当前 form 没有 `engine` 维度
- API seam 仍是隐式引擎推断：`CreateRuleRequest` / `AlertRuleResponse` / `AlertRecordResponse` 只有 `metric_name`，没有 `engine`
- Domain seam 仍只靠 metric 字符串驱动：`AlertRule` / `AlertRecord` 不携带 `engine`，评估路径 `_matching_samples()` 仅比较 `metric_name` 与 `instance_ids`
- Workflow seam 仍把“可告警语义”与 MySQL 默认样例绑在一起：focused API、rule-engine、pipeline、delivery、workflow tests 主要围绕 `mysql_replication_lag_seconds` 与 `mysql_threads_running`
- State seam 仍未显式分引擎：Postgres `alert_rules` / `alert_records` 当前 schema 只保存 `metric_name`，没有 `engine` 列，因此任何 multi-engine 扩展都还不能靠持久化契约自证

## Contract Freeze

- engine-aware baseline 的共享 rule identity 固定为：
  - `engine`
  - `metric_name`
  - `operator`
  - `threshold`
  - `severity`
  - `instance_ids`
- `engine` 是 rule / alert contract 的显式一等字段，不再允许依赖 `metric_name` 前缀去“猜测”引擎语义
- metric selection 采用 engine-scoped catalog，而不是 engine-neutral DSL：
  - 当前 baseline 只允许使用已进入 telemetry state-plane 的 availability 或 gauge 类指标
  - 不允许把 counter/raw total 直接当作共享 alert baseline，因为当前规则语义只有阈值比较，没有 rate/derivative 语义
- 当前批准的 catalog boundary：
  - MySQL: `mysql_server_available`, `mysql_threads_connected`, `mysql_threads_running`, `mysql_uptime_seconds`, `mysql_replication_lag_seconds`
  - Oracle: `oracle_server_available`, `oracle_sessions_total`, `oracle_sessions_active`, `oracle_session_waits`, `oracle_uptime_seconds`
- instance scope 继续允许空 `instance_ids` 代表“当前组织下该 engine catalog 的全部实例”，但一条规则只能属于一个 engine；显式 scope 的实例也必须全部与 rule.engine 一致
- alert record 必须继承 rule.engine，并把它贯通到 API payload、持久化状态与 workflow/notifier message 语义中；这会由 child `#2` / `#3` 具体实现

## Explicit Non-Goals

- 不引入 `replication_lag_seconds` / `sessions_active` 这类 engine-neutral metric alias；本 epic 先保留 engine-scoped metric names
- 不支持一条规则跨 MySQL 与 Oracle 混合实例 scope
- 不把 raw counter metrics 直接提升为当前 alert baseline；`mysql_queries_total`、`oracle_user_calls_total` 等仍不是本 epic 当前批准的规则 catalog
- 不在本轮把 notifier / on-call copy 扩展成分引擎独立 workflow 家族
- 不宣称 Oracle 已经拥有与 MySQL 完全对齐的 alert parity；当前只冻结“可运营且诚实”的最小第二引擎 baseline

## Next-Child Direction

- child `#2` 必须先落三件事：
  - 在 rule / alert domain、router、typed client、OpenAPI 中显式增加 `engine`
  - 增加 engine-scoped rule catalog validation，并拒绝跨引擎 instance scope
  - 为现有持久化规则/告警补上 `engine` schema/backfill 路径，默认把历史数据收敛为当前已知的 MySQL baseline
- child `#3` 再继续：
  - 让 evaluation / alert pipeline / recovery/noise control 使用新的 engine-aware contract
  - 用 Oracle-focused sample fixtures 证明第二引擎 baseline 真能打开/保持/恢复告警，而不是只停留在 payload 层

## Evidence

- 审计证据：
  - `packages/ui/src/index.ts` 仍以 `mysql_replication_lag_seconds` 作为规则表单默认提示
  - `apps/api/src/db_monitor_api/alerting/domain.py`、`router.py`、`evaluation.py` 目前没有显式 `engine` 字段
  - `tests/api/alerting/test_alerting_contract.py`、`tests/rule_engine/test_rule_engine_contract.py`、`tests/rule_engine/test_rule_engine_evaluate.py` 与 `tests/integration/alert_pipeline/test_alert_pipeline.py` 仍主要围绕 MySQL 指标名组织
- 设计锚点：
  - telemetry 层已经有 `DatabaseEngine` 与 `MetricSample.engine`
  - `apps/api/src/db_monitor_pipeline/normalization.py` 已明确区分 availability 与 gauge/counter metrics，因此 alert baseline 可以直接建立在现有 engine-aware telemetry catalog 之上，而不需要发明新 DSL

## Validation

- `bash -lc "rg -q 'mysql_replication_lag_seconds' packages/ui/src/index.ts && rg -q 'mysql_replication_lag_seconds' tests/api/alerting/test_alerting_contract.py"`
- `bash -lc "grep -q 'engine-aware' .codex-tasks/20260420-multi-engine-alerting-epic/tasks/20260420-01-rule-contract-baseline/PROGRESS.md"`
- `uv run pytest tests/api/alerting/test_alerting_contract.py tests/rule_engine/test_rule_engine_contract.py`
- `pnpm openapi:check`
