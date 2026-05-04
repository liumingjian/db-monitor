# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 冻结本 epic 中什么算作 `fleet metric parity`
- 明确当前 MySQL-only overview seams、批准的 Oracle fleet metric family，以及 signal leader 允许演进到什么边界
- 在进入 API 实现前，把 contract、guardrail 和非目标写成明确 truth

## Non-Goals

- 不在本任务中完成 analytics API 代码实现
- 不把不同引擎的指标强行定义成完全等价
- 不提前宣称 Oracle runtime reliability 已被解决

## Constraints

- 必须显式点名当前 seam：
  - `OVERVIEW_METRIC_ENGINES`
  - `OVERVIEW_INSTANCE_METRIC_ENGINES`
  - web `Mixed-engine baseline` / `Metrics scoped` 文案
- 必须冻结本 epic 批准的 Oracle fleet metric family：
  - `oracle_sessions_total`
  - `oracle_sessions_active`
  - `oracle_session_waits`
  - `oracle_user_calls_total`
  - `oracle_physical_reads_total`
- 必须写清 signal leaders 与 cards / charts 的关系，避免 child #3 和 #4 各自发明边界

## Deliverables

- 本 child 的 contract baseline
- 允许进入 child #3 的实现前置条件

## Final Validation Command

```bash
grep -q "oracle_sessions_active" .codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-02-parity-contract-baseline/SPEC.md \
  && grep -q "signal leaders" .codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-02-parity-contract-baseline/PROGRESS.md \
  && grep -q "OVERVIEW_METRIC_ENGINES" .codex-tasks/20260421-fleet-metric-parity-epic/tasks/20260421-02-parity-contract-baseline/PROGRESS.md
```
