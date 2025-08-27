from rest_framework import serializers
from workspace.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "id",
            "workspace",
            "plan",
            "status",
            "current_period_end",
            "limits",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "workspace", "created_at", "updated_at"]
