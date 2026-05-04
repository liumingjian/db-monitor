"""SMTP notifier configuration.

Pure-data settings parsed from the process environment. Returning ``None`` from
``from_env`` signals that the SMTP channel should be considered disabled so the
caller can skip registering the notifier instead of failing later at send time.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

_ENV_HOST = "DB_MONITOR_SMTP_HOST"
_ENV_PORT = "DB_MONITOR_SMTP_PORT"
_ENV_USERNAME = "DB_MONITOR_SMTP_USERNAME"
_ENV_PASSWORD = "DB_MONITOR_SMTP_PASSWORD"
_ENV_FROM = "DB_MONITOR_SMTP_FROM"
_ENV_USE_TLS = "DB_MONITOR_SMTP_USE_TLS"

_DEFAULT_TLS_PORT = 465
_DEFAULT_PLAIN_PORT = 25
_DEFAULT_TIMEOUT_SECONDS = 10.0
_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})
_FALSE_TOKENS = frozenset({"0", "false", "no", "off"})


def _parse_bool(raw: str | None, *, default: bool) -> bool:
    if raw is None:
        return default
    token = raw.strip().lower()
    if token in _TRUE_TOKENS:
        return True
    if token in _FALSE_TOKENS:
        return False
    return default


def _parse_port(raw: str | None, *, use_tls: bool) -> int:
    if raw is None or raw.strip() == "":
        return _DEFAULT_TLS_PORT if use_tls else _DEFAULT_PLAIN_PORT
    return int(raw)


def _clean(raw: str | None) -> str | None:
    if raw is None:
        return None
    value = raw.strip()
    return value or None


@dataclass(frozen=True)
class SMTPSettings:
    host: str
    port: int
    username: str | None
    password: str | None
    from_addr: str
    use_tls: bool
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> SMTPSettings | None:
        host = _clean(env.get(_ENV_HOST))
        from_addr = _clean(env.get(_ENV_FROM))
        if host is None or from_addr is None:
            return None
        use_tls = _parse_bool(env.get(_ENV_USE_TLS), default=True)
        port = _parse_port(env.get(_ENV_PORT), use_tls=use_tls)
        return cls(
            host=host,
            port=port,
            username=_clean(env.get(_ENV_USERNAME)),
            password=_clean(env.get(_ENV_PASSWORD)),
            from_addr=from_addr,
            use_tls=use_tls,
        )
