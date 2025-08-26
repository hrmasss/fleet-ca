from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Workspace, WorkspaceMembership, Subscription
from .role_defaults import seed_workspace_roles
from .rbac import WorkspaceHeaderResolverMixin
from rest_framework import serializers
from django.conf import settings
from workspace.serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)


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


def _seed_default_roles(workspace: Workspace) -> None:
    seed_workspace_roles(workspace)


class WorkspaceListCreateView(WorkspaceHeaderResolverMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkspaceSerializer
    queryset = Workspace.objects.none()

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
            # Auto-create a subscription for onboarding (dev-friendly)
            Subscription.objects.create(
                workspace=ws,
                plan="free",
                status="active" if settings.DEBUG else "trial",
                limits={},
            )
        return Response(WorkspaceSerializer(ws).data, status=201)


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


class SubscriptionView(WorkspaceHeaderResolverMixin, generics.RetrieveUpdateAPIView):
    """Get or update the subscription for the active workspace.

    - GET: any active member can view
    - PATCH: only workspace owner; in DEBUG, allows toggling status/plan/limits directly
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_object(self):
        ws = self.get_workspace(self.request)
        if not ws:
            raise serializers.ValidationError(
                "Workspace not resolved. Provide X-Workspace-ID header."
            )
        try:
            sub = ws.subscription
        except Subscription.DoesNotExist:
            sub = Subscription.objects.create(
                workspace=ws, plan="free", status="trial", limits={}
            )
        return sub

    def patch(self, request, *args, **kwargs):
        sub = self.get_object()
        ws = sub.workspace
        if request.user != ws.owner:
            return Response(
                {"detail": "Only owner can update subscription."}, status=403
            )
        # Dev-friendly: allow plan/status/limits updates directly in DEBUG
        data = {
            k: v for k, v in request.data.items() if k in {"plan", "status", "limits"}
        }
        if not settings.DEBUG and ("status" in data or "limits" in data):
            # In non-debug, restrict updates to plan only (placeholder)
            data.pop("status", None)
            data.pop("limits", None)
        serializer = self.get_serializer(sub, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserProfileView(generics.RetrieveAPIView):
    """Get current user's profile information."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = get_user_model().objects.none()

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
    queryset = get_user_model().objects.none()

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
    queryset = WorkspaceMembership.objects.none()

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
