# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 实现 phase-one 对内可用的核心 Web 页面与交互流
- 覆盖实例接入、实例列表/详情、overview dashboard、告警列表/详情、规则管理和系统设置
- 将 PRD 中的核心用户故事转成可操作的前端主路径

## Non-Goals

- 不做慢查询深挖、高级报表或多引擎页面
- 不绕过生成客户端直接访问后端或数据库

## Constraints

- 页面能力必须建立在 `#5` 和 `#6` 的正式 API 上
- 图表统一使用 `ECharts`
- 组件和布局应复用 `#7` 中的共享原语
- 交互范围只覆盖 phase-one，避免向未来多租户或高级报表扩张

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `TypeScript / Node 22 LTS`
- **Package manager**: `pnpm`
- **Test framework**: `frontend unit/integration tests + smoke`
- **Build command**: `pnpm --filter web build`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 若页面在 API 未稳定前先落地，后续会反复改动
- [ ] 接入流程、dashboard 和 alert 页面若各自造状态管理，维护成本会迅速变高
- [ ] 若规则和设置页面不复用 shared primitives，会偏离 phase-one UI 基线

## Deliverables

- MySQL 实例接入表单、实例列表和详情页面
- overview dashboard 与核心趋势图
- alert list/detail、rule management、system settings 页面
- Web 主路径 smoke 流程

## Done-When

- [ ] 内部用户可以完成 phase-one 主要使用流程
- [ ] 页面与 API 契约一致，不再额外做页面层拼装
- [ ] 关键页面有自动化测试和 smoke 覆盖

## Final Validation Command

```bash
pnpm --filter web test && pnpm smoke:web
```

## Demo Flow

1. 登录后进入 overview dashboard
2. 新增 MySQL 实例并查看详情趋势
3. 浏览告警、规则和系统设置页面

