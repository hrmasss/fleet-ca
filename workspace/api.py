from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Workspace, WorkspaceMembership
from .rbac import WorkspaceHeaderResolverMixin
from rest_framework import serializers
from workspace.serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = [
            "id",
            "name",
            "branding_logo",
            "branding_color",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["name", "branding_logo", "branding_color"]


def _seed_default_roles(workspace: Workspace) -> None:
    from .models import WorkspaceRole, RolePermission, PermissionScope

    owner = WorkspaceRole.objects.create(
        workspace=workspace, name="Owner", is_system=True
    )
    all_codes = [
        "content.view",
        "content.change",
        "campaigns.view",
        "campaigns.change",
        "social_accounts.view",
        "social_accounts.change",
        "workspace_users.view",
        "workspace_users.change",
        "roles.view",
        "roles.change",
    ]
    RolePermission.objects.bulk_create(
        [
            RolePermission(role=owner, code=c, scope=PermissionScope.ALL)
            for c in all_codes
        ]
    )

    editor = WorkspaceRole.objects.create(
        workspace=workspace, name="Editor", is_system=True
    )
    editor_codes = [
        ("content.view", PermissionScope.ALL),
        ("content.change", PermissionScope.ALL),
        ("campaigns.view", PermissionScope.ALL),
        ("campaigns.change", PermissionScope.ALL),
        ("published_posts.view", PermissionScope.ALL),
        ("published_posts.change", PermissionScope.ALL),
    ]
    RolePermission.objects.bulk_create(
        [RolePermission(role=editor, code=c, scope=s) for c, s in editor_codes]
    )

    member = WorkspaceRole.objects.create(
        workspace=workspace, name="Member", is_system=True
    )
    member_codes = [
        ("content.view", PermissionScope.ALL),
        ("content.change", PermissionScope.OWN),
        ("campaigns.view", PermissionScope.ALL),
        ("published_posts.view", PermissionScope.ALL),
    ]
    RolePermission.objects.bulk_create(
        [RolePermission(role=member, code=c, scope=s) for c, s in member_codes]
    )


class WorkspaceListCreateView(WorkspaceHeaderResolverMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkspaceSerializer

    @extend_schema(
        operation_id="list_workspaces",
        summary="List my workspaces",
        responses={200: WorkspaceSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        qs = Workspace.objects.filter(
            memberships__user=request.user, memberships__is_active=True
        ).distinct()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        operation_id="create_workspace",
        summary="Create a workspace",
        request=WorkspaceCreateSerializer,
        responses={201: WorkspaceSerializer},
    )
    def post(self, request, *args, **kwargs):
        data_s = WorkspaceCreateSerializer(data=request.data)
        data_s.is_valid(raise_exception=True)
        with transaction.atomic():
            ws = Workspace.objects.create(owner=request.user, **data_s.validated_data)
            _seed_default_roles(ws)
            # Assign membership as Owner
            owner_role = ws.roles.get(name="Owner")
            WorkspaceMembership.objects.create(
                workspace=ws, user=request.user, role=owner_role
            )
        return Response(WorkspaceSerializer(ws).data, status=201)


class TokenObtainPairView(BaseTokenObtainPairView):
    pass


class TokenRefreshView(BaseTokenRefreshView):
    pass


class UserProfileView(generics.RetrieveAPIView):
    """Get current user's profile information."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        operation_id="get_user_profile",
        summary="Get user profile",
        description="Retrieve the current user's profile information including permissions",
        responses={
            200: OpenApiResponse(
                response=UserProfileSerializer, description="User profile data"
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserProfileUpdateView(generics.UpdateAPIView):
    """Update current user's profile (partial update only)."""

    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user

    @extend_schema(
        operation_id="update_user_profile",
        summary="Update user profile",
        description="Update user profile information (name and image only)",
        request=UserProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=UserProfileSerializer, description="Updated user profile data"
            ),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def patch(self, request, *args, **kwargs):
        """Handle profile update and return full profile data."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return full profile data using the read serializer
        profile_serializer = UserProfileSerializer(instance)
        return Response(profile_serializer.data)


class MyMembershipsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    class _MembershipSerializer(serializers.ModelSerializer):
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

    serializer_class = _MembershipSerializer

    @extend_schema(
        operation_id="list_my_memberships",
        summary="List my workspace memberships",
        responses={200: _MembershipSerializer(many=True)},
    )
    def get_queryset(self):
        return WorkspaceMembership.objects.select_related("workspace", "role").filter(
            user=self.request.user
        )
