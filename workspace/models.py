import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models import TimeStampedModel
from django.conf import settings


class User(AbstractUser):
    pass


class Workspace(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_workspaces",
    )

    def __str__(self) -> str:
        return self.name


class WorkspaceRole(TimeStampedModel):
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


class WorkspaceMembership(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.ForeignKey(
        WorkspaceRole,
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


class PermissionScope(models.TextChoices):
    OWN = "own", "Own"
    ALL = "all", "All"


class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        WorkspaceRole, on_delete=models.CASCADE, related_name="permissions"
    )
    code = models.CharField(max_length=100)
    scope = models.CharField(
        max_length=5, choices=PermissionScope.choices, default=PermissionScope.OWN
    )

    class Meta:
        unique_together = ("role", "code")


class UserPermissionOverride(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    membership = models.ForeignKey(
        WorkspaceMembership, on_delete=models.CASCADE, related_name="overrides"
    )
    code = models.CharField(max_length=100)
    scope = models.CharField(
        max_length=5, choices=PermissionScope.choices, default=PermissionScope.OWN
    )
    allow = models.BooleanField(default=True)

    class Meta:
        unique_together = ("membership", "code")


class Subscription(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.OneToOneField(
        Workspace, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.CharField(max_length=50, default="free")
    status = models.CharField(max_length=20, default="active")
    current_period_end = models.DateTimeField(null=True, blank=True)
    limits = models.JSONField(default=dict, blank=True)
