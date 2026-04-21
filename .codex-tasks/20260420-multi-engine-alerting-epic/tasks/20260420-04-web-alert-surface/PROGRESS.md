# Progress

## Summary

- Task shape: single-full
- Goal: 实现 engine-aware web rule and alert surface 与 workflow messaging

## Recovery

- 任务: child `#4` 已完成，rules / alerts web surface 已经开始真实承接 multi-engine alert baseline
- 形态: single-full
- 进度: 3/3
- 当前: 所有步骤已完成，等待 child `#5` 接手 notifier / delivery / on-call semantics
- 文件: `.codex-tasks/20260420-multi-engine-alerting-epic/tasks/20260420-04-web-alert-surface/TODO.csv`
- 下一步: 进入 child `#5`，继续把 notifier、delivery 与 on-call workflow semantics 从“去掉 MySQL-only copy”推进到真正 coherent 的 mixed-engine triage 语义

## Surface Closure

- rules page 现在显式展示：
  - `engine` 选择
  - 当前批准的 rule catalog
  - engine-scoped scope copy 与 active rule engine cues
- alerts list / alert detail / triage panel 现在显式展示 alert.engine，不再让 Oracle alert 看起来像隐式 MySQL 事件
- note placeholder 与 workflow copy 已从 “replication lag / replica IO state” 这类 MySQL-specific 文案收敛到 engine-agnostic triage 语义

## Evidence

- `apps/web/app/rules/page.tsx` 已接入 `listRuleCatalog()`，并在现有 route family 下渲染 engine select + supported metrics
- `apps/web/app/alerts/page.tsx`、`apps/web/app/alerts/[alertId]/page.tsx`、`apps/web/src/components/alert-triage-panel.tsx` 已补 engine cues 与更中性的 workflow copy
- `apps/web/src/monitoring-ui.ts` / `monitoring-preview.ts` / `packages/ui/src/index.ts` 已同步规则表单默认值、catalog preview 与 mixed-engine placeholder
- `apps/web/tests/alerts.test.ts`、`apps/web/tests/data-layer.test.ts` 已同步新的 contract/runtime expectation

## Validation

- `pnpm --filter web test`
- `pnpm --filter web typecheck`
