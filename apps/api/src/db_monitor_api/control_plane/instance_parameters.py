"""Access layer for per-instance runtime parameters (ADR-0011 D3).

The `instance_parameters` table is a generic JSONB bag shared by every
slice 1+ runtime parameter (processlist interval, slow query threshold,
future OS/Redis/SNMP knobs). Missing rows and missing keys return `{}`
so collectors can fall back to ADR-defined defaults without silent
fallbacks in hot code paths.
"""

from collections.abc import Mapping
from typing import Any, Protocol, cast
import json

import psycopg

_SELECT_PARAMETERS_SQL = (
    "SELECT parameters FROM instance_parameters WHERE instance_id = %s"
)


class InstanceParameterRepository(Protocol):
    def get_parameters(self, instance_id: str) -> Mapping[str, Any]:
        ...


class InMemoryInstanceParameterRepository:
    def __init__(
        self,
        *,
        parameters_by_instance: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> None:
        self._parameters: dict[str, dict[str, Any]] = {
            instance_id: dict(parameters)
            for instance_id, parameters in (parameters_by_instance or {}).items()
        }

    def get_parameters(self, instance_id: str) -> Mapping[str, Any]:
        return dict(self._parameters.get(instance_id, {}))

    def set_parameters(self, instance_id: str, parameters: Mapping[str, Any]) -> None:
        self._parameters[instance_id] = dict(parameters)


class PostgresInstanceParameterRepository:
    def __init__(self, *, postgres_dsn: str) -> None:
        self._postgres_dsn = postgres_dsn

    def get_parameters(self, instance_id: str) -> Mapping[str, Any]:
        with psycopg.connect(self._postgres_dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(_SELECT_PARAMETERS_SQL, (instance_id,))
                row = cursor.fetchone()
        if row is None:
            return {}
        raw = row[0]
        if raw is None:
            return {}
        if isinstance(raw, (dict, Mapping)):
            return cast(Mapping[str, Any], raw)
        return cast(Mapping[str, Any], json.loads(str(raw)))
