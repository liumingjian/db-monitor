from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from db_monitor_api.auth.domain import (
    AuditEntry,
    OrganizationMembership,
    PasswordDigest,
    Session,
    User,
    UserRecord,
)


class PasswordHasherLike(Protocol):
    def hash_password(self, password: str) -> PasswordDigest:
        ...


class AuditRepository(Protocol):
    @property
    def entries(self) -> Sequence[AuditEntry]:
        ...

    def append(self, entry: AuditEntry) -> None:
        ...

    def list_entries(
        self,
        *,
        descending: bool = False,
        limit: int | None = None,
        organization_id: str | None = None,
    ) -> tuple[AuditEntry, ...]:
        ...


@dataclass(frozen=True)
class SeedUser:
    active_organization_id: str
    user_id: str
    username: str
    password: str
    display_name: str
    organization_memberships: tuple[OrganizationMembership, ...]
    roles: frozenset[str]


class InMemoryUserRepository:
    def __init__(self, users: Sequence[UserRecord]) -> None:
        self._by_id = {user.user.user_id: user for user in users}
        self._by_username = {user.user.username: user for user in users}

    @classmethod
    def from_seed_users(
        cls,
        *,
        password_hasher: PasswordHasherLike,
        seed_users: Sequence[SeedUser],
    ) -> "InMemoryUserRepository":
        return cls(
            users=[
                UserRecord(
                    password_digest=password_hasher.hash_password(seed_user.password),
                    user=User(
                        active_organization_id=seed_user.active_organization_id,
                        user_id=seed_user.user_id,
                        username=seed_user.username,
                        display_name=seed_user.display_name,
                        organization_memberships=seed_user.organization_memberships,
                        roles=seed_user.roles,
                    ),
                )
                for seed_user in seed_users
            ]
        )

    def get_by_id(self, user_id: str) -> UserRecord | None:
        return self._by_id.get(user_id)

    def get_by_username(self, username: str) -> UserRecord | None:
        return self._by_username.get(username)


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, session: Session) -> None:
        self._sessions[session.session_id] = session

    def delete(self, session_id: str) -> Session | None:
        return self._sessions.pop(session_id, None)

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)

    def append(self, entry: AuditEntry) -> None:
        self._entries.append(entry)

    def list_entries(
        self,
        *,
        descending: bool = False,
        limit: int | None = None,
        organization_id: str | None = None,
    ) -> tuple[AuditEntry, ...]:
        entries = [
            entry
            for entry in self._entries
            if organization_id is None or entry.organization_id == organization_id
        ]
        if descending:
            entries.reverse()
        if limit is not None:
            entries = entries[:limit]
        return tuple(entries)
