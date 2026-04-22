# Progress

## Summary

- Task shape: single-full
- Goal: rule-engine 命中 → Notifier 异步送达；timeout/失败不回压；Feishu→SMTP 降级

## Recovery

- 任务: Epic 16 child #4
- 形态: single-full
- 进度: 0/5
- 当前: PLANNED（依赖 child #2 + #3）
- 文件: `.codex-tasks/20260422-slice01-epic16-notifier-reality/tasks/20260422-04-end-to-end-integration/TODO.csv`
- 下一步: child #2/#3 DONE 后 → TODO `#1` publish RuleHitEvent

## Reference

- Epic 16 EPIC.md Scope 第 4 项 + Control Contract（rule-engine p95 硬边界）
- ADR-0003（Notifier 不得阻塞评估核心）

## Notes

- 降级只在同一事件内触发，不做跨事件状态机；跨事件的抑制 / 升级切到 Slice 3
- `pnpm test:notifier:signoff` 在本子任务落地后就具备最终验证能力
