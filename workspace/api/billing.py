from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter
from workspace.serializers.subscriptions import SubscriptionSerializer
from workspace.services.access_control import (
    WorkspaceHeaderResolverMixin,
    WorkspaceRBACPermission,
    has_workspace_permission,
)
from workspace.services.billing import (
    create_checkout_session,
    confirm_checkout_session,
)
from workspace.serializers.billing import (
    CheckoutRequestSerializer,
    CheckoutResponseSerializer,
    ConfirmRequestSerializer,
)


class CreateCheckoutSessionView(WorkspaceHeaderResolverMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, WorkspaceRBACPermission]
    resource = "subscription"

    @extend_schema(
        request=CheckoutRequestSerializer,
        responses={200: CheckoutResponseSerializer},
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
    def post(self, request):
        ws = self.get_workspace(request)
        if not ws:
            raise serializers.ValidationError(
                "Workspace not resolved. Provide X-Workspace-ID header."
            )
        if not has_workspace_permission(request.user, ws, "subscription", "change"):
            return Response({"detail": "Insufficient permissions."}, status=403)

        req = CheckoutRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        plan = req.validated_data["plan"]

        data = create_checkout_session(user=request.user, workspace=ws, plan=plan)
        res = CheckoutResponseSerializer(data=data)
        res.is_valid(raise_exception=True)
        return Response(res.data)


class ConfirmCheckoutSessionView(WorkspaceHeaderResolverMixin, APIView):
    permission_classes = [permissions.IsAuthenticated, WorkspaceRBACPermission]
    resource = "subscription"

    @extend_schema(
        request=ConfirmRequestSerializer,
        responses={200: SubscriptionSerializer},
        parameters=[
            OpenApiParameter(
                name="X-Workspace-ID",
                type={"type": "string", "format": "uuid"},
                required=True,
                location=OpenApiParameter.HEADER,
                description="Active workspace ID.",
            ),
            OpenApiParameter(
                name="session_id",
                type={"type": "string"},
                required=True,
                location=OpenApiParameter.QUERY,
                description="Stripe Checkout Session ID from frontend success URL.",
            ),
        ],
    )
    def post(self, request):
        ws = self.get_workspace(request)
        if not ws:
            raise serializers.ValidationError(
                "Workspace not resolved. Provide X-Workspace-ID header."
            )
        if not has_workspace_permission(request.user, ws, "subscription", "change"):
            return Response({"detail": "Insufficient permissions."}, status=403)

        data_in = {
            "session_id": request.query_params.get("session_id")
            or request.data.get("session_id")
        }
        req = ConfirmRequestSerializer(data=data_in)
        req.is_valid(raise_exception=True)
        session_id = req.validated_data["session_id"]

        data = confirm_checkout_session(workspace=ws, session_id=session_id)
        return Response(data)
