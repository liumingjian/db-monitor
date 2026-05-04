# Operator Release Checklist

- 确认 `docker`、`pnpm`、`.venv` 可用
- 确认当前上线目标仍然是 internal single-environment production
- 确认环境变量与 secrets 已按 `operator-launch-environment-baseline.md` 准备完成
- 确认 `pnpm dev:deps:up` 成功
- 确认 `pnpm test:hardening:signoff` 成功
- 确认 `pnpm test:oracle-runtime:signoff` 成功
- 确认 `pnpm test:launch-readiness:signoff` 成功
- 记录当前通过的命令和时间戳
