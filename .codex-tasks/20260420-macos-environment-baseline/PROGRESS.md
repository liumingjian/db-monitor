# Progress

## Summary

- Task shape: single-full
- Goal: 为当前仓库建立可在 macOS 上直接执行的环境脚本与 gate 基线

## Recovery

- 任务: 收敛当前开发 / smoke / live gate 的 macOS 执行入口
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260420-macos-environment-baseline/TODO.csv`
- 下一步: 当前环境基线已完成；后续继续跟随 `.codex-tasks/20260420-analytics-capacity-epic/SUBTASKS.csv`

## Control Contract

- Primary Setpoint: 当前根级开发与 gate 命令可在 macOS 上直接执行，不依赖系统安装 `powershell`
- Acceptance: `pnpm test:hardening:signoff` 与 `pnpm test:alert-maturity:signoff` 通过
- Guardrails: 不删除 live gate，不改变根级命令名，不让 runbook 与 package scripts 漂移
- Sampling Plan: 先做 L0 合同测试与脚本审计，再跑 L1/L2 根级 signoff
- Known Delays: `pnpm install`、Next build、Docker 镜像拉取和 live gate 启停会带来分钟级时延
- Recovery Target: 若改动导致 gate 失败，应能通过 repo-local runner 或最小脚本回退在当前任务内恢复
- Rollback Trigger: 若跨平台改造开始触碰业务语义或引入新的 fake green path，停止扩大范围，收缩回纯执行层
- Constraints: 仅改执行层、文档与必要测试；业务 API / 数据模型不在本任务改动范围
- Boundary: `package.json`、`scripts/`、相关 `tests/ops`、runbook/checklist 文档
- Coupling Notes: hardening signoff、alert maturity signoff、smoke 和 live gate 共用根级脚本入口

## Notes

- 当前仓库已经有 `scripts/powershell_shim.py`，但只覆盖 alert maturity signoff 相关的少数脚本
- 仍存在 `smoke:web`、`test:hardening:signoff` 和多个 live gate 直接绑定 `powershell` 的情况
- 已把当前真实需要的 `dev:deps:*`、`smoke:web`、hardening live gates、alert maturity signoff 入口统一收敛到 repo-local runner
- `pyproject.toml` 已把 `.venv` 纳入 Ruff exclude，避免本地虚拟环境把第三方包噪声抬进项目 lint gate
- smoke 现已使用 Playwright 自管 `chromium`，并把本地 HTTP 主机口径统一到 `localhost`，避免 macOS 上的 cookie 域漂移
- live background process gate 还修复了 Redis dedupe set 未清理导致的假 idle 问题

## Latest Validation

- `uv run pytest tests/ops`
- `pnpm dev:deps:up`
- `pnpm dev:deps:down`
- `pnpm smoke`
- `pnpm test:hardening:signoff`
- `pnpm test:alert-maturity:signoff`
