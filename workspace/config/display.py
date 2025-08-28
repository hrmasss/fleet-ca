from typing import Dict
from workspace.models.permission import PermissionScope
from .types import PermissionCode as PC, Action


HUMAN_LABELS: Dict[PC, str] = {
    PC.WORKSPACE_USERS_VIEW: "View workspace members",
    PC.WORKSPACE_USERS_CHANGE: "Manage workspace members",
    PC.ROLES_VIEW: "View roles",
    PC.ROLES_CHANGE: "Manage roles",
    PC.SUBSCRIPTION_VIEW: "View subscription",
    PC.SUBSCRIPTION_CHANGE: "Manage subscription",
    PC.INVITES_VIEW: "View invites",
    PC.INVITES_CHANGE: "Manage invites",
    PC.ORGANIZATION_VIEW: "View organization",
    PC.ORGANIZATION_CHANGE: "Manage organization",
}


SCOPE_LABELS: Dict[PermissionScope, str] = {
    PermissionScope.OWN: "own",
    PermissionScope.ALL: "all",
}


def permission_display(code: PC, scope: PermissionScope) -> str:
    base = HUMAN_LABELS.get(code, code.value)
    scope_label = SCOPE_LABELS.get(scope, str(scope))
    # Example outputs: "Change content (own)", "Manage invites (all)"
    if code.name.endswith(Action.CHANGE.name):
        return f"{base} ({scope_label})"
    return base
