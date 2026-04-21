$ErrorActionPreference = "Stop"

pnpm openapi:check
uv run pytest tests/ops/test_alert_maturity_signoff.py tests/alerting_contract tests/alerting_workflow tests/alerting_noise tests/alerting_delivery tests/recovery tests/api/alerting tests/integration/alert_pipeline
pnpm test
pnpm typecheck
pnpm build
pnpm test:alert-pipeline:postgres
pnpm test:recovery-paths
