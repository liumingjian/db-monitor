$ErrorActionPreference = "Stop"

$env:DB_MONITOR_POSTGRES_DSN = "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor"
$env:DB_MONITOR_REDIS_URL = "redis://127.0.0.1:6379/0"

docker compose up -d postgres redis

try {
    uv run pytest gates/recovery/test_recovery_paths_live.py
}
finally {
    docker compose stop postgres redis
}
