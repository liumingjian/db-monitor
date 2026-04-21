# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 建立 phase-one 前端应用壳与路由保护基础
- 接入 OpenAPI 生成客户端、TanStack Query provider 和共享 UI 原语
- 为后续监控页面提供稳定的页面布局、导航和认证态边界

## Non-Goals

- 不实现完整业务页面
- 不在前端复制业务校验或数据库访问逻辑

## Constraints

- 前端必须保持 `Next.js` 纯 UI 层定位
- 数据访问必须通过 OpenAPI 生成客户端和统一 query layer
- 图表技术栈统一为 `ECharts`
- 样式与组件应围绕 `Tailwind CSS v4 + shadcn/ui`

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `TypeScript / Node 22 LTS`
- **Package manager**: `pnpm`
- **Test framework**: `frontend unit/integration tests`
- **Build command**: `pnpm --filter web build`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 若客户端生成和 query provider 未先稳定，业务页面会重复造轮子
- [ ] 若认证态边界只做前端判断，容易造成越权错觉
- [ ] 若共享表格、表单、图表原语过晚建立，页面开发会碎片化

## Deliverables

- Next.js 应用壳与受保护路由基础
- OpenAPI 生成客户端与 query provider
- 共享布局、表格、表单、图表基础原语
- 认证接入与基础导航

## Done-When

- [ ] 前端应用壳可运行并受认证保护
- [ ] OpenAPI 生成客户端接入完成
- [ ] 后续业务页面不需要重复建立 provider 和基础原语

## Final Validation Command

```bash
pnpm --filter web lint && pnpm --filter web typecheck && pnpm --filter web test
```

## Demo Flow

1. 打开 Web 应用并进入登录页
2. 登录后进入受保护壳层
3. 通过共享 provider 加载基础查询和导航

