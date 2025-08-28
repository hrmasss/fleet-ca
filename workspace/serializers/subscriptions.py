from rest_framework import serializers
from workspace.models import Subscription
from workspace.config.types import SubscriptionInterval


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "id",
            "workspace",
            "plan",
            "status",
            "pending_plan",
            "current_period_end",
            "limits",
            "renew_interval",
            "auto_renew",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "workspace",
            "plan",
            "status",
            "current_period_end",
            "limits",
            "created_at",
            "updated_at",
        ]


class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    renew_interval = serializers.ChoiceField(
        choices=[e.value for e in SubscriptionInterval], required=False
    )
    auto_renew = serializers.BooleanField(required=False)

    class Meta:
        model = Subscription
        fields = ["pending_plan", "renew_interval", "auto_renew"]
