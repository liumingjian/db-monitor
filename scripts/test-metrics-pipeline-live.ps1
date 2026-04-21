$ErrorActionPreference = "Stop"

$env:DB_MONITOR_CLICKHOUSE_DATABASE = "db_monitor"
$env:DB_MONITOR_CLICKHOUSE_ENDPOINT = "http://127.0.0.1:8123"
$env:DB_MONITOR_CLICKHOUSE_PASSWORD = "db_monitor"
$env:DB_MONITOR_CLICKHOUSE_USERNAME = "db_monitor"
$env:DB_MONITOR_REDIS_URL = "redis://127.0.0.1:6379/0"

docker compose up -d clickhouse redis

try {
    uv run pytest gates/metrics_pipeline/test_metrics_pipeline_live.py
}
finally {
    docker compose stop clickhouse redis
}
