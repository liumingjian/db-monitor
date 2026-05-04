# Progress

## Summary

- Task shape: single-full
- Goal: 把 audit 覆盖从"用户/角色 + kill"扩展到"rule + instance + override + channel binding"全写路径

## Recovery

- 任务: Slice 2 child #4
- 形态: single-full
- 进度: 0/N
- 当前: PLANNED（依赖 child #3 + ADR-0015 决议）
- 文件: `.codex-tasks/20260504-slice02-alert-maturity-epic/tasks/20260504-04-audit-scope-expansion/`
- 下一步: ADR-0015 转 Accepted → 设计 audit_entries.target_type + diff_summary schema 迁移 v12→v13

## Reference

- ADR-0015 审计范围扩展
- Epic 10 引入的 `audit_entries` 表
- Epic 15 引入的 `instance.process.kill` 审计模式

## Notes

- service 层 explicit `audit_service.log(...)` 调用（不用装饰器，便于 review 时 grep）
- webhook secret / SMS access_key 走 SHA256 hash 进 audit；不存原文
- 失败请求（4xx/5xx）不入审计（避免污染）
- web Audit 页加 4 维过滤（actor / target_type / action / time）；前端用 Slice 1.5 已建的 Audit Feed
