from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from workspace.models import User


class WorkspaceSubscriptionSnapshotSerializer(serializers.Serializer):
    plan = serializers.CharField()
    pending_plan = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    limits = serializers.DictField(child=serializers.IntegerField(), allow_empty=True)


class UserWorkspaceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    subscription = WorkspaceSubscriptionSnapshotSerializer(allow_null=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data (read-only)."""

    full_name = serializers.SerializerMethodField()
    groups = serializers.StringRelatedField(many=True, read_only=True)
    permissions = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    workspaces = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "groups",
            "permissions",
            "workspaces",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "groups",
            "permissions",
            "workspaces",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_permissions(self, obj):
        # Return standard Django permission strings (app_label.codename)
        return sorted(list(obj.get_all_permissions()))

    def get_email(self, obj):
        return obj.email or None

    @extend_schema_field(UserWorkspaceSerializer(many=True))
    def get_workspaces(self, obj):
        memberships = obj.memberships.select_related("workspace").all()
        items = []
        for m in memberships:
            ws = m.workspace
            sub = getattr(ws, "subscription", None)
            snapshot = None
            if sub:
                snapshot = {
                    "plan": sub.plan,
                    "pending_plan": sub.pending_plan,
                    "status": sub.status,
                    "limits": sub.limits,
                }
            items.append({"id": ws.id, "name": ws.name, "subscription": snapshot})
        return UserWorkspaceSerializer(items, many=True).data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (limited fields)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name"]
