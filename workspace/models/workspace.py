import uuid
from django.db import models
from common.models import TimeStampedModel
from workspace.models.organization import Organization
from safedelete.models import SafeDeleteModel
from safedelete import SOFT_DELETE_CASCADE
from django.conf import settings


class Workspace(SafeDeleteModel, TimeStampedModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_workspaces",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workspaces",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"], name="uniq_workspace_name_per_owner"
            )
        ]


class WorkspaceRole(SafeDeleteModel, TimeStampedModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="roles"
    )
    name = models.CharField(max_length=50)
    is_system = models.BooleanField(default=False)

    class Meta:
        unique_together = ("workspace", "name")

    def __str__(self) -> str:
        return f"{self.workspace}:{self.name}"


class WorkspaceMembership(SafeDeleteModel, TimeStampedModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.ForeignKey(
        "workspace.WorkspaceRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("workspace", "user")

    def __str__(self) -> str:
        return f"{self.user} in {self.workspace}"


class WorkspaceInvite(SafeDeleteModel, TimeStampedModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="invites"
    )
    email = models.EmailField()
    role = models.ForeignKey(
        "workspace.WorkspaceRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invites",
    )
    token = models.CharField(max_length=64, unique=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("workspace", "email")
