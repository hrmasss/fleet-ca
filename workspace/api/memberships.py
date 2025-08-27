from rest_framework import generics
from drf_spectacular.utils import extend_schema
from workspace.models import WorkspaceMembership
from rest_framework.permissions import IsAuthenticated
from workspace.serializers.memberships import MembershipSerializer


class MyMembershipsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = WorkspaceMembership.objects.none()
    serializer_class = MembershipSerializer

    @extend_schema(
        operation_id="list_my_memberships",
        summary="List my workspace memberships",
        responses={200: MembershipSerializer(many=True)},
    )
    def get_queryset(self):
        return WorkspaceMembership.objects.select_related("workspace", "role").filter(
            user=self.request.user
        )
