$ErrorActionPreference = "Stop"

pnpm openapi:check
uv run pytest tests/alerting_notification tests/rule_engine tests/api/alerting tests/alerting_contract tests/alerting_workflow tests/alerting_noise tests/alerting_delivery tests/schema/test_schema_bootstrap.py
pnpm test
pnpm typecheck
