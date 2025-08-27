from rest_framework import serializers
from workspace.models import Workspace
from workspace.config.plans import PLAN_CHOICES


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = [
            "id",
            "name",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    plan = serializers.ChoiceField(
        choices=PLAN_CHOICES, required=False, allow_null=True
    )

    class Meta:
        model = Workspace
        fields = ["name", "plan"]
