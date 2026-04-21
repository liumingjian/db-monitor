# Progress

## Summary

- Task shape: single-full
- Goal: 让 overview / instance detail 支持 approved time window 切换

## Recovery

- 任务: 解锁当前 analytics API 已有的多窗口能力
- 形态: single-full
- 进度: 3/3
- 当前: 已完成
- 文件: `.codex-tasks/20260420-analytics-capacity-epic/tasks/20260420-02-time-window-nav/TODO.csv`
- 下一步: 后续 child task 将在当前 URL-backed contract 之上继续补 analytics depth 与 presets

## Notes

- 当前 API contract 已支持 `15m / 1h / 6h / 24h`
- 当前 web 只通过 `DEFAULT_TIME_WINDOW` 取数，没有窗口切换交互
- 已新增共享 `TimeWindowNav` 组件和 `parseTimeWindow()` helper
- overview / instance detail 现在都通过 query param 读取 approved window，并把当前 window 明确显示在页面上

## Latest Validation

- `pnpm --filter web test`
- `pnpm --filter web typecheck`
- `pnpm --filter web build`
- `uv run pytest tests/api/analytics tests/integration/analytics_queries`
