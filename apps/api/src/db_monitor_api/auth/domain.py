from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class Permission(StrEnum):
    INSTANCES_READ = "instances:read"
    INSTANCES_WRITE = "instances:write"
    RULES_READ = "rules:read"
    RULES_WRITE = "rules:write"
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
    INSTANCES_ACTION = "instances:action"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "admin": frozenset(permission for permission in Permission),
    "operator": frozenset(
        {
            Permission.INSTANCES_READ,
            Permission.INSTANCES_WRITE,
            Permission.INSTANCES_ACTION,
            Permission.RULES_READ,
            Permission.RULES_WRITE,
            Permission.SETTINGS_READ,
        }
    ),
    "viewer": frozenset(
        {
            Permission.INSTANCES_READ,
            Permission.RULES_READ,
            Permission.SETTINGS_READ,
        }
    ),
}


@dataclass(frozen=True)
class PasswordDigest:
    digest: str
    salt: str


@dataclass(frozen=True)
class User:
    active_organization_id: str
    user_id: str
    username: str
    display_name: str
    organization_memberships: tuple["OrganizationMembership", ...]
    roles: frozenset[str]


@dataclass(frozen=True)
class UserRecord:
    password_digest: PasswordDigest
    user: User


@dataclass(frozen=True)
class Organization:
    organization_id: str
    name: str
    slug: str


@dataclass(frozen=True)
class OrganizationMembership:
    organization: Organization
    roles: frozenset[str]


@dataclass(frozen=True)
class Session:
    session_id: str
    user_id: str
    active_organization_id: str
    created_at: datetime


@dataclass(frozen=True)
class AuditEntry:
    action: str
    actor_user_id: str
    occurred_at: datetime
    organization_id: str
    outcome: str
    resource: str


@dataclass(frozen=True)
class AuthContext:
    active_organization: Organization
    permissions: frozenset[Permission]
    session: Session
    user: User


@dataclass(frozen=True)
class ManagedUser:
    active_organization_id: str
    display_name: str
    effective_permissions: frozenset[Permission]
    roles: frozenset[str]
    user_id: str
    username: str


@dataclass(frozen=True)
class RoleCatalogEntry:
    permissions: frozenset[Permission]
    role: str


def utc_now() -> datetime:
    return datetime.now(tz=UTC)
