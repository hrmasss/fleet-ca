from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base with timezone-aware timestamps."""

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
