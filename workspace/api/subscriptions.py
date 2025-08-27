from workspace.models import Subscription
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from workspace.serializers.subscriptions import SubscriptionSerializer
from workspace.services.onboarding import confirm_plan
from workspace.services.access_control import (
    WorkspaceHeaderResolverMixin,
    WorkspaceRBACPermission,
    has_workspace_permission,
)


class SubscriptionView(WorkspaceHeaderResolverMixin, generics.RetrieveUpdateAPIView):
    """Get or update the subscription for the active workspace.

    - GET: any active member can view
    - PATCH: only workspace owner
    """

    permission_classes = [IsAuthenticated, WorkspaceRBACPermission]
    resource = "subscription"
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="X-Workspace-ID",
                type={"type": "string", "format": "uuid"},
                required=True,
                location=OpenApiParameter.HEADER,
                description="Active workspace ID.",
            )
        ]
    )
    def patch(self, request, *args, **kwargs):
        sub = self.get_object()
        ws = sub.workspace
        # Require subscription.change
        if not has_workspace_permission(request.user, ws, "subscription", "change"):
            return Response({"detail": "Insufficient permissions."}, status=403)
        # Only allow setting pending_plan (choose plan); confirmation is a separate action
        data = {k: v for k, v in request.data.items() if k in {"pending_plan"}}
        serializer = self.get_serializer(sub, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        operation_id="confirm_subscription",
        summary="Confirm pending plan",
        parameters=[
            OpenApiParameter(
                name="X-Workspace-ID",
                type={"type": "string", "format": "uuid"},
                required=True,
                location=OpenApiParameter.HEADER,
                description="Active workspace ID.",
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        sub = self.get_object()
        ws = sub.workspace
        if not has_workspace_permission(request.user, ws, "subscription", "change"):
            return Response({"detail": "Insufficient permissions."}, status=403)
        confirm_plan(ws)
        return Response(self.get_serializer(ws.subscription).data)
