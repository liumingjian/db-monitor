# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 建立符合 phase-one 架构的 monorepo 目录和根级工具链
- 落下 `apps/`、`packages/`、共享配置、开发脚本与数据库测试基线
- 让后续子任务可以在统一命令、统一目录和统一门禁上继续开发

## Non-Goals

- 实现任何业务接口、页面或告警逻辑
- 引入旧 Lepus 运行时代码或兼容层

## Constraints

- 根级包管理必须使用 `pnpm`
- Python 工具链必须使用 `uv`，目标版本 `Python 3.12`
- 前端和后端目录要预留给 `Next.js`、`FastAPI`、`scheduler`、`worker-mysql`、`rule-engine`、`notifier`
- 质量门禁要能从根目录统一调用

## Environment

- **Project root**: `C:\Users\14142\Desktop\ai-project\db-monitor`
- **Language/runtime**: `TypeScript + Python 3.12`
- **Package manager**: `pnpm + uv`
- **Test framework**: `pytest + frontend test runner (to be wired in this task)`
- **Build command**: `pnpm build`
- **Existing test count**: `0 planned`

## Risk Assessment

- [ ] 根级 workspace 结构若定义不稳，后续所有子任务都会返工
- [ ] Node/Python 多工具链若没有统一入口，本地开发会持续失稳
- [ ] 数据库测试 compose 若未纳入脚手架，后续集成测试成本会偏高

## Deliverables

- root workspace 配置与共享脚本
- `apps/` 与 `packages/` 初始目录
- 本地开发启动脚本和数据库测试 compose 基线
- 根级 lint、typecheck、test 命令骨架

## Done-When

- [ ] Monorepo 目录和根级工具链可用
- [ ] 后续子任务不再需要重新定义根级命令和目录约定
- [ ] 基础质量门禁可以从仓库根目录执行

## Final Validation Command

```bash
pnpm lint && pnpm typecheck && uv run ruff check . && uv run mypy apps
```

## Demo Flow

1. 安装 `pnpm` 与 `uv` 依赖
2. 从根目录启动本地开发脚本和测试数据库
3. 从根目录执行基础门禁命令

