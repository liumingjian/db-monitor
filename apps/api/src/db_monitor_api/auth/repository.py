from collections.abc import Sequence
from dataclasses import replace
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


class UserRepository(Protocol):
    def get_by_id(self, user_id: str) -> UserRecord | None:
        ...

    def get_by_username(self, username: str) -> UserRecord | None:
        ...

    def list_by_organization(self, *, organization_id: str) -> tuple[UserRecord, ...]:
        ...

    def update_roles(
        self,
        *,
        organization_id: str,
        roles: frozenset[str],
        user_id: str,
    ) -> UserRecord | None:
        ...


class SessionRepository(Protocol):
    def create(self, session: Session) -> None:
        ...

    def delete(self, session_id: str) -> Session | None:
        ...

    def get(self, session_id: str) -> Session | None:
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

    def list_by_organization(self, *, organization_id: str) -> tuple[UserRecord, ...]:
        return tuple(
            sorted(
                (
                    user
                    for user in self._by_id.values()
                    if any(
                        membership.organization.organization_id == organization_id
                        for membership in user.user.organization_memberships
                    )
                ),
                key=lambda user: (user.user.display_name, user.user.username),
            )
        )

    def update_roles(
        self,
        *,
        organization_id: str,
        roles: frozenset[str],
        user_id: str,
    ) -> UserRecord | None:
        user_record = self._by_id.get(user_id)
        if user_record is None:
            return None
        memberships = []
        updated = False
        for membership in user_record.user.organization_memberships:
            if membership.organization.organization_id == organization_id:
                memberships.append(replace(membership, roles=roles))
                updated = True
                continue
            memberships.append(membership)
        if not updated:
            return None
        next_user = replace(
            user_record.user,
            organization_memberships=tuple(memberships),
            roles=roles
            if user_record.user.active_organization_id == organization_id
            else user_record.user.roles,
        )
        next_record = replace(user_record, user=next_user)
        self._by_id[user_id] = next_record
        self._by_username[next_user.username] = next_record
        return next_record


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
