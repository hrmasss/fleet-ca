from django.db import transaction
from workspace.models import Workspace, WorkspaceMembership, Subscription
from workspace.config.plans import limits_for
from .roles import seed_workspace_roles


@transaction.atomic
def create_workspace_with_defaults(owner, name: str) -> Workspace:
    ws = Workspace.objects.create(owner=owner, name=name)
    seed_workspace_roles(ws)
    owner_role = ws.roles.get(name="Owner")
    WorkspaceMembership.objects.create(workspace=ws, user=owner, role=owner_role)
    Subscription.objects.create(
        workspace=ws,
        plan="free",
        status="trial",
        limits=limits_for("free"),
    )
    return ws


@transaction.atomic
def choose_plan(workspace: Workspace, plan: str) -> Subscription:
    """Set a pending plan. Actual plan remains until payment confirmation.
    Payment gateway integration can call confirm_plan() on success.
    """
    sub, _ = Subscription.objects.get_or_create(workspace=workspace)
    sub.pending_plan = plan
    sub.save(update_fields=["pending_plan"])
    return sub


@transaction.atomic
def confirm_plan(workspace: Workspace) -> Subscription:
    """Confirm pending plan after payment. Copies pending_plan to plan and updates limits."""
    sub = workspace.subscription
    if sub.pending_plan:
        sub.plan = sub.pending_plan
        sub.pending_plan = None
        sub.status = "active"
        sub.limits = limits_for(sub.plan)
        sub.save(update_fields=["plan", "pending_plan", "status", "limits"])
    return sub
