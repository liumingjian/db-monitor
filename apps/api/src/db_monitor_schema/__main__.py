import argparse
import json
import os
from dataclasses import asdict

from db_monitor_api.settings import ClickHouseSettings, load_api_settings
from db_monitor_schema.clickhouse import bootstrap_clickhouse_schema, verify_clickhouse_schema
from db_monitor_schema.contract import SchemaVersion
from db_monitor_schema.postgres import bootstrap_postgres_schema, verify_postgres_schema
from db_monitor_schema.runtime import bootstrap_api_runtime_schema, verify_api_runtime_schema


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m db_monitor_schema")
    subparsers = parser.add_subparsers(dest="command", required=True)

    postgres_bootstrap = subparsers.add_parser("bootstrap-postgres")
    postgres_bootstrap.add_argument("--postgres-dsn")

    postgres_verify = subparsers.add_parser("verify-postgres")
    postgres_verify.add_argument("--postgres-dsn")

    clickhouse_bootstrap = subparsers.add_parser("bootstrap-clickhouse")
    _add_clickhouse_arguments(clickhouse_bootstrap)

    clickhouse_verify = subparsers.add_parser("verify-clickhouse")
    _add_clickhouse_arguments(clickhouse_verify)

    subparsers.add_parser("bootstrap-runtime")
    subparsers.add_parser("verify-runtime")

    args = parser.parse_args()
    result: tuple[SchemaVersion, ...]
    if args.command == "bootstrap-postgres":
        result = (bootstrap_postgres_schema(postgres_dsn=_load_postgres_dsn(args.postgres_dsn)),)
    elif args.command == "verify-postgres":
        result = (verify_postgres_schema(postgres_dsn=_load_postgres_dsn(args.postgres_dsn)),)
    elif args.command == "bootstrap-clickhouse":
        result = (bootstrap_clickhouse_schema(settings=_load_clickhouse_settings(args)),)
    elif args.command == "verify-clickhouse":
        result = (verify_clickhouse_schema(settings=_load_clickhouse_settings(args)),)
    elif args.command == "bootstrap-runtime":
        result = bootstrap_api_runtime_schema(load_api_settings())
    else:
        settings = load_api_settings()
        if settings.postgres_dsn is None:
            raise RuntimeError("Postgres runtime requires DB_MONITOR_POSTGRES_DSN.")
        result = verify_api_runtime_schema(
            analytics_repository=None,
            clickhouse=settings.clickhouse,
            postgres_dsn=settings.postgres_dsn,
        )
    print(json.dumps({"schemas": [asdict(item) for item in result]}))
    return 0


def _add_clickhouse_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--database")
    parser.add_argument("--endpoint")
    parser.add_argument("--password")
    parser.add_argument("--username")


def _load_clickhouse_settings(args: argparse.Namespace) -> ClickHouseSettings:
    return ClickHouseSettings(
        database=args.database or _required_env("DB_MONITOR_CLICKHOUSE_DATABASE"),
        endpoint=args.endpoint or _required_env("DB_MONITOR_CLICKHOUSE_ENDPOINT"),
        password=args.password or _required_env("DB_MONITOR_CLICKHOUSE_PASSWORD"),
        username=args.username or _required_env("DB_MONITOR_CLICKHOUSE_USERNAME"),
    )


def _load_postgres_dsn(explicit_value: str | None) -> str:
    return explicit_value or _required_env("DB_MONITOR_POSTGRES_DSN")


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
