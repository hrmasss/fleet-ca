from typing import Dict
from workspace.models.permission import PermissionScope
from .types import PermissionCode as PC

PERMS: Dict[PC, PermissionScope] = {
    PC.WORKSPACE_USERS_VIEW: PermissionScope.ALL,
    PC.WORKSPACE_USERS_CHANGE: PermissionScope.ALL,
    PC.ROLES_VIEW: PermissionScope.ALL,
    PC.ROLES_CHANGE: PermissionScope.ALL,
    PC.SUBSCRIPTION_VIEW: PermissionScope.ALL,
    PC.SUBSCRIPTION_CHANGE: PermissionScope.ALL,
    PC.INVITES_VIEW: PermissionScope.ALL,
    PC.INVITES_CHANGE: PermissionScope.ALL,
    PC.ORGANIZATION_VIEW: PermissionScope.ALL,
    PC.ORGANIZATION_CHANGE: PermissionScope.ALL,
}
