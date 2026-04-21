$ErrorActionPreference = "Stop"

$env:DB_MONITOR_CLICKHOUSE_DATABASE = "db_monitor"
$env:DB_MONITOR_CLICKHOUSE_ENDPOINT = "http://127.0.0.1:8123"
$env:DB_MONITOR_CLICKHOUSE_PASSWORD = "db_monitor"
$env:DB_MONITOR_CLICKHOUSE_USERNAME = "db_monitor"

docker compose up -d clickhouse

try {
    uv run pytest gates/analytics/test_analytics_clickhouse_live.py
}
finally {
    docker compose stop clickhouse
}
