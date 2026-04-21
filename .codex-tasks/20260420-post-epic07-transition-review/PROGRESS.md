# Progress

## Summary

- Task shape: single-full
- Goal: 完成 Epic 07 之后的正式 close-out review，并把下一阶段重新冻结到 roadmap extension

## Recovery

- 任务: 关闭 Epic 07 之后，确认当前 roadmap 是否还存在可直接激活的既有 epic；如果没有，则先停在 close-out review，不提前进入 phase 2
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260420-post-epic07-transition-review/TODO.csv`
- 下一步: 如需继续推进，下一轮必须先进入 roadmap extension，再执行 `next epic planning materialization`

## Control Contract

- Primary Setpoint: 在不伪造“默认 next epic”的前提下，为 Epic 07 之后的继续开发提供一个严格符合 `AGENT.md` 的 phase-1 结论
- Acceptance: 本任务 `PROGRESS.md` 明确写出 Epic 07 close-out review、现有 roadmap 是否已耗尽、为什么当前下一步必须是 roadmap extension，以及哪些显式 repo gap 值得进入 phase 2 讨论
- Guardrails: 不把已完成的旧 epic 重新激活；不把 roadmap extension 偷换成产品代码实现；不把 Oracle 最小闭环说成“已经达到全引擎 parity”
- Sampling Plan: 先读 Epic 07 的 parent truth artifacts 与路线图状态，再对照 `PRD.md` / `RESEARCH.md` 与当前 repo 中仍显式保留的 MySQL-first / MySQL-specific 边界，最后冻结 transition gate
- Constraints: 当前 `EPIC_ROADMAP.md` 01-07 已全部 `Done`；在扩展 roadmap 之前，不存在可直接激活的既有 active/default epic

## Close-Out Review

- Epic 07 证明了什么：
  - Oracle 不再停留在 validation-only，而是获得了最小真实 `collector -> schema -> analytics -> web detail -> signoff` 闭环
  - `MetricSample` / ClickHouse schema / analytics route / typed client / web detail flow 都已具备真实 `engine-aware` 维度
  - 当前 macOS + Docker 环境仍可通过 `pnpm test:control-plane:oracle` 执行 Oracle live gate
  - 同一轮根级 signoff 证明 MySQL 主路径、组织治理语义与 Oracle 第二引擎最小闭环可以同时成立
- Epic 07 没证明什么：
  - Oracle fleet overview semantics 和更深 engine-specific diagnostics 仍未做到 full parity
  - 规则/告警语义是否已经从 MySQL 指标名扩展到真正的多引擎可运营状态
  - roadmap 在 Epic 07 之后是否还保留一个可直接激活的既有 future epic
- 当前 roadmap 状态：
  - `EPIC_ROADMAP.md` 当前快照中 01-07 已全部标记为 `Done`
  - 因此当前阶段不存在一个可以按旧路线图直接激活的既有 epic
  - 下一步不是激活新的既有 epic，而是先做 roadmap extension，再进入 `next epic planning materialization`
- 为什么当前不能伪造默认 next：
  - `AGENT.md` 明确规定：当 roadmap 中所有 epic 都已 `Done` 时，必须先基于显式 repo gap 扩展 roadmap，再激活新的 epic
  - `PRD.md` 与 `RESEARCH.md` 仍把产品主边界定义为 `MySQL-first`、内部单租户、phase-one 起点，因此后续方向必须来自当前仓库已显式暴露的真实误差，而不是抽象“想做更多”
- 当前仓库里仍显式保留、值得进入 roadmap extension 讨论的 gap：
  - Oracle 详情页虽已可见最小趋势，但 `apps/web/src/monitoring-ui.ts` 与 `apps/web/app/instances/page.tsx` 仍显式写明 overview semantics 和更深 engine diagnostics remain `MySQL-first`
  - 规则与告警链路当前仍明显以 MySQL 指标名为主，例如 `packages/ui/src/index.ts` 中的 rule form placeholder 仍是 `mysql_replication_lag_seconds`，`tests/api/alerting/test_alerting_contract.py` 与 `tests/integration/alert_pipeline/test_alert_pipeline.py` 也仍围绕 MySQL replication-lag 语义组织
  - 这些都是真实 repo gap，但它们现在只是 phase-2 的候选输入，不是 phase-1 可以直接激活的新 epic
- 什么证据会决定 phase 2 应该优先扩展哪类方向：
  - 如果产品压力来自多引擎 fleet overview / deeper diagnostics 不一致，应优先考虑 engine-aware insights / overview 方向
  - 如果真实运维压力来自 Oracle 缺少告警与规则承载，应优先考虑 multi-engine alerting / rule semantics 方向
  - 在没有进一步权重判断前，phase 1 只负责把这些候选 gap 写清，不负责替用户提前选择和物化

## Decision Gate

- 当前结论：
  - Epic 07 已正式关闭
  - 当前 roadmap 01-07 已全部完成，不存在可直接继续激活的既有 epic
  - phase 2 必须先做 roadmap extension，之后才能进入新的 epic planning materialization
- 当前结果：
  - 本轮只交付 post-Epic-07 close-out review truth source
  - 当前没有新建任何后续 active epic skeleton，保持与 `AGENT.md` 的 phase separation 一致

## Validation

- `bash -lc "grep -q 'Close-Out Review' .codex-tasks/20260420-post-epic07-transition-review/PROGRESS.md && grep -q 'roadmap 01-07 已全部完成' .codex-tasks/20260420-post-epic07-transition-review/PROGRESS.md && grep -q 'phase 2' .codex-tasks/20260420-post-epic07-transition-review/PROGRESS.md && grep -q '下一步不是激活新的既有 epic' .codex-tasks/20260420-post-epic07-transition-review/PROGRESS.md && ! rg -n '\\| .* \\| Active \\|' EPIC_ROADMAP.md"`
