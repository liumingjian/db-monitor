# Progress

## Summary

- Task shape: single-full
- Goal: 扩展 rule engine evaluation 与 alert pipeline 的第二引擎基线

## Recovery

- 任务: child `#3` 已完成，第二引擎 alert lifecycle 已经在 evaluation / pipeline / noise-control / recovery 语义上得到 focused 证明
- 形态: single-full
- 进度: 3/3
- 当前: 所有步骤已完成，等待 child `#4` 接手 web rule / alert surface 收敛
- 文件: `.codex-tasks/20260420-multi-engine-alerting-epic/tasks/20260420-03-rule-engine-pipeline/TODO.csv`
- 下一步: 进入 child `#4`，把当前已经可运行的 multi-engine alert baseline 真实暴露到 rules / alerts web surface 与 workflow messaging

## Runtime Closure

- `evaluate_samples()` 现在不只知道 `engine` 字段存在，而且有第二引擎样例证明：
  - Oracle rule 可以打开 alert
  - Oracle repeated trigger 会复用现有 alert，并遵守 suppression / retry 语义
  - Oracle recovery 会沿当前 notification backoff contract 收敛
- `tests/integration/alert_pipeline/test_alert_pipeline.py` 现在包含 Oracle route-level lifecycle proof，而不是只验证 MySQL
- `tests/alerting_support.py` 已泛化为可注入显式 instance 集合，避免 alert pipeline integration tests 继续被 MySQL-only helper 锁死

## Evidence

- `tests/rule_engine/test_rule_engine_evaluate.py` 新增 Oracle open/resolve lifecycle coverage
- `tests/integration/alert_pipeline/test_alert_pipeline.py` 新增 Oracle alert route lifecycle coverage，并为现有 MySQL create-rule payload 补齐显式 `engine`
- `tests/alerting_noise/test_noise_controls.py` 新增 Oracle suppression coverage
- `tests/recovery/test_alert_recovery.py` 新增 Oracle notification retry/backoff coverage

## Validation

- `uv run pytest tests/rule_engine/test_rule_engine_contract.py`
- `uv run pytest tests/rule_engine tests/integration/alert_pipeline tests/alerting_noise tests/recovery`
