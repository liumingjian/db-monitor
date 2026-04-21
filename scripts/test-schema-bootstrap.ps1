$ErrorActionPreference = "Stop"

$env:DB_MONITOR_RUNTIME = "postgres"
$env:DB_MONITOR_POSTGRES_DSN = "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor"
$env:DB_MONITOR_CLICKHOUSE_DATABASE = "db_monitor"
$env:DB_MONITOR_CLICKHOUSE_ENDPOINT = "http://127.0.0.1:8123"
$env:DB_MONITOR_CLICKHOUSE_PASSWORD = "db_monitor"
$env:DB_MONITOR_CLICKHOUSE_USERNAME = "db_monitor"
$env:PYTHONPATH = (Resolve-Path "./apps/api/src").Path

docker compose up -d postgres clickhouse

try {
    uv run pytest gates/schema/test_schema_bootstrap_live.py
}
finally {
    docker compose stop postgres clickhouse
}
