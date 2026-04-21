$ErrorActionPreference = "Stop"

$env:DB_MONITOR_POSTGRES_TEST_DSN = "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor"

docker compose up -d postgres

try {
    uv run pytest gates/alerting/test_alert_pipeline_postgres.py
}
finally {
    docker compose stop postgres
}
