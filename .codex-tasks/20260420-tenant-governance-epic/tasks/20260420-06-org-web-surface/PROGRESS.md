# Progress

## Summary

- Task shape: single-full
- Goal: 在 API 与 web surface 上暴露组织治理最小入口

## Recovery

- 任务: 已完成
- 形态: single-full
- 进度: 3/3
- 当前: 子任务已收口，父 epic 可进入最终 signoff
- 文件: `.codex-tasks/20260420-tenant-governance-epic/tasks/20260420-06-org-web-surface/TODO.csv`
- 下一步: 进入子任务 `#7 Run tenant governance signoff gates`

## Evidence

- Session snapshot 现在显式暴露：
  - `activeOrganization`
  - `organizationMemberships`
- server-side session fetch 已把 typed auth contract 中的组织信息映射进 web shell
- shell model / chrome 现在会显示 active organization、roles 与 membership count
- settings 页面新增了最小治理入口：
  - active organization 说明卡
  - membership scope 列表
  - 明确说明当前 shell 是按组织收敛、但还没有做 org switching
- 现有 API contract version 与 web data layer 已保持同步为 `0.5.0`

## Validation

- `pnpm openapi:check`
- `pnpm --filter web test`
- `pnpm --filter web typecheck`
- `pnpm --filter web build`
