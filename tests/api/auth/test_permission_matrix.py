"""ADR-0006 / ADR-0011 D2: runtime action permission matrix.

`Permission.INSTANCES_ACTION` is a new permission that gates runtime
commands (e.g. `instances.process.kill`). It must be held by `admin` and
`operator` roles and must never be inherited by `viewer`. Kill endpoints
will not accept `INSTANCES_WRITE` as a substitute (ADR-0006 forbids
reusing WRITE for runtime side-effects).
"""

from db_monitor_api.auth.domain import Permission, ROLE_PERMISSIONS


def test_instances_action_permission_is_registered() -> None:
    assert Permission.INSTANCES_ACTION.value == "instances:action"


def test_admin_role_holds_instances_action_permission() -> None:
    assert Permission.INSTANCES_ACTION in ROLE_PERMISSIONS["admin"]


def test_operator_role_holds_instances_action_permission() -> None:
    assert Permission.INSTANCES_ACTION in ROLE_PERMISSIONS["operator"]


def test_viewer_role_does_not_hold_instances_action_permission() -> None:
    assert Permission.INSTANCES_ACTION not in ROLE_PERMISSIONS["viewer"]


def test_instances_action_is_distinct_from_instances_write() -> None:
    action: Permission = Permission.INSTANCES_ACTION
    write: Permission = Permission.INSTANCES_WRITE
    assert action is not write
    assert action.value != write.value


def test_role_permissions_catalog_contains_all_known_roles() -> None:
    assert set(ROLE_PERMISSIONS) == {"admin", "operator", "viewer"}
