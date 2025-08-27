from workspace.models import PermissionScope
from .types import Resource, Action


def code_with_scope(
    resource: Resource | str, action: Action | str, scope: PermissionScope
) -> str:
    """Return a canonical resource.action.scope string for display/logging."""
    r = resource.value if isinstance(resource, Resource) else resource
    a = action.value if isinstance(action, Action) else action
    return f"{r}.{a}.{scope}"
