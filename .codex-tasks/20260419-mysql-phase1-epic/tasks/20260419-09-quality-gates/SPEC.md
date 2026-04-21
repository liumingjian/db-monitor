# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 建立 phase-one 的最终契约、集成和 smoke 门禁
- 把 OpenAPI 生成、契约 diff、后端集成测试、前端 smoke 和根级验证汇总到统一释放入口
- 形成真正可签收的 phase-one 完成标准

## Non-Goals

- 不新增业务功能
- 不用手工检查替代自动化验证

## Constraints

- 门禁必须可在仓库根目录一键运行
- OpenAPI 检查必须显式比较契约变化
- 后端集成测试必须覆盖控制面、指标链路和告警链路
- smoke 流程必须覆盖 phase-one 主路径

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `TypeScript + Python 3.12`
- **Package manager**: `pnpm + uv`
- **Test framework**: `pytest + frontend smoke/e2e`
- **Build command**: `pnpm build && uv run pytest`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 若各子任务各自定义验证方式，最终不会形成统一 release gate
- [ ] 若 OpenAPI diff 不纳入门禁，前后端会再次发生契约漂移
- [ ] 若 smoke 只覆盖页面渲染，不覆盖关键主路径，phase-one 签收价值不足

## Deliverables

- 根级质量门禁脚本与命令
- OpenAPI 生成与 diff 检查
- 后端集成测试聚合入口
- 前端 smoke/e2e 聚合入口与 release checklist

## Done-When

- [ ] phase-one 的根级验证命令稳定可运行
- [ ] 契约、集成和 smoke 能作为最终签收依据
- [ ] 子任务成果全部被纳入统一质量门禁

## Final Validation Command

```bash
pnpm lint && pnpm typecheck && uv run ruff check . && uv run mypy apps && uv run pytest tests && pnpm openapi:check && pnpm smoke
```

## Demo Flow

1. 从仓库根目录执行最终验证命令
2. 查看 OpenAPI diff 结果
3. 查看后端集成测试和前端 smoke 结果

