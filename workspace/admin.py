from django.contrib import admin
from unfold.admin import ModelAdmin
from common.admin import BaseModelAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from workspace.models import User
from .models import (
    Workspace,
    WorkspaceRole,
    WorkspaceMembership,
    RolePermission,
    UserPermissionOverride,
    Subscription,
    Organization,
)


@admin.register(Workspace)
class WorkspaceAdmin(BaseModelAdmin):
    list_display = ("name", "owner", "created_at")


@admin.register(WorkspaceRole)
class WorkspaceRoleAdmin(BaseModelAdmin):
    list_display = ("workspace", "name", "is_system")


@admin.register(WorkspaceMembership)
class WorkspaceMembershipAdmin(BaseModelAdmin):
    list_display = ("workspace", "user", "role", "is_active")


@admin.register(RolePermission)
class RolePermissionAdmin(BaseModelAdmin):
    list_display = ("role", "code", "scope")


@admin.register(UserPermissionOverride)
class UserPermissionOverrideAdmin(BaseModelAdmin):
    list_display = ("membership", "code", "scope", "allow")


@admin.register(Subscription)
class SubscriptionAdmin(BaseModelAdmin):
    list_display = ("workspace", "plan", "status")


# --- UNREGISTER DEFAULT ADMIN CLASSES ---


admin.site.unregister(Group)


# --- REGISTER ADMIN CLASSES ---


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Important dates",
            {
                "fields": ("last_login", "date_joined"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
        (
            "Personal info",
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "email"),
            },
        ),
        (
            "Permissions",
            {
                "classes": ("wide", "collapse"),
                "fields": ("is_active", "is_staff", "is_superuser", "groups"),
            },
        ),
    )


@admin.register(Organization)
class OrganizationAdmin(BaseModelAdmin):
    list_display = ("name", "owner", "created_at")
