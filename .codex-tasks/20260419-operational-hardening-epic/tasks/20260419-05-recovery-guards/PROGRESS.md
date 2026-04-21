# Progress

## Summary

- Task shape: single-full
- Goal: 建立可验证的重试、幂等与恢复基线

## Recovery

- 任务: 收敛后台链路的恢复语义，防止重复副作用
- 形态: single-full
- 进度: 4/4
- 当前: 已完成
- 文件: `.codex-tasks/20260419-operational-hardening-epic/tasks/20260419-05-recovery-guards/TODO.csv`
- 下一步: 将 epic 控制权切换到 `#6 release baseline`

## Notes

- 上游 `#3 process entrypoints` 与 `#4 schema bootstrap` 已完成，恢复语义进入可实现状态
- 本任务已收敛两个高风险重复副作用面：
  - worker 现在只对 collector 失败做显式 backoff retry；sink 失败会因非幂等写边界而显式停止，不做隐式重试
  - queue 现在对 pending job 做去重，防止 scheduler 周期性放大同一实例的待处理任务
  - alert lifecycle 现在基于历史事件做 notification retry backoff，成功通知不会被重复发送
- 新增验证资产：
  - `tests/recovery/test_pipeline_recovery.py`
  - `tests/recovery/test_alert_recovery.py`
  - `gates/recovery/test_recovery_paths_live.py`
  - `scripts/test-recovery-paths.ps1`
- 本任务验证已通过：
  - `uv run pytest tests/recovery tests/worker_mysql tests/scheduler tests/operations/processes`
  - `uv run pytest tests/recovery tests/integration`
  - `uv run ruff check apps tests gates`
  - `uv run mypy apps tests gates`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-recovery-paths.ps1`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-alert-pipeline-postgres.ps1`
  - `powershell -ExecutionPolicy Bypass -File ./scripts/test-background-processes.ps1`
