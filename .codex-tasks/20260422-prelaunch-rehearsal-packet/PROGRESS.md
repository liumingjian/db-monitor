# Progress

## Summary

- Task shape: single-full
- Goal: 把 Epic 13 之后的目标环境试运行推进成一个 repo-local rehearsal packet

## Recovery

- 任务: 已完成
- 形态: single-full
- 进度: 4/4
- 当前: 已关闭；prelaunch rehearsal packet 已落盘并接入验证
- 文件: `.codex-tasks/20260422-prelaunch-rehearsal-packet/TODO.csv`
- 下一步: operator 按 runbook 在目标环境执行一次真实 rehearsal，并根据结果决定是否只做 launch baseline 小收口，还是需要 Epic 14 级别的 scale / failure-domain 工作

## Control Contract

- Primary Setpoint: 在不扩成新 epic 的前提下，把“去目标环境试运行”变成可执行、可留证据、可做 go/no-go 的正式资产
- Acceptance: rehearsal runbook、evidence template、ops tests 与 launch signoff wiring 全部存在并通过
- Guardrails:
  - 不发明仓库里不存在的 deployment stack
  - 不把 Oracle scope 从现有 signoff 里静默移除
  - 不把 rehearsal packet 扩成新的 HA/DR 设计
- Sampling Plan: 先记录当前 gap，再落 docs，之后加 ops tests，最后回归 launch readiness signoff

## Current Gap

- 当前仓库已经有 launch baseline，但还缺一份专门面向目标环境试运行的 packet：
  - 没有单独的 prelaunch rehearsal runbook
  - 没有 fill-in evidence template
  - 还存在一处口径漂移：release runbook 把 Oracle 写成“条件性”，但当前 `pnpm test:launch-readiness:signoff` 实际会强制串上 Oracle runtime signoff
- 因为仓库里没有额外的目标环境编排资产，下一步最合理的动作是把试运行流程固化成 operator packet，而不是继续猜新的部署形态

## Latest Evidence

- 新增 rehearsal 资产：
  - `docs/operator-prelaunch-rehearsal-runbook.md`
  - `docs/operator-prelaunch-evidence-template.md`
- 更新 launch baseline 资产：
  - `docs/operator-release-baseline.md`
  - `docs/operator-launch-acceptance-checklist.md`
  - `scripts/test-launch-readiness-signoff.ps1`
  - `scripts/powershell_shim.py`
- 新增并通过的 ops tests：
  - `tests/ops/test_prelaunch_rehearsal_packet.py`
  - `python3 -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' uv run pytest tests/ops/test_prelaunch_rehearsal_packet.py tests/ops/test_launch_readiness_baseline.py tests/ops/test_release_baseline.py -q`
- 最终回归：
  - `pnpm test:launch-readiness:signoff`

## Next Operator Path

1. 在目标机器上按 `docs/operator-prelaunch-rehearsal-runbook.md` 准备环境并填写 evidence template。
2. 执行 `pnpm test:launch-readiness:signoff`，收集 gate 与日志证据。
3. 若问题仍落在环境合同、依赖准备、回滚或门禁漂移，继续按当前 launch baseline 修复。
4. 若暴露出容量瓶颈、单点失效、备份恢复或明确 RTO/RPO 诉求，再把证据升级为 `Epic 14` 的激活输入。
