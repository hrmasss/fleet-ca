from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from workspace.services.onboarding import choose_plan
from workspace.services.roles import seed_workspace_roles
from workspace.models import WorkspaceMembership, Subscription
from workspace.config.plans import limits_for
from workspace.services.access_control import WorkspaceHeaderResolverMixin
from workspace.models import Workspace
from workspace.serializers.workspaces import (
    WorkspaceSerializer,
    WorkspaceCreateSerializer,
)


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
        data_s = WorkspaceCreateSerializer(
            data=request.data, context={"request": request}
        )
        data_s.is_valid(raise_exception=True)
        with transaction.atomic():
            ws = data_s.save()
            # Seed roles if needed
            if ws.roles.count() == 0:
                seed_workspace_roles(ws)
            # Ensure creator is Owner member
            if not WorkspaceMembership.objects.filter(
                workspace=ws, user=request.user, is_active=True
            ).exists():
                owner_role = ws.roles.filter(name="Owner").first()
                WorkspaceMembership.objects.create(
                    workspace=ws, user=request.user, role=owner_role
                )
            # Ensure subscription exists
            try:
                _ = ws.subscription
            except Subscription.DoesNotExist:
                Subscription.objects.create(
                    workspace=ws,
                    plan="free",
                    status="trial",
                    limits=limits_for("free"),
                )
            desired = data_s.validated_data.get("plan")
            if desired and desired != "free":
                choose_plan(ws, desired)
        return Response(WorkspaceSerializer(ws).data, status=201)
