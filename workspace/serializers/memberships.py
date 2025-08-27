from rest_framework import serializers
from workspace.models import WorkspaceMembership


class MembershipSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", allow_null=True)
    workspace_name = serializers.CharField(source="workspace.name")

    class Meta:
        model = WorkspaceMembership
        fields = [
            "id",
            "workspace",
            "workspace_name",
            "role",
            "is_active",
            "created_at",
        ]
