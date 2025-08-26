from typing import Dict, Iterable, Tuple
from .models import Workspace, WorkspaceRole, RolePermission, PermissionScope


DEFAULT_ROLE_DEFS: Dict[str, Iterable[Tuple[str, PermissionScope]]] = {
    "Owner": [
        ("content.view", PermissionScope.ALL),
        ("content.change", PermissionScope.ALL),
        ("campaigns.view", PermissionScope.ALL),
        ("campaigns.change", PermissionScope.ALL),
        ("social_accounts.view", PermissionScope.ALL),
        ("social_accounts.change", PermissionScope.ALL),
        ("workspace_users.view", PermissionScope.ALL),
        ("workspace_users.change", PermissionScope.ALL),
        ("roles.view", PermissionScope.ALL),
        ("roles.change", PermissionScope.ALL),
        ("subscription.view", PermissionScope.ALL),
        ("subscription.change", PermissionScope.ALL),
    ],
    "Editor": [
        ("content.view", PermissionScope.ALL),
        ("content.change", PermissionScope.ALL),
        ("campaigns.view", PermissionScope.ALL),
        ("campaigns.change", PermissionScope.ALL),
        ("published_posts.view", PermissionScope.ALL),
        ("published_posts.change", PermissionScope.ALL),
    ],
    "Member": [
        ("content.view", PermissionScope.ALL),
        ("content.change", PermissionScope.OWN),
        ("campaigns.view", PermissionScope.ALL),
        ("published_posts.view", PermissionScope.ALL),
    ],
}


def seed_workspace_roles(
    workspace: Workspace,
    role_defs: Dict[str, Iterable[Tuple[str, PermissionScope]]] | None = None,
) -> None:
    """Seed workspace with default roles and permissions from a simple mapping."""
    defs = role_defs or DEFAULT_ROLE_DEFS
    for role_name, perms in defs.items():
        role = WorkspaceRole.objects.create(
            workspace=workspace, name=role_name, is_system=True
        )
        RolePermission.objects.bulk_create(
            [RolePermission(role=role, code=code, scope=scope) for code, scope in perms]
        )
