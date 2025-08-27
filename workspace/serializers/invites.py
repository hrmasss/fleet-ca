from rest_framework import serializers
from workspace.models import WorkspaceInvite, WorkspaceRole


class InviteCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_role_id(self, value):
        if value is None:
            return value
        try:
            return WorkspaceRole.objects.get(pk=value)
        except WorkspaceRole.DoesNotExist:
            raise serializers.ValidationError("Invalid role")


class InviteSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", allow_null=True)

    class Meta:
        model = WorkspaceInvite
        fields = ["id", "email", "role", "token", "accepted", "created_at"]
        read_only_fields = ["id", "token", "accepted", "created_at"]


class InviteAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
