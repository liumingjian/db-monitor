import pytest

from db_monitor_api.settings import RuntimeMode, load_api_settings


def test_load_api_settings_defaults_to_local_runtime() -> None:
    settings = load_api_settings({})

    assert settings.runtime_mode is RuntimeMode.LOCAL
    assert settings.postgres_dsn is None
    assert settings.clickhouse is None


def test_load_api_settings_requires_clickhouse_and_postgres_in_postgres_mode() -> None:
    with pytest.raises(RuntimeError, match="Missing required environment variable:"):
        load_api_settings({"DB_MONITOR_RUNTIME": RuntimeMode.POSTGRES.value})


def test_load_api_settings_reads_postgres_runtime_values() -> None:
    settings = load_api_settings(
        {
            "DB_MONITOR_CLICKHOUSE_DATABASE": "db_monitor",
            "DB_MONITOR_CLICKHOUSE_ENDPOINT": "http://127.0.0.1:8123",
            "DB_MONITOR_CLICKHOUSE_PASSWORD": "db_monitor",
            "DB_MONITOR_CLICKHOUSE_USERNAME": "db_monitor",
            "DB_MONITOR_POSTGRES_DSN": "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor",
            "DB_MONITOR_RUNTIME": RuntimeMode.POSTGRES.value,
        }
    )

    assert settings.runtime_mode is RuntimeMode.POSTGRES
    assert settings.postgres_dsn == "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor"
    assert settings.clickhouse is not None
    assert settings.clickhouse.endpoint == "http://127.0.0.1:8123"
