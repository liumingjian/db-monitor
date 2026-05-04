# Progress

## Summary

- Task shape: single-full
- Goal: 在 post-Slice-1 close-out review 之后，把 Slice 2（告警成熟度 + 通知面扩展）正式 materialize 为 active epic，并保持 Slice 1 演练在 deferred 注脚

## Recovery

- 任务: 在 Slice 1 close-out 之后，把 Slice 2 完整物化到 roadmap + skeleton
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260504-post-slice1-planning-materialization/PROGRESS.md`
- 下一步: 待 kickoff PR 合并 + Boss 把 ADR-0013 转 Accepted 后，再把 `#1 WeCom 通道 + ChannelRegistry 扩展` 切到 IN_PROGRESS 并启动实现

## Control Contract

- Primary Setpoint: 在不越界进入 Slice 2 实现细节的前提下，把"告警成熟度 + 通知面扩展"落成正式 active epic
- Acceptance: `EPIC_ROADMAP.md` 出现 Slice 2 = Active；新 epic parent/child skeleton 完整存在；所有 child 处于 `PLANNED`（kickoff PR 合并 + ADR 锁定后再切 IN_PROGRESS）；3 份 ADR 草稿已就位
- Guardrails:
  - 不把 Epic 15 / Epic 16 重新激活；演练 deferred 是已签的一次性决议
  - 不把 Slice 2 偷换为新引擎扩展（OS / SQLServer 推到 Slice 3+）
  - 不在没有 ADR 锁定前进入实现
  - 不把告警去重 / 抑制做成完整 DSL（保持最小可验证语义）
- Sampling Plan: 先冻结 close-out decision → 写 3 份 ADR 草稿 → 一次性创建 Slice 2 epic parent/child skeleton → 更新 roadmap → 静态 completeness 校验
- Constraints: 本任务只负责 roadmap extension、activation 和 skeleton materialization，不开始 child `#2-#5` 的实现

## Decision Notes

- 选择 `Slice 2 — Alert Maturity & Notification Surface Expansion` 作为 active epic 的依据：
  - `CONTEXT.md` Slice sequence 已锁定 Slice 2 为 Slice 1 的默认下一个，主题为"企业微信 / 短信 / 告警去重抑制深化（对标 lepus `alarm_temp`）/ 审计范围扩展"
  - Slice 1 演练 DEFERRED 不再阻塞代码侧推进（Boss 2026-04-22 决议）
  - Epic 16 已经把 ChannelRegistry / DispatchCoordinator / fallback 抽象为 pluggable factory，扩 WeCom / SMS 是"在已成立抽象上的最小新通道"，没有架构返工
  - 告警去重 / 抑制（lepus `alarm_temp` 对标）是当前 Notifier 之上明显的下一层语义：飞书 + SMTP 已能投递，但相同事件在评估周期内可能反复投，运维侧已经反映"告警太吵"
  - 审计范围扩展是把 Epic 16 已建立的 `notify_history` 模式扩散到 rule/instance/session 改动审计
- roadmap extension 的结果：
  - Slice 2 状态从 `Planned` 改为 `Active`
  - 新增 Slice 2 完整 epic 段（参考 Epic 12-13 格式）
  - Epic 15 / Epic 16 状态从 `Active` / `Planned` 改为 `Done`，并补一行 Slice 1.5 UI Redesign = Done
- Slice 2 active epic 的当前 child 规划（全部 PLANNED；待 kickoff PR 合并）：
  - `#1` WeCom（企业微信）通道 + ChannelRegistry 扩展
  - `#2` SMS 通道（阿里云单 provider，YAGNI）
  - `#3` 告警去重 + 抑制窗口（rule × instance × severity 维度的最小状态机）
  - `#4` 审计范围扩展（rule / instance / override / channel binding 改动）+ 查询 surface
  - `#5` Slice 2 离线 signoff + 新能力 smoke

## ADR Drafts

- `docs/adr/0013-wecom-and-sms-channel-expansion.md` — Draft；锁定 WeCom webhook 卡片格式 + SMS 服务商边界（不引入 lepus 飞信）
- `docs/adr/0014-alarm-dedup-and-suppression.md` — Draft；锁定去重 key（rule_id × instance_id × severity）+ 抑制窗口默认 10 分钟可 per-rule override + 状态机
- `docs/adr/0015-audit-scope-expansion.md` — Draft；锁定新增审计动作类型（rule.create/update/delete、instance.config.change、channel_binding.\*）

## Validation

- `bash -lc '
set -e
test -f .codex-tasks/20260504-slice02-alert-maturity-epic/EPIC.md
test -f .codex-tasks/20260504-slice02-alert-maturity-epic/SUBTASKS.csv
test -f .codex-tasks/20260504-slice02-alert-maturity-epic/PROGRESS.md
test -f docs/adr/0013-wecom-and-sms-channel-expansion.md
test -f docs/adr/0014-alarm-dedup-and-suppression.md
test -f docs/adr/0015-audit-scope-expansion.md
grep -q "Slice 2 — Alert Maturity & Notification Surface Expansion | Active" EPIC_ROADMAP.md
grep -q "Slice 1 / Epic 15 — Monitoring Depth & Rule Granularity | Done" EPIC_ROADMAP.md
grep -q "Slice 1 / Epic 16 — Notification Reality" EPIC_ROADMAP.md
[ "$(grep -c ",PLANNED," .codex-tasks/20260504-slice02-alert-maturity-epic/SUBTASKS.csv)" = "5" ]
'`
