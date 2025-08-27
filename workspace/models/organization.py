import uuid
from django.db import models
from common.models import TimeStampedModel
from safedelete.models import SafeDeleteModel
from common.fields import OptimizedImageField
from safedelete import SOFT_DELETE_CASCADE


class Organization(SafeDeleteModel, TimeStampedModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    logo = OptimizedImageField(upload_to="org_logos/", null=True, blank=True)
    brand = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.name
