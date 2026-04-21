# Progress

## Summary

- Task shape: single-full
- Goal: 给 web surface 增加最小 engine-aware 语义

## Recovery

- 任务: 已完成 web engine-aware cue 提升
- 形态: single-full
- 进度: 3/3
- 当前: 已完成最终验证
- 文件: `.codex-tasks/20260420-multi-engine-validation-epic/tasks/20260420-05-engine-aware-web/TODO.csv`
- 下一步: 将父 epic 切换到子任务 `#6 Run multi-engine validation signoff`

## Notes

- 前置子任务已经让控制面和 dispatch seam 都具备真实 `engine` 维度，因此当前 web 已经不应该继续把实例表述成隐式 MySQL-only
- 本任务保持了最小 surface 扩张：
  - onboarding form 增加轻量 engine selector，并把 Oracle 的 DSN/service name 语义写入文案
  - inventory card 显示 engine badge 和 capability boundary
  - detail route 复用现有路径，但 Oracle 实例不再调用 MySQL analytics endpoint，而是显式展示 capability boundary
- 本轮验证证据：
  - `pnpm --filter web test`
  - `pnpm --filter web typecheck`
  - `pnpm --filter web build`
- 这一步没有承诺 Oracle analytics parity；它只是把当前已知的能力边界诚实地暴露到了 UI 上
