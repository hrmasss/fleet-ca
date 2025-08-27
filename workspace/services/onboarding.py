from django.db import transaction
from django.conf import settings
from workspace.models import Workspace, WorkspaceMembership, Subscription
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
        status="active" if settings.DEBUG else "trial",
        limits={},
    )
    return ws
