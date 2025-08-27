from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from workspace.models import User


class WorkspaceSubscriptionSnapshotSerializer(serializers.Serializer):
    plan = serializers.CharField()
    pending_plan = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    limits = serializers.DictField(child=serializers.IntegerField(), allow_empty=True)


class WorkspaceRoleSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    is_system = serializers.BooleanField()


class PermissionItemSerializer(serializers.Serializer):
    code = serializers.CharField()
    scope = serializers.ChoiceField(choices=["own", "all"])


class UserWorkspaceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    subscription = WorkspaceSubscriptionSnapshotSerializer(allow_null=True)
    role = WorkspaceRoleSerializer(allow_null=True)
    permissions = PermissionItemSerializer(many=True)
    organization = serializers.DictField(allow_null=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data (read-only)."""

    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    workspaces = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "workspaces",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "workspaces",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_email(self, obj):
        return obj.email or None

    @extend_schema_field(UserWorkspaceSerializer(many=True))
    def get_workspaces(self, obj):
        memberships = obj.memberships.select_related(
            "workspace",
            "role",
            "workspace__organization",
        ).prefetch_related("role__permissions", "overrides")
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
            # Role
            role = (
                {"id": m.role.id, "name": m.role.name, "is_system": m.role.is_system}
                if m.role
                else None
            )
            # Effective permissions: union of role permissions and allow=True overrides, highest scope wins
            eff: dict[str, str] = {}
            if m.role:
                for rp in m.role.permissions.all():
                    prev = eff.get(rp.code)
                    if prev != "all":
                        eff[rp.code] = rp.scope
            for ov in m.overrides.all():
                if not getattr(ov, "allow", True):
                    continue
                prev = eff.get(ov.code)
                # Promote to "all" if any source grants ALL
                if ov.scope == "all" or prev == "all":
                    eff[ov.code] = "all"
                else:
                    eff.setdefault(ov.code, ov.scope)
            permissions = [
                {"code": code, "scope": scope} for code, scope in sorted(eff.items())
            ]

            org = None
            if getattr(ws, "organization_id", None):
                o = ws.organization
                logo_url = None
                try:
                    if o.logo:
                        logo_url = o.logo.url
                except Exception:
                    logo_url = None
                org = {
                    "id": o.id,
                    "name": o.name,
                    "logo": logo_url,
                    "brand": o.brand,
                }

            items.append(
                {
                    "id": ws.id,
                    "name": ws.name,
                    "subscription": snapshot,
                    "role": role,
                    "permissions": permissions,
                    "organization": org,
                }
            )
        return UserWorkspaceSerializer(items, many=True).data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (limited fields)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name"]
