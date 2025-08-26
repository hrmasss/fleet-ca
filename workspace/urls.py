from django.urls import path
from workspace.api import (
    UserProfileView,
    UserProfileUpdateView,
    WorkspaceListCreateView,
    MyMembershipsView,
)

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path(
        "profile/update/", UserProfileUpdateView.as_view(), name="user-profile-update"
    ),
    path("workspaces/", WorkspaceListCreateView.as_view(), name="workspaces"),
    path("memberships/", MyMembershipsView.as_view(), name="my-memberships"),
]
