from django.urls import path
from workspace.api import (
    TokenObtainPairView,
    TokenRefreshView,
    UserProfileView,
    UserProfileUpdateView,
    WorkspaceListCreateView,
    MyMembershipsView,
)

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh-token/", TokenRefreshView.as_view(), name="refresh-token"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path(
        "profile/update/", UserProfileUpdateView.as_view(), name="user-profile-update"
    ),
    path("workspaces/", WorkspaceListCreateView.as_view(), name="workspaces"),
    path("memberships/", MyMembershipsView.as_view(), name="my-memberships"),
]
