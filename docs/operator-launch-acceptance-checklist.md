# Operator Launch Acceptance Checklist

- 确认当前上线目标仍然是 internal single-environment production
- 确认环境变量与 secrets 已按 [operator-launch-environment-baseline.md](./operator-launch-environment-baseline.md) 准备完成
- 确认目标环境若进入 rehearsal，已准备 [operator-prelaunch-rehearsal-runbook.md](./operator-prelaunch-rehearsal-runbook.md) 与 [operator-prelaunch-evidence-template.md](./operator-prelaunch-evidence-template.md)
- 确认 `pnpm test:hardening:signoff` 成功
- 确认 `pnpm test:oracle-runtime:signoff` 成功
- 确认 `pnpm test:launch-readiness:signoff` 成功
- 确认 `git diff --check` 成功
- 若目标环境无法满足 Oracle baseline，停止窗口并升级 scope 决策，而不是跳过 signoff
- 记录本次通过的 gate、时间戳和运行环境标识
- 若任一 gate 失败，立即转入 [operator-rollback-checklist.md](./operator-rollback-checklist.md)
