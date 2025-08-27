import secrets
from rest_framework import generics
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from workspace.models import WorkspaceInvite, WorkspaceMembership
from workspace.services.access_control import (
    WorkspaceHeaderResolverMixin,
    WorkspaceRBACPermission,
)
from workspace.serializers.invites import (
    InviteCreateSerializer,
    InviteSerializer,
    InviteAcceptSerializer,
)


class InviteCreateView(WorkspaceHeaderResolverMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated, WorkspaceRBACPermission]
    resource = "invites"
    serializer_class = InviteCreateSerializer

    @extend_schema(
        operation_id="create_invite",
        summary="Invite a user to the workspace",
        request=InviteCreateSerializer,
        responses={201: InviteSerializer},
    )
    def post(self, request, *args, **kwargs):
        ws = self.get_workspace(request)
        if not ws:
            return Response({"detail": "Workspace not found."}, status=404)
        s = InviteCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        role = s.validated_data.get("role_id")
        token = secrets.token_urlsafe(24)
        invite, _created = WorkspaceInvite.objects.update_or_create(
            workspace=ws,
            email=s.validated_data["email"],
            defaults={"role": role, "token": token, "accepted": False},
        )
        join_url = f"{request.build_absolute_uri('/api/workspace/invites/accept/')}?token={invite.token}"
        send_mail(
            subject=f"You're invited to {ws.name}",
            message=f"Join workspace {ws.name}: {join_url}",
            from_email=None,
            recipient_list=[invite.email],
            fail_silently=True,
        )
        return Response(InviteSerializer(invite).data, status=201)


class InviteAcceptView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InviteAcceptSerializer

    @extend_schema(
        operation_id="accept_invite",
        summary="Accept a workspace invite",
        request=InviteAcceptSerializer,
        responses={200: None},
    )
    def post(self, request, *args, **kwargs):
        s = InviteAcceptSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            invite = WorkspaceInvite.objects.select_related("workspace", "role").get(
                token=s.validated_data["token"], accepted=False
            )
        except WorkspaceInvite.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=400)
        ws = invite.workspace
        # Default role: Member (if not provided)
        role = invite.role or ws.roles.filter(name="Member").first()
        WorkspaceMembership.objects.get_or_create(
            workspace=ws, user=request.user, defaults={"role": role}
        )
        invite.accepted = True
        invite.save(update_fields=["accepted"])
        return Response({"detail": "Joined"}, status=200)

    @extend_schema(
        operation_id="accept_invite_get",
        summary="Accept invite by visiting link",
        responses={200: None},
    )
    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        if not token:
            return Response({"detail": "Missing token"}, status=400)
        try:
            invite = WorkspaceInvite.objects.select_related("workspace", "role").get(
                token=token, accepted=False
            )
        except WorkspaceInvite.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=400)
        ws = invite.workspace
        role = invite.role or ws.roles.filter(name="Member").first()
        WorkspaceMembership.objects.get_or_create(
            workspace=ws, user=request.user, defaults={"role": role}
        )
        invite.accepted = True
        invite.save(update_fields=["accepted"])
        return Response({"detail": "Joined"}, status=200)
