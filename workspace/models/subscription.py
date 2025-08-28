import uuid
from django.db import models
from common.models import TimeStampedModel
from safedelete.models import SafeDeleteModel
from safedelete import SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
from workspace.config.types import SubscriptionInterval


class Subscription(SafeDeleteModel, TimeStampedModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.OneToOneField(
        "workspace.Workspace", on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.CharField(max_length=50, default="free")
    pending_plan = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, default="active")
    current_period_end = models.DateTimeField(null=True, blank=True)
    limits = models.JSONField(default=dict, blank=True)
    renew_interval = models.CharField(
        max_length=10,
        choices=[(e.value, e.value) for e in SubscriptionInterval],
        default=SubscriptionInterval.MONTHLY.value,
    )
    auto_renew = models.BooleanField(default=True)
    history = HistoricalRecords()
