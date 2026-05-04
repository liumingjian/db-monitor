# Progress

## Summary

- Epic: 16 — Notifier Reality & Slice-1 Production Rehearsal
- 状态: **CLOSED (代码侧)**（child #1-#4 DONE；child #5 真人演练 2026-04-22 Boss 决议 DEFERRED）
- Slice: 1 / 8（最后一个子 epic）

## Recovery

- Epic: 16
- 进度: 4/5 DONE + 1 DEFERRED（代码侧 100% 收口）
- 当前: Epic 16 Slice 1 代码侧关闭；child #5 真人演练 Boss 决议 DEFERRED，推到客户验收前窗口
- 文件: `.codex-tasks/20260422-slice01-epic16-notifier-reality/SUBTASKS.csv`
- 下一步: 启动 Slice 1.5 UI 重做（前提 2 条已满足：Slice 1 代码侧收官 + Boss 批准）
- CSE 控制记录:
  - Phase A/B 全部一次过（零重试）
  - Phase C child #4 一次过（evaluation.py 旁路 sink 99 regressions 绿 → AlertingService/bootstrap 装配 → 背压测试 test_dispatch_backpressure 一次绿；pnpm test:notifier:signoff 全绿）
  - 累计 102 alerting 相关测试 + 72 web 测试 + mypy/ruff 28 源文件全绿；OpenAPI 0.15.0；schema v11

## Reference

- ADR-0001 lepus parity pivot
- ADR-0003 Slice 1 monitoring before notification（明确 Epic 15 → Epic 16 顺序）
- `CONTEXT.md` Slice sequence（Slice 1 的 done 判据）
- lepus-v3.8 告警模板（`lepus_alarm_mail_content` 作为字段参考，**不**抄实现）

## Notes

- Epic 16 通过后：Slice 1 = DONE；触发 Slice 2 planning materialization（OS 指标 + 多实例分组）
- WeCom / SMS / 告警抑制 / 升级链均不在本 epic；不要在演练反馈里尝试"补一下"
- 演练签字后不可回撤——这是一次性 gate
