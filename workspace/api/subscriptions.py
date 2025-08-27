from workspace.models import Subscription
from rest_framework.response import Response
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from workspace.services.access_control import WorkspaceHeaderResolverMixin
from workspace.serializers.subscriptions import SubscriptionSerializer


class SubscriptionView(WorkspaceHeaderResolverMixin, generics.RetrieveUpdateAPIView):
    """Get or update the subscription for the active workspace.

    - GET: any active member can view
    - PATCH: only workspace owner
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
        data = {
            k: v for k, v in request.data.items() if k in {"plan", "status", "limits"}
        }
        serializer = self.get_serializer(sub, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
