"""Default seed users for in-memory auth repositories.

Moved out of `bootstrap.py` to keep that file below the 300 line limit
after wiring additional runtime services.
"""

from db_monitor_api.auth.domain import Organization, OrganizationMembership
from db_monitor_api.auth.repository import SeedUser


def default_seed_users() -> tuple[SeedUser, ...]:
    default_organization = Organization(
        organization_id="org-internal",
        name="Internal Operations",
        slug="internal-ops",
    )
    return (
        SeedUser(
            active_organization_id=default_organization.organization_id,
            user_id="user-admin",
            username="admin",
            password="admin-password",
            display_name="Platform Admin",
            organization_memberships=(
                OrganizationMembership(
                    organization=default_organization,
                    roles=frozenset({"admin"}),
                ),
            ),
            roles=frozenset({"admin"}),
        ),
        SeedUser(
            active_organization_id=default_organization.organization_id,
            user_id="user-ops",
            username="operator",
            password="operator-password",
            display_name="Operations Engineer",
            organization_memberships=(
                OrganizationMembership(
                    organization=default_organization,
                    roles=frozenset({"operator"}),
                ),
            ),
            roles=frozenset({"operator"}),
        ),
        SeedUser(
            active_organization_id=default_organization.organization_id,
            user_id="user-viewer",
            username="viewer",
            password="viewer-password",
            display_name="Read Only User",
            organization_memberships=(
                OrganizationMembership(
                    organization=default_organization,
                    roles=frozenset({"viewer"}),
                ),
            ),
            roles=frozenset({"viewer"}),
        ),
    )
