# Task Specification

## Task Shape

- **Shape**: `single-full`

## Goals

- 让告警、工作流与审计记录在组织上下文下保持一致

## Final Validation Command

```bash
uv run pytest tests/api/alerting tests/integration/alert_pipeline tests/recovery
```
