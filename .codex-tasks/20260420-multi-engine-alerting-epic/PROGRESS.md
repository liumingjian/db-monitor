# Progress

## Summary

- Task shape: epic
- Goal: 把 multi-engine rule / alert semantics 从 MySQL-specific 推进到诚实可用的 engine-aware baseline

## Recovery

- 任务: Epic 09 已完成，multi-engine alerting baseline 已通过所有 planned signoff gates
- 形态: epic
- 进度: 6/6
- 当前: 已收口
- 文件: `.codex-tasks/20260420-multi-engine-alerting-epic/SUBTASKS.csv`
- 下一步: 回到路线图层选择下一个 epic，或先做 Epic 09 close-out review / handoff 摘要

## Control Contract

- Primary Setpoint: 让 multi-engine rule / alert semantics 成为真实产品语义，而不是继续依赖 MySQL-specific metric names 与 workflow wording
- Acceptance: 新 epic truth artifacts 完整存在；rule contract baseline child 已开始；后续 API/pipeline/web/signoff 子任务都可从磁盘恢复
- Guardrails: 不把本 epic 扩展误报成 full alert parity；不回退 Epic 08 的 overview baseline；不打坏现有 MySQL alert maturity 主链
- Sampling Plan: 先冻结 contract，再修 backend alert API、rule-engine pipeline、web rule surface、notifier workflow，最后通过 root signoff 与 Oracle live gate 收口
- Constraints: phase 2 刚完成，本 epic 当前只允许进入 `#1`，不允许跳过 contract baseline 直接改 surface

## Notes

- 这是 post-Epic-08 close-out review 后的新 active epic，而不是对旧路线图条目的重复激活
- child `#1` 已经收口了 baseline seam：规则与告警必须显式携带 `engine`，当前 catalog 仅批准 engine-scoped availability/gauge metrics，且一条规则不能跨引擎 scope
- child `#2` 已经把 boundary 落成真实 contract：alert API / typed client / OpenAPI / PostgreSQL 持久化现在都知道 `engine`，而且 rule catalog 与 cross-engine scope rejection 已有 focused coverage
- child `#3` 已经证明第二引擎 alert lifecycle 在 evaluation / pipeline / suppression / recovery 面真实成立，不再只停留在 payload 或 schema
- child `#4` 已经把 web surface 从 MySQL-first 规则页提升到了 mixed-engine baseline：现有页面家族里已经能选择 engine、看到 catalog、识别 alert engine 和更中性的 workflow 文案
- child `#5` 已收口：notification request、notified/suppressed/recovered history、delivery suppression reason 与 smoke fixtures 现在都带有明确 engine cue，Oracle-focused delivery/workflow/notifier coverage 也已补齐
- child `#6` 已完成根级 signoff：backend contract/pipeline/workflow/recovery gates、OpenAPI、web test/typecheck、smoke，以及 Oracle live gate 全部通过
- close-out review 捕获并修复了一个真实回归点：smoke 与 preview fixtures 仍引用旧的非 engine-aware notifier wording；现已与 runtime 语义对齐
