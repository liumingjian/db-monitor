# Operator Release Baseline

## Scope

这份 runbook 定义当前仓库的最小 operator 发布基线。
目标不是建设完整 CI/CD，而是把现有可运行的本地发布、检查和回滚流程固化为显式步骤。

## Preconditions

- 已安装 `docker`
- 已安装 `pnpm`
- 已准备仓库根目录下的 `.venv`
- 当前根级 `pnpm` 命令已适配 macOS，本地无需系统 PowerShell
- `pnpm smoke` 使用 Playwright 自管 `chromium`，本地无需安装 Microsoft Edge
- 本地端口 `38100`、`38101`、`5432`、`6379`、`8123`、`3306` 未被其他进程占用

## Start Procedure

1. 启动基础依赖：
   - `pnpm dev:deps:up`
2. 如需验证 schema bootstrap 与运行时 readiness，执行：
   - `pnpm test:schema:bootstrap`
   - `pnpm test:api:readiness`
3. 如需验证后台进程与恢复路径，执行：
   - `pnpm test:background-processes`
   - `pnpm test:recovery-paths`

## Verify Procedure

1. 执行根级 smoke：
   - `pnpm smoke`
2. 如 smoke 失败，先查看：
   - `.tmp-smoke-api.err.log`
   - `.tmp-smoke-api.out.log`
   - `.tmp-smoke-web.err.log`
   - `.tmp-smoke-web.out.log`
3. 如需进一步确认运行时硬化 gates，按顺序执行：
   - `pnpm test:api:readiness`
   - `pnpm test:background-processes`
   - `pnpm test:schema:bootstrap`
   - `pnpm test:recovery-paths`

## Rollback Trigger

出现以下任一信号，默认停止继续发布并进入回滚：

- `pnpm smoke` 失败
- `pnpm test:api:readiness` 失败
- `pnpm test:background-processes` 失败
- `pnpm test:schema:bootstrap` 失败
- `pnpm test:recovery-paths` 失败
- Docker 依赖无法稳定拉起，或本地端口冲突无法消除

## Rollback Procedure

1. 停止本地依赖：
   - `pnpm dev:deps:down`
2. 清理残留 smoke 进程日志并确认端口释放。
3. 记录最后一个失败 gate、错误日志路径和当前运行命令，再重新开始下一次发布尝试。

## Checklists

- Release checklist: [operator-release-checklist.md](./operator-release-checklist.md)
- Rollback checklist: [operator-rollback-checklist.md](./operator-rollback-checklist.md)
