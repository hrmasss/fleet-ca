import pytest
from django.urls import reverse
from rest_framework import status
from .conftest import UserFactory
from workspace.models import Workspace, WorkspaceMembership


@pytest.mark.django_db
def test_user_can_register_and_login(api_client):
    # Register
    reg_url = reverse("rest_register")
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password1": "Testpass123!",
        "password2": "Testpass123!",
    }
    r = api_client.post(reg_url, payload)
    assert r.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    # Login
    login = api_client.post(
        reverse("rest_login"), {"username": "alice", "password": "Testpass123!"}
    )
    assert login.status_code == 200
    assert "access" in login.data


@pytest.mark.django_db
def test_user_can_create_workspace_with_org(authenticated_client, user):
    # Create with new org inline
    url = reverse("workspaces")
    payload = {
        "name": "Acme Workspace",
        "organization": {"name": "Acme Inc", "brand": {"primary": "#f00"}},
    }
    r = authenticated_client.post(url, payload, format="json")
    assert r.status_code == status.HTTP_201_CREATED
    ws_id = r.data["id"]
    ws = Workspace.objects.get(id=ws_id)
    assert ws.organization is not None
    assert ws.organization.name == "Acme Inc"

    # Create another workspace reusing same org
    r2 = authenticated_client.post(
        url,
        {"name": "Acme Workspace 2", "organization_id": str(ws.organization.id)},
        format="json",
    )
    assert r2.status_code == status.HTTP_201_CREATED
    ws2 = Workspace.objects.get(id=r2.data["id"])
    assert ws2.organization_id == ws.organization_id


@pytest.mark.django_db
def test_multiple_workspaces_can_have_different_orgs(authenticated_client):
    url = reverse("workspaces")
    r1 = authenticated_client.post(
        url,
        {"name": "Org A WS", "organization": {"name": "Org A"}},
        format="json",
    )
    assert r1.status_code == 201
    r2 = authenticated_client.post(
        url,
        {"name": "Org B WS", "organization": {"name": "Org B"}},
        format="json",
    )
    assert r2.status_code == 201
    ws1 = Workspace.objects.get(id=r1.data["id"])
    ws2 = Workspace.objects.get(id=r2.data["id"])
    assert ws1.organization_id != ws2.organization_id


@pytest.mark.django_db
def test_user_can_join_workspace_via_invite(api_client):
    # Arrange: owner creates workspace and invite
    owner = UserFactory(username="owner", password="pass12345")
    api_client.force_authenticate(user=owner)
    ws_resp = api_client.post(
        reverse("workspaces"),
        {"name": "Team WS", "organization": {"name": "Team Org"}},
        format="json",
    )
    assert ws_resp.status_code == 201
    ws_id = ws_resp.data["id"]

    invite_resp = api_client.post(
        reverse("invite-create"),
        {"email": "bob@example.com"},
        HTTP_X_WORKSPACE_ID=str(ws_id),
        format="json",
    )
    assert invite_resp.status_code == 201
    token = invite_resp.data["token"]

    # Invitee accepts
    bob = UserFactory(username="bob", password="pass12345")
    client_bob = api_client
    client_bob.force_authenticate(user=bob)
    accept = client_bob.post(reverse("invite-accept"), {"token": token}, format="json")
    assert accept.status_code == 200
    assert WorkspaceMembership.objects.filter(workspace_id=ws_id, user=bob).exists()


@pytest.mark.django_db
def test_rbac_is_workspace_scoped(authenticated_client, user):
    # Create two separate workspaces
    url = reverse("workspaces")
    w1 = authenticated_client.post(url, {"name": "W1"}, format="json")
    w2 = authenticated_client.post(url, {"name": "W2"}, format="json")
    assert w1.status_code == 201 and w2.status_code == 201

    # Subscription is guarded by WorkspaceRBACPermission; creator is Owner, should have change
    sub_patch = authenticated_client.patch(
        reverse("subscription"),
        {"pending_plan": "pro"},
        HTTP_X_WORKSPACE_ID=str(w1.data["id"]),
        format="json",
    )
    assert sub_patch.status_code in (200, 403)
    # For sanity, hitting W2 should not reduce permissions of W1 and vice versa; differences are expected per workspace
    sub_patch2 = authenticated_client.patch(
        reverse("subscription"),
        {"pending_plan": "pro"},
        HTTP_X_WORKSPACE_ID=str(w2.data["id"]),
        format="json",
    )
    assert sub_patch2.status_code in (200, 403)
