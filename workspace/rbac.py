from typing import Optional
from .models import Workspace, WorkspaceMembership, PermissionScope
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.http import HttpRequest
from dataclasses import dataclass


def permission_code(resource: str, action: str) -> str:
    return f"{resource}.{action}"


def resolve_action(method: str) -> str:
    return "view" if method in SAFE_METHODS else "change"


@dataclass
class PermissionContext:
    membership: WorkspaceMembership
    has_all: bool
    has_own: bool


def _membership_for(user, workspace: Workspace) -> Optional[WorkspaceMembership]:
    try:
        return WorkspaceMembership.objects.select_related("role").get(
            workspace=workspace, user=user, is_active=True
        )
    except WorkspaceMembership.DoesNotExist:
        return None


def has_workspace_permission(
    user,
    workspace: Workspace,
    resource: str,
    action: str,
    owner_id: Optional[int | str] = None,
) -> bool:
    if user.is_superuser:
        return True
    membership = _membership_for(user, workspace)
    if not membership:
        return False
    code = permission_code(resource, action)

    # Role grants
    role_perms = (
        membership.role.permissions.filter(code=code) if membership.role else []
    )
    has_all = any(p.scope == PermissionScope.ALL for p in role_perms)
    has_own = any(p.scope == PermissionScope.OWN for p in role_perms)

    # Overrides (allow = True only)
    overrides = membership.overrides.filter(code=code, allow=True)
    has_all = has_all or any(o.scope == PermissionScope.ALL for o in overrides)
    has_own = has_own or any(o.scope == PermissionScope.OWN for o in overrides)

    if has_all:
        return True
    if has_own and owner_id is not None:
        return str(owner_id) == str(user.id)
    return False


class WorkspaceHeaderResolverMixin:
    """Mixin to resolve workspace from header or url kwarg `workspace_id`."""

    workspace_kwarg = "workspace_id"

    def get_workspace(self, request: HttpRequest) -> Optional[Workspace]:
        ws_id = request.headers.get("X-Workspace-ID") or request.query_params.get(
            "workspace_id"
        )
        if not ws_id and hasattr(self, "kwargs"):
            ws_id = self.kwargs.get(self.workspace_kwarg)
        if not ws_id:
            return None
        try:
            return Workspace.objects.get(pk=ws_id)
        except Workspace.DoesNotExist:
            return None


class WorkspaceRBACPermission(BasePermission):
    """DRF permission that enforces workspace membership and resource/action checks.

    Set view attributes: `resource = "content"` and optionally `action` (for custom actions).
    Otherwise action is inferred from the method.
    """

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(view, "public", False):
            return True
        workspace = getattr(request, "workspace", None)
        if workspace is None and hasattr(view, "get_workspace"):
            workspace = view.get_workspace(request)
            setattr(request, "workspace", workspace)
        if workspace is None:
            return False
        resource = getattr(view, "resource", None)
        if not resource:
            # If view doesn't declare resource, only membership is required
            return _membership_for(request.user, workspace) is not None
        action = getattr(view, "action_code", None) or resolve_action(request.method)
        return has_workspace_permission(request.user, workspace, resource, action)

    def has_object_permission(self, request, view, obj) -> bool:
        workspace = getattr(request, "workspace", None)
        resource = getattr(view, "resource", None)
        if not resource:
            return True
        action = getattr(view, "action_code", None) or resolve_action(request.method)
        owner_id = getattr(obj, "created_by_id", None)
        return has_workspace_permission(
            request.user, workspace, resource, action, owner_id=owner_id
        )
