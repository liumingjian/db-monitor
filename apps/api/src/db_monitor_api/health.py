from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import psycopg


@dataclass(frozen=True)
class DependencyStatus:
    detail: str
    name: str
    ready: bool


class DependencyCheck(Protocol):
    def check(self) -> DependencyStatus:
        ...


@dataclass(frozen=True)
class ReadinessSnapshot:
    dependencies: tuple[DependencyStatus, ...]

    @property
    def ready(self) -> bool:
        return all(dependency.ready for dependency in self.dependencies)


@dataclass(frozen=True)
class ReadinessProbe:
    checks: tuple[DependencyCheck, ...]

    def snapshot(self) -> ReadinessSnapshot:
        return ReadinessSnapshot(
            dependencies=tuple(check.check() for check in self.checks),
        )


@dataclass(frozen=True)
class StaticDependencyCheck:
    detail: str
    name: str

    def check(self) -> DependencyStatus:
        return DependencyStatus(detail=self.detail, name=self.name, ready=True)


@dataclass(frozen=True)
class PostgresDependencyCheck:
    postgres_dsn: str
    name: str = "postgres"

    def check(self) -> DependencyStatus:
        try:
            with psycopg.connect(self.postgres_dsn) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
        except psycopg.Error as error:
            return DependencyStatus(detail=str(error), name=self.name, ready=False)
        return DependencyStatus(detail="SELECT 1 ok", name=self.name, ready=True)


@dataclass(frozen=True)
class ClickHouseDependencyCheck:
    database: str
    endpoint: str
    password: str
    username: str
    name: str = "clickhouse"

    def check(self) -> DependencyStatus:
        request = Request(
            url=(
                self.endpoint.rstrip("/")
                + "/?"
                + urlencode({"database": self.database, "query": "SELECT 1 FORMAT JSONEachRow"})
            ),
            data=b"",
            headers={
                "X-ClickHouse-Key": self.password,
                "X-ClickHouse-User": self.username,
            },
            method="POST",
        )
        try:
            with urlopen(request) as response:
                response.read()
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            return DependencyStatus(
                detail=f"HTTP {error.code}: {detail}",
                name=self.name,
                ready=False,
            )
        except Exception as error:  # pragma: no cover - urllib exception taxonomy is environment-specific
            return DependencyStatus(detail=str(error), name=self.name, ready=False)
        return DependencyStatus(detail="SELECT 1 ok", name=self.name, ready=True)
