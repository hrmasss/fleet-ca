from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from workspace.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data (read-only)."""

    full_name = serializers.SerializerMethodField()
    groups = serializers.StringRelatedField(many=True, read_only=True)
    permissions = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "groups",
            "permissions",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "groups",
            "permissions",
        ]

    @extend_schema_field(
        {
            "type": "string",
            "format": "email",
            "nullable": True,
            "title": "Email address",
        }
    )
    def get_email(self, obj):
        return obj.email or None

    @extend_schema_field(
        {
            "type": "string",
            "description": "User's full name or username in title case if full name is blank",
            "example": "John Doe",
        }
    )
    def get_full_name(self, obj) -> str:
        """Return full name or username in title case if full name is blank."""
        full_name = obj.get_full_name().strip()
        if full_name:
            return full_name
        return obj.username.title()

    @extend_schema_field(
        {
            "type": "array",
            "items": {"type": "string"},
            "description": 'User permissions. "*" indicates all permissions (superuser).',
            "example": ["view_order", "add_order"],
        }
    )
    def get_permissions(self, obj):
        """Return minimal permission indicator.

        For now: '*' if superuser, else empty list. We'll wire RBAC-derived
        permissions later when resource endpoints are added.
        """
        return ["*"] if obj.is_superuser else []


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (limited fields)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name"]
