# Progress

## Summary

- Task shape: single-full
- Goal: 完成 Epic 08 之后的正式 close-out review，并把下一阶段重新冻结到 Epic 09 planning materialization

## Recovery

- 任务: 关闭 Epic 08 之后，确认当前 roadmap 是否已经收敛到一个明确的默认下一步；如果是，则先停在 close-out review，不提前进入 Epic 09 实现
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260420-post-epic08-transition-review/TODO.csv`
- 下一步: 如需继续推进，下一轮必须先进入 Epic 09 的 planning materialization，再允许开始实现

## Control Contract

- Primary Setpoint: 在不跳过 phase separation 的前提下，为 Epic 08 之后的继续开发提供一个严格符合 `AGENT.md` 的 phase-1 结论
- Acceptance: 本任务 `PROGRESS.md` 明确写出 Epic 08 close-out review、为什么 Epic 09 现在成为默认下一步、什么证据会阻止直接激活，以及为什么当前下一步仍只是 planning materialization
- Guardrails: 不把 overview baseline 说成 alert parity；不把 close-out review 偷换成 Epic 09 代码实现；不在没有证据时发明新的 roadmap 方向
- Sampling Plan: 先读 Epic 08 truth artifacts 与 roadmap 当前状态，再对照当前仓库中仍显式保留的 MySQL-specific alert/rule seams，最后冻结 transition gate
- Constraints: 当前 `EPIC_ROADMAP.md` 中 08 已 `Done`，09 是唯一未完成的 roadmap epic；但在 phase 2 物化之前，09 仍不能直接开始实现

## Close-Out Review

- Epic 08 证明了什么：
  - `OverviewResponse` 已经具备 mixed-engine overview instance metadata、engine-aware summary 与 coverage boundary，不再把 Oracle 支持面限制在 detail-only 路径
  - web overview surface 已经能够显式渲染 capability boundary、coverage readout、engine summaries，以及 scope-aware 的 leaders / insight / presets 语义
  - 根级 signoff 已证明 mixed-engine overview baseline 与既有 MySQL 主链、web smoke、Oracle live gate 可以同时成立
  - 当前 macOS + Docker 环境下，`pnpm smoke` 与 `pnpm test:control-plane:oracle` 都仍然可作为真实 gate 使用
- Epic 08 没证明什么：
  - alert rule contract 是否已经从 MySQL 指标名提升为真正的多引擎可运营语义
  - notifier、noise controls、alert pipeline、on-call workflow 是否已经能承载 Oracle 或更广义的 multi-engine metric families
  - 规则创建、规则评估和告警契约是否已经具备 engine-aware metric selection / validation / preview / delivery semantics
- 当前 roadmap 状态：
  - `EPIC_ROADMAP.md` 当前快照中 01-08 已全部标记为 `Done`
  - 09 `Multi-Engine Alerting and Rule Semantics` 是唯一剩余、且与当前显式 repo 主误差直接对齐的 future epic
  - 因此 Epic 09 现在不再只是抽象候选，而是基于现有证据收敛出的默认下一步
- 为什么 Epic 09 现在是 default next：
  - 当前仓库中大量 alert/rule 契约与测试仍直接绑定 MySQL metric names，例如：
    - `tests/api/alerting/test_alerting_contract.py`
    - `tests/integration/alert_pipeline/test_alert_pipeline.py`
    - `tests/alerting_contract/test_alert_workflow_contract.py`
    - `tests/rule_engine/test_rule_engine_contract.py`
    - `tests/rule_engine/test_rule_engine_evaluate.py`
  - 这些测试与行为仍围绕 `mysql_replication_lag_seconds`、`mysql_threads_running`、`mysql_threads_connected` 等指标名组织
  - 当前的主误差已经不再是 “overview 仍是 MySQL-first”，而是 “alert/rule semantics 仍明显是 MySQL-specific”
- 什么证据会阻止直接进入 Epic 09：
  - 如果 root signoff 之后出现新的 runtime / release / governance 回退，且严重程度高于 alert/rule semantics gap，应先回到对应层级处理
  - 如果新的真实运行证据表明当前产品阻塞重新落回 overview baseline 或 Oracle data-plane 稳定性，而不是 alert/rule 契约，则需要重新排序 roadmap
  - 在没有这些新证据前，当前最诚实的下一步就是 Epic 09

## Decision Gate

- 当前结论：
  - Epic 08 已正式关闭
  - Epic 09 现在成为默认下一步，因为它是 roadmap 中唯一剩余、且与当前仓库显式主误差直接对齐的 future epic
  - 下一步是 Epic 09 planning materialization，不直接开始实现
- 当前结果：
  - 本轮只交付 post-Epic-08 close-out review truth source
  - 当前还没有创建 Epic 09 skeleton；phase 2 仍需单独执行，保持与 `AGENT.md` 的 phase separation 一致

## Validation

- `bash -lc "grep -q 'Close-Out Review' .codex-tasks/20260420-post-epic08-transition-review/PROGRESS.md && grep -q 'Epic 09' .codex-tasks/20260420-post-epic08-transition-review/PROGRESS.md && grep -q 'planning materialization' .codex-tasks/20260420-post-epic08-transition-review/PROGRESS.md && grep -q 'mysql_' .codex-tasks/20260420-post-epic08-transition-review/PROGRESS.md"`
