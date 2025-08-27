import uuid
from django.db import models


class PermissionScope(models.TextChoices):
    OWN = "own", "Own"
    ALL = "all", "All"


class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        "workspace.WorkspaceRole", on_delete=models.CASCADE, related_name="permissions"
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
        "workspace.WorkspaceMembership",
        on_delete=models.CASCADE,
        related_name="overrides",
    )
    code = models.CharField(max_length=100)
    scope = models.CharField(
        max_length=5, choices=PermissionScope.choices, default=PermissionScope.OWN
    )
    allow = models.BooleanField(default=True)

    class Meta:
        unique_together = ("membership", "code")
