# Progress

## Summary

- Task shape: epic
- Goal: 把 mixed-engine fleet overview 与更深 diagnostics 从 `MySQL-first` 推进到诚实可用的 engine-aware baseline

## Recovery

- 任务: Epic 08 已完成，所有 child tasks 与根级 signoff gate 已关闭
- 形态: epic
- 进度: 6/6
- 当前: 无 active child；当前 epic 已完成，等待 protocol-required 的 post-Epic-08 close-out review
- 文件: `.codex-tasks/20260420-engine-aware-overview-epic/SUBTASKS.csv`
- 下一步: 执行 post-Epic-08 close-out review，并基于 roadmap 判断是否进入 Epic 09 planning materialization

## Control Contract

- Primary Setpoint: 让 mixed-engine fleet overview 成为真实产品语义，而不是继续依赖 detail-only Oracle support 与 MySQL-first copy
- Acceptance: 新 epic truth artifacts 完整存在；overview contract baseline child 已开始；后续 analytics/web/signoff 子任务都可从磁盘恢复
- Guardrails: 不把 overview 扩展误报成 multi-engine alert parity；不回退 Epic 07 的 Oracle data-plane；不打坏现有 MySQL detail 与 governance 主链
- Sampling Plan: 先冻结 contract，再修 backend aggregation、web overview、diagnostics presets，最后通过 root signoff 与 Oracle live gate 收口
- Constraints: phase 2 刚完成，本 epic 当前只允许进入 `#2`，不允许跳过 contract baseline 直接改 surface

## Latest Evidence

- child `#2` 已把 `OverviewInstanceResponse` 冻结为 mixed-engine aware instance contract，并同步了 OpenAPI snapshot
- child `#3` 已把 overview API 扩展为 engine-aware summary + coverage contract，同时保留当前 MySQL cards/charts 兼容面
- child `#4` 已把 web overview surface 与 instances copy 收敛到新的 coverage boundary 上
- child `#5` 已把 presets 与剩余 overview guidance copy 收敛到 coverage-aware baseline 上
- child `#6` 已通过 root signoff：OpenAPI、analytics/integration、web、smoke、Oracle live gate 全部成立
- focused verification passed:
  - `uv run pytest tests/integration/analytics_queries/test_analytics_queries.py`
  - `uv run pytest tests/api/analytics tests/integration/analytics_queries`
  - `uv run pytest tests/api/analytics tests/integration/analytics_queries tests/integration/metrics_pipeline tests/integration/control_plane`
  - `pnpm --filter web typecheck`
  - `pnpm --filter web test`
  - `pnpm --filter web build`
  - `pnpm openapi:check`
  - `pnpm smoke`
  - `pnpm test:control-plane:oracle`

## Notes

- 这是 post-Epic-07 roadmap extension 后的新 active epic，而不是对旧路线图条目的重复激活
- child `#2` 已经证明：mixed-engine fleet overview 至少可以先从 instance metadata contract 诚实落地，而无需一次性宣称 full metrics parity
- child `#3` 已经证明：API 可以先显式表达 engine coverage 边界，而不是继续把 MySQL-only semantics 隐含在 payload 之外
- child `#4` 已经证明：页面已经可以消费 engine-aware contract，而不需要拆出新的 Oracle overview 页面家族
- child `#5` 已经证明：preset semantics 与剩余 diagnostics wording 可以在不扩 scope 的前提下回到诚实的 mixed-engine baseline
- Epic 08 已证明：mixed-engine fleet overview 可以在不伪装 alert parity 的前提下形成诚实可用的 baseline，并与既有 MySQL 主链和 Oracle live gate 同时成立
- `Epic 09: Multi-Engine Alerting and Rule Semantics` 已进入 roadmap，但仍是 `Conditional Next`，不能在没有 close-out review 与 planning materialization 的前提下直接开始实现
