from django.urls import path
from workspace.api.subscriptions import SubscriptionView
from workspace.api.profile import UserProfileView, UserProfileUpdateView
from workspace.api.invites import InviteCreateView, InviteAcceptView
from workspace.api.workspaces import WorkspaceListCreateView
from workspace.api.organization import OrganizationView
from workspace.api.memberships import MyMembershipsView
from workspace.api.billing import (
    CreateCheckoutSessionView,
    ConfirmCheckoutSessionView,
)

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path(
        "profile/update/", UserProfileUpdateView.as_view(), name="user-profile-update"
    ),
    path("workspaces/", WorkspaceListCreateView.as_view(), name="workspaces"),
    path("memberships/", MyMembershipsView.as_view(), name="my-memberships"),
    path("subscription/", SubscriptionView.as_view(), name="subscription"),
    path(
        "billing/checkout/",
        CreateCheckoutSessionView.as_view(),
        name="billing-checkout",
    ),
    path(
        "billing/confirm/", ConfirmCheckoutSessionView.as_view(), name="billing-confirm"
    ),
    path("organization/", OrganizationView.as_view(), name="organization"),
    path("invites/", InviteCreateView.as_view(), name="invite-create"),
    path("invites/accept/", InviteAcceptView.as_view(), name="invite-accept"),
]
