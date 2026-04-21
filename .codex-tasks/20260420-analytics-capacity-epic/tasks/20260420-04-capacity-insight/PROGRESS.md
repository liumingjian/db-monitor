# Progress

## Summary

- Task shape: single-full
- Goal: 提供容量风险语义而不是只堆更多图表

## Recovery

- 任务: capacity insight summaries and ranking views 已完成
- 形态: single-full
- 进度: 2/2
- 当前: 已完成，等待后续 preset 子任务复用
- 文件: `.codex-tasks/20260420-analytics-capacity-epic/tasks/20260420-04-capacity-insight/TODO.csv`
- 下一步: 子任务 `#5` 在当前稳定的 window + capacity semantics 之上沉淀可重开的 preset baseline

## Notes

- 子任务 `#2` 已解锁 URL-backed time window contract
- 子任务 `#3` 已补出 `outbound throughput` 与 `buffer pool reads`，因此当前不需要先扩 collector 就能定义一版 capacity semantics
- 当前实现没有引入黑箱容量分数，而是显式暴露：
  - overview `Capacity outlook`
  - overview `Signal leaders`
  - instance detail `Capacity readout`
- 本轮验证已通过：
  - `uv run pytest tests/api/analytics tests/integration/analytics_queries`
  - `pnpm --filter web test`
  - `pnpm --filter web build`
