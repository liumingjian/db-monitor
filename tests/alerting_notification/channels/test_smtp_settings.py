from db_monitor_api.alerting.notification.channels.smtp_settings import (
    SMTPSettings,
)


def test_from_env_with_tls_defaults_to_port_465() -> None:
    settings = SMTPSettings.from_env(
        {
            "DB_MONITOR_SMTP_HOST": "mail.example.com",
            "DB_MONITOR_SMTP_FROM": "alerts@example.com",
            "DB_MONITOR_SMTP_USE_TLS": "true",
        }
    )

    assert settings is not None
    assert settings.host == "mail.example.com"
    assert settings.from_addr == "alerts@example.com"
    assert settings.use_tls is True
    assert settings.port == 465
    assert settings.username is None
    assert settings.password is None


def test_from_env_without_tls_defaults_to_port_25() -> None:
    settings = SMTPSettings.from_env(
        {
            "DB_MONITOR_SMTP_HOST": "mail.example.com",
            "DB_MONITOR_SMTP_FROM": "alerts@example.com",
            "DB_MONITOR_SMTP_USE_TLS": "false",
        }
    )

    assert settings is not None
    assert settings.use_tls is False
    assert settings.port == 25


def test_from_env_missing_host_returns_none() -> None:
    assert (
        SMTPSettings.from_env({"DB_MONITOR_SMTP_FROM": "alerts@example.com"})
        is None
    )


def test_from_env_missing_from_addr_returns_none() -> None:
    assert (
        SMTPSettings.from_env({"DB_MONITOR_SMTP_HOST": "mail.example.com"})
        is None
    )


def test_from_env_respects_explicit_port_and_credentials() -> None:
    settings = SMTPSettings.from_env(
        {
            "DB_MONITOR_SMTP_HOST": "mail.example.com",
            "DB_MONITOR_SMTP_FROM": "alerts@example.com",
            "DB_MONITOR_SMTP_PORT": "2525",
            "DB_MONITOR_SMTP_USERNAME": "alice",
            "DB_MONITOR_SMTP_PASSWORD": "secret",
            "DB_MONITOR_SMTP_USE_TLS": "false",
        }
    )

    assert settings is not None
    assert settings.port == 2525
    assert settings.username == "alice"
    assert settings.password == "secret"
    assert settings.use_tls is False
