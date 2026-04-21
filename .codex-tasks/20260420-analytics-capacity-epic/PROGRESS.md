# Progress

## Summary

- Task shape: epic
- Goal: 把现有 analytics 从基础趋势浏览推进到可切窗口、可看更深指标、可判断容量风险的下一阶段

## Recovery

- 任务: 激活 `Analytics and Capacity Insight Expansion` 并推进第一个真实实现子任务
- 形态: epic
- 进度: 6/6
- 当前: Epic 04 已完成
- 文件: `.codex-tasks/20260420-analytics-capacity-epic/SUBTASKS.csv`
- 下一步: 当前 epic 边界已关闭；如果继续推进 roadmap，下一轮需先执行新的 epic close-out review 和 planning materialization

## Notes

- Epic 03 的 close-out review 已显式写入本 epic `EPIC.md`
- Alert maturity 与 macOS 环境基线都已通过根级 signoff，因此当前主误差转到 analytics 深度和容量洞察
- 子任务 `#3` 已完成：analytics 已从 `threads / QPS / inbound / lag / uptime` 扩到 `outbound throughput` 与 `buffer pool reads`
- 子任务 `#3` 证据：
  - `uv run pytest tests/api/analytics tests/integration/analytics_queries`
  - `pnpm --filter web test`
  - `pnpm --filter web build`
  - `pnpm openapi:check`
  - `pnpm test:analytics:clickhouse`
- 子任务 `#4` 已完成：overview / instance detail 已经把 capacity semantics 收敛成明确的 outlook、leaders 与 readout，而不是额外堆图表
- 子任务 `#5` 已完成：overview / instance detail 已提供 route-backed preset baseline，减少重复手动切换路径与窗口
- 子任务 `#6` 已完成：Epic 04 root signoff 已通过，API / web / live ClickHouse / smoke 证据链闭合
- 全部已批准 child task skeleton 已一次性落盘，满足 planning completeness 规则
- 子任务 `#2` 已完成：overview / instance detail 已接入 approved window query params 与 URL-backed window navigation，并通过 web 与 analytics API 验证
