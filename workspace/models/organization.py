import uuid
from django.db import models
from django.conf import settings
from common.models import TimeStampedModel
from safedelete.models import SafeDeleteModel
from common.fields import OptimizedImageField
from safedelete import SOFT_DELETE_CASCADE


class Organization(SafeDeleteModel, TimeStampedModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizations",
    )
    name = models.CharField(max_length=200)
    logo = OptimizedImageField(upload_to="org_logos/", null=True, blank=True)
    brand = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"], name="uniq_org_name_per_owner"
            )
        ]
