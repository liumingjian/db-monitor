# Progress

## Summary

- Task shape: single-full
- Goal: 在 web detail flow 中暴露 Oracle 最小趋势能力

## Recovery

- 任务: 已完成 Oracle web detail flow 的最小趋势呈现收口
- 形态: single-full
- 进度: 3/3
- 当前: 已完成，等待父 epic 切到 `#6`
- 文件: `.codex-tasks/20260420-oracle-data-plane-epic/tasks/20260420-05-oracle-web-surface/TODO.csv`
- 下一步: 由子任务 `#6` 汇总 backend / live gate / web / smoke 证据，完成 Oracle data-plane signoff

## Notes

- 已完成的最小控制输入：
  - `supportsInstanceAnalytics` 现在允许 Oracle 详情页进入 trends 分支
  - `buildInstancesFlowModel` 会按选中实例 `engine` 选择 preview trend 和 capacity readout 解释
  - Oracle detail readout 已收敛为最小 sessions / waits / user calls / physical reads 视角，不伪装成 MySQL lag / buffer-pool 语义
  - capability 文案、instances onboarding copy、以及 instance preset descriptions 已同步更新为“最小趋势可见，但 overview 与更深诊断仍未 full parity”
- 当前仍显式保留的边界：
  - 不新增 Oracle 专属页面家族
  - 不承诺 full overview parity
  - 不把 MySQL 专用容量洞察直接平移成 Oracle 等价物

## Validation

- `pnpm --filter web test`
- `pnpm --filter web typecheck`
- `pnpm --filter web build`
