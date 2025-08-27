from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from workspace.serializers.workspaces import OrganizationSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from workspace.services.access_control import (
    WorkspaceHeaderResolverMixin,
    WorkspaceRBACPermission,
)


class OrganizationView(WorkspaceHeaderResolverMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated, WorkspaceRBACPermission]
    resource = "organization"
    serializer_class = OrganizationSerializer

    def get_object(self):
        ws = self.get_workspace(self.request)
        return ws.organization if ws else None

    @extend_schema(
        operation_id="get_organization",
        summary="Get current workspace's organization",
        parameters=[
            OpenApiParameter(
                name="X-Workspace-ID",
                type={"type": "string", "format": "uuid"},
                required=True,
                location=OpenApiParameter.HEADER,
                description="Active workspace ID.",
            )
        ],
        responses={200: OrganizationSerializer},
    )
    def get(self, request, *args, **kwargs):
        org = self.get_object()
        if not org:
            return Response({"detail": "No organization"}, status=404)
        return Response(self.get_serializer(org).data)

    @extend_schema(
        operation_id="update_organization",
        summary="Update organization information",
        parameters=[
            OpenApiParameter(
                name="X-Workspace-ID",
                type={"type": "string", "format": "uuid"},
                required=True,
                location=OpenApiParameter.HEADER,
                description="Active workspace ID.",
            )
        ],
        request=OrganizationSerializer,
        responses={200: OrganizationSerializer},
    )
    def patch(self, request, *args, **kwargs):
        org = self.get_object()
        if not org:
            return Response({"detail": "No organization"}, status=404)
        serializer = self.get_serializer(org, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
