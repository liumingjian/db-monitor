from dataclasses import dataclass
import hashlib
import secrets

from db_monitor_api.auth.domain import (
    AuthContext,
    AuditEntry,
    ManagedUser,
    Organization,
    PasswordDigest,
    Permission,
    RoleCatalogEntry,
    ROLE_PERMISSIONS,
    Session,
    UserRecord,
    utc_now,
)
from db_monitor_api.auth.repository import (
    AuditRepository,
    SessionRepository,
    UserRepository,
)

HASH_ITERATIONS = 120_000
SESSION_COOKIE_NAME = "dbmon_session"


class AuthenticationError(Exception):
    pass


class PermissionDenied(Exception):
    pass


class ManagedUserNotFoundError(Exception):
    pass


class UnknownRoleError(Exception):
    pass


class PasswordHasher:
    def hash_password(self, password: str) -> PasswordDigest:
        salt = secrets.token_hex(16)
        digest = self._build_digest(password=password, salt=salt)
        return PasswordDigest(digest=digest, salt=salt)

    def verify_password(self, *, password: str, stored: PasswordDigest) -> bool:
        actual = self._build_digest(password=password, salt=stored.salt)
        return secrets.compare_digest(actual, stored.digest)

    def _build_digest(self, *, password: str, salt: str) -> str:
        raw_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            HASH_ITERATIONS,
        )
        return raw_digest.hex()


@dataclass(frozen=True)
class AuditService:
    audit_repository: AuditRepository

    def record(
        self,
        *,
        action: str,
        actor_user_id: str,
        organization_id: str,
        outcome: str,
        resource: str,
    ) -> None:
        self.audit_repository.append(
            AuditEntry(
                action=action,
                actor_user_id=actor_user_id,
                occurred_at=utc_now(),
                organization_id=organization_id,
                outcome=outcome,
                resource=resource,
            )
        )

    def list_entries(
        self,
        *,
        limit: int,
        organization_id: str,
    ) -> tuple[AuditEntry, ...]:
        return self.audit_repository.list_entries(
            descending=True,
            limit=limit,
            organization_id=organization_id,
        )


@dataclass(frozen=True)
class AuthService:
    audit_service: AuditService
    password_hasher: PasswordHasher
    session_repository: SessionRepository
    user_repository: UserRepository

    def login(self, *, password: str, username: str) -> AuthContext:
        user_record = self.user_repository.get_by_username(username)
        if user_record is None:
            raise AuthenticationError("Invalid username or password.")
        if not self.password_hasher.verify_password(
            password=password,
            stored=user_record.password_digest,
        ):
            raise AuthenticationError("Invalid username or password.")

        session = Session(
            session_id=secrets.token_urlsafe(24),
            user_id=user_record.user.user_id,
            active_organization_id=user_record.user.active_organization_id,
            created_at=utc_now(),
        )
        self.session_repository.create(session)
        self.audit_service.record(
            action="auth.login",
            actor_user_id=user_record.user.user_id,
            organization_id=user_record.user.active_organization_id,
            outcome="allowed",
            resource="session",
        )
        return _build_auth_context(session=session, user_record=user_record)

    def logout(self, *, session_id: str) -> None:
        session = self.session_repository.delete(session_id)
        if session is None:
            raise AuthenticationError("Session is not active.")
        self.audit_service.record(
            action="auth.logout",
            actor_user_id=session.user_id,
            organization_id=session.active_organization_id,
            outcome="allowed",
            resource="session",
        )

    def require_session(self, *, session_id: str) -> AuthContext:
        session = self.session_repository.get(session_id)
        if session is None:
            raise AuthenticationError("Session is not active.")

        user_record = self.user_repository.get_by_id(session.user_id)
        if user_record is None:
            raise AuthenticationError("User is not available for the active session.")
        return _build_auth_context(session=session, user_record=user_record)

    def list_managed_users(self, *, organization_id: str) -> tuple[ManagedUser, ...]:
        return tuple(
            _build_managed_user(user_record=user_record, organization_id=organization_id)
            for user_record in self.user_repository.list_by_organization(
                organization_id=organization_id
            )
        )

    def list_role_catalog(self) -> tuple[RoleCatalogEntry, ...]:
        return tuple(
            RoleCatalogEntry(
                permissions=_permissions_for_roles(frozenset({role})),
                role=role,
            )
            for role in sorted(ROLE_PERMISSIONS)
        )

    def update_user_roles(
        self,
        *,
        actor_user_id: str,
        organization_id: str,
        roles: frozenset[str],
        target_user_id: str,
    ) -> ManagedUser:
        _require_known_roles(roles)
        user_record = self.user_repository.update_roles(
            organization_id=organization_id,
            roles=roles,
            user_id=target_user_id,
        )
        if user_record is None:
            raise ManagedUserNotFoundError(f"Unknown user: {target_user_id}")
        self.audit_service.record(
            action="users.roles.update",
            actor_user_id=actor_user_id,
            organization_id=organization_id,
            outcome="allowed",
            resource=f"user:{target_user_id}",
        )
        return _build_managed_user(
            user_record=user_record,
            organization_id=organization_id,
        )


@dataclass(frozen=True)
class AuthorizationService:
    audit_service: AuditService

    def require_permission(
        self,
        *,
        context: AuthContext,
        permission: Permission,
        resource: str,
    ) -> None:
        if permission in context.permissions:
            return
        self.audit_service.record(
            action=f"{resource}.denied",
            actor_user_id=context.user.user_id,
            organization_id=context.active_organization.organization_id,
            outcome="denied",
            resource=resource,
        )
        raise PermissionDenied(f"Missing permission: {permission.value}")


def _build_auth_context(*, session: Session, user_record: UserRecord) -> AuthContext:
    return AuthContext(
        active_organization=_require_active_organization(
            active_organization_id=session.active_organization_id,
            user_record=user_record,
        ),
        permissions=_permissions_for_roles(user_record.user.roles),
        session=session,
        user=user_record.user,
    )


def _permissions_for_roles(roles: frozenset[str]) -> frozenset[Permission]:
    permissions: set[Permission] = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, frozenset()))
    return frozenset(permissions)


def _build_managed_user(
    *,
    organization_id: str,
    user_record: UserRecord,
) -> ManagedUser:
    roles = _require_membership_roles(
        organization_id=organization_id,
        user_record=user_record,
    )
    return ManagedUser(
        active_organization_id=user_record.user.active_organization_id,
        display_name=user_record.user.display_name,
        effective_permissions=_permissions_for_roles(roles),
        roles=roles,
        user_id=user_record.user.user_id,
        username=user_record.user.username,
    )


def _require_known_roles(roles: frozenset[str]) -> None:
    unknown_roles = sorted(role for role in roles if role not in ROLE_PERMISSIONS)
    if unknown_roles:
        raise UnknownRoleError(
            f"Unknown roles: {', '.join(unknown_roles)}"
        )


def _require_active_organization(
    *,
    active_organization_id: str,
    user_record: UserRecord,
) -> Organization:
    for membership in user_record.user.organization_memberships:
        if membership.organization.organization_id == active_organization_id:
            return membership.organization
    raise AuthenticationError("User is not available for the active organization session.")


def _require_membership_roles(
    *,
    organization_id: str,
    user_record: UserRecord,
) -> frozenset[str]:
    for membership in user_record.user.organization_memberships:
        if membership.organization.organization_id == organization_id:
            return membership.roles
    raise ManagedUserNotFoundError(f"Unknown user organization scope: {user_record.user.user_id}")
