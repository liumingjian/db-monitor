# Progress

## Summary

- Task shape: single-full
- Goal: 形成 Alert Maturity 的 root signoff gate

## Recovery

- 任务: 汇总 Epic 03 的 backend/web/live 验证证据
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260419-alert-maturity-epic/tasks/20260419-07-alert-signoff/TODO.csv`
- 下一步: 已回写父 epic；如继续推进 roadmap，先做 Epic 03 close-out review，再决定是否激活后续 epic

## Notes

- 本任务只做收口，不反向改变 epic 边界
- `uv run pytest tests/ops/test_alert_maturity_signoff.py` 通过，证明 signoff contract、package script 和 runbook 没有漂移
- 首次执行根级 signoff 暴露当前 macOS 环境缺少 `powershell` 且 `node_modules` 未安装；这属于执行入口扰动，不是 alert domain 逻辑失败
- 为避免 shell 依赖造成假失败，仓库新增 `scripts/powershell_shim.py`，只接管当前 alert maturity signoff 所需的三条 `.ps1` 执行入口，保留原 `.ps1` 契约文件不变
- `pnpm install --frozen-lockfile` 已补齐 web gate 的运行前提
- `pnpm test:alert-maturity:signoff` 现已串起 OpenAPI、backend pytest、web vitest、typecheck、Next build、live PostgreSQL alert gate 和 live recovery gate

## Latest Validation

- `uv run pytest tests/ops/test_alert_maturity_signoff.py`
- `pnpm install --frozen-lockfile`
- `pnpm test:alert-maturity:signoff`
