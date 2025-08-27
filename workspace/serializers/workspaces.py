from rest_framework import serializers
from workspace.models import Workspace


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
    class Meta:
        model = Workspace
        fields = ["name"]
