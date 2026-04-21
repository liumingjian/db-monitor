$ErrorActionPreference = "Stop"

$env:DB_MONITOR_POSTGRES_TEST_DSN = "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor"
$env:DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER = "oracle-xe-local"
$env:DB_MONITOR_ORACLE_TEST_HOST = "127.0.0.1"
$env:DB_MONITOR_ORACLE_TEST_PASSWORD = "oracle"
$env:DB_MONITOR_ORACLE_TEST_PORT = "15211"
$env:DB_MONITOR_ORACLE_TEST_SERVICE = "XE"
$env:DB_MONITOR_ORACLE_TEST_USERNAME = "system"

docker compose up -d postgres oracle-xe
$env:DB_MONITOR_ORACLE_SQLPLUS_DOCKER_CONTAINER = (docker compose ps -q oracle-xe).Trim()

try {
    uv run pytest gates/control_plane/test_control_plane_oracle_live.py
}
finally {
    docker compose stop postgres oracle-xe
}
