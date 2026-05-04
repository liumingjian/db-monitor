# Progress

## Summary

- Epic: Slice 2 — Alert Maturity & Notification Surface Expansion
- 状态: **Active**
- Slice: 2 / 8
- 启动日: 2026-05-04（post-Slice-1 planning materialization 触发）

## Recovery

- Epic: Slice 2
- 形态: epic
- 进度: 0/5（child #1 PLANNED；等 kickoff PR 合并 + ADR-0013/0014/0015 转 Accepted）
- 当前: kickoff 分支 `codex/slice2-alert-maturity-kickoff` 待 commit + push + open PR；Boss review 后 child #1 unblocked
- 文件: `.codex-tasks/20260504-slice02-alert-maturity-epic/SUBTASKS.csv`
- 下一步:
  1. Boss review 并锁定 ADR-0013/0014/0015
  2. 启动 child #1：`tasks/20260504-01-wecom-channel/SPEC.md` 撰写 + WeCom webhook 测试 fixture 准备
  3. child #1 DONE 后启动 child #2（SMS 通道）

## 启动前提（entry gate）

1. Slice 1 Epic 15 + Epic 16 代码侧 DONE ✅
2. Slice 1.5 UI 重做 11/11 DONE ✅
3. PR #1 已合并到 main（merge `15a0fee`） ✅
4. Boss 批准启动 Slice 2 ✅
5. ADR-0013/0014/0015 草稿已就位 ✅（待 Boss 决议转 Accepted）

## 决策来源

- `CONTEXT.md` Slice sequence（2026-04-22 locked）：Slice 2 主题"告警成熟度 + 通知面扩展"
- ADR-0013 WeCom + SMS 通道
- ADR-0014 告警去重 + 抑制窗口
- ADR-0015 审计范围扩展
- Epic 16 HANDOFF.md（ChannelRegistry / DispatchCoordinator 抽象边界继承点）

## Validation

- 待 child #5 实施时跑 `pnpm test:slice02:signoff`
- 当前阶段（planning materialization 收尾）只做静态 completeness 检查，见 `post-slice1-planning-materialization/PROGRESS.md` Validation 段

## Tier 3 占位（Slice 3+ 回填清单）

- 告警升级链 / on-call 轮询 → Slice 3
- 告警自动恢复后通知 → Slice 3
- PostgresBindingRepository（binding 持久化跨重启） → Slice 3
- 跨 rule 去重 / 内容相似度去重 → Slice 3+
- SMS 多 provider 抽象 / 国际短信 → Slice 3+（条件性）
- 审计 TTL / 归档策略 → Slice 3+

## Notes

- 不重新激活 Epic 16 child #5 真人演练（DEFERRED 决议不可回撤）
- WeCom + SMS 凭据投产时由 env 注入（与 SMTP 同模式），bootstrap 不读 env binding（仍 in-memory）
- 客户验收时序约束：Slice 2 关闭 → 客户演练 → Lighthouse prod 重跑 → 真投产
