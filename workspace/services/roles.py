from typing import Dict, Iterable
from workspace.config.registry import get_permissions_registry
from workspace.models import Workspace, WorkspaceRole, RolePermission, PermissionScope
from workspace.config.types import PermissionCode as PC


DEFAULT_ROLE_DEFS: Dict[str, Iterable[tuple[PC, PermissionScope]]] = {
    "Owner": [
        (PC.WORKSPACE_USERS_VIEW, PermissionScope.ALL),
        (PC.WORKSPACE_USERS_CHANGE, PermissionScope.ALL),
        (PC.ROLES_VIEW, PermissionScope.ALL),
        (PC.ROLES_CHANGE, PermissionScope.ALL),
        (PC.SUBSCRIPTION_VIEW, PermissionScope.ALL),
        (PC.SUBSCRIPTION_CHANGE, PermissionScope.ALL),
        (PC.INVITES_VIEW, PermissionScope.ALL),
        (PC.INVITES_CHANGE, PermissionScope.ALL),
        (PC.ORGANIZATION_VIEW, PermissionScope.ALL),
        (PC.ORGANIZATION_CHANGE, PermissionScope.ALL),
    ],
    "Editor": [
        (PC.INVITES_VIEW, PermissionScope.ALL),
        (PC.INVITES_CHANGE, PermissionScope.ALL),
        (PC.ORGANIZATION_VIEW, PermissionScope.ALL),
        (PC.ORGANIZATION_CHANGE, PermissionScope.ALL),
    ],
    "Member": [
        (PC.INVITES_VIEW, PermissionScope.ALL),
        (PC.ORGANIZATION_VIEW, PermissionScope.ALL),
    ],
}


def seed_workspace_roles(
    workspace: Workspace,
    role_defs: Dict[str, Iterable[tuple[PC, PermissionScope]]] | None = None,
) -> None:
    # Validate against centralized registry to avoid typos and keep consistency
    registry = get_permissions_registry()
    defs = role_defs or DEFAULT_ROLE_DEFS
    for role_name, perms in defs.items():
        role = WorkspaceRole.objects.create(
            workspace=workspace, name=role_name, is_system=True
        )
        valid_perms = [(code, scope) for code, scope in perms if code.value in registry]
        RolePermission.objects.bulk_create(
            [
                RolePermission(role=role, code=code.value, scope=scope)
                for code, scope in valid_perms
            ]
        )
