from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD_CONFIG = {
    "SITE_TITLE": "Oppora Marketing",
    "SITE_HEADER": "Oppora Marketing",
    "SITE_SYMBOL": "interests",
    "BORDER_RADIUS": "5px",
    "STYLES": [
        lambda request: static("css/admin.css"),
    ],
    "COLORS": {
        "base": {
            "50": "250 250 250",
            "100": "240 240 240",
            "200": "224 224 224",
            "300": "192 192 192",
            "400": "160 160 160",
            "500": "112 112 112",
            "600": "80 80 80",
            "700": "48 48 48",
            "800": "28 28 28",
            "900": "16 16 16",
            "950": "8 8 8",
        },
        "primary": {
            "50": "236 254 255",
            "100": "207 250 254",
            "200": "165 243 252",
            "300": "103 232 249",
            "400": "34 211 238",
            "500": "6 182 212",
            "600": "8 145 178",
            "700": "14 116 144",
            "800": "21 94 117",
            "900": "22 78 99",
            "950": "8 51 68",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-800)",
            "default-dark": "var(--color-base-200)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-50)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "collapsible": False,
                "items": [
                    {
                        "title": "Auth",
                        "icon": "lock",
                        "link": reverse_lazy("admin:workspace_user_changelist"),
                        "permission": lambda r: r.user.has_perm("workspace.view_user"),
                    },
                    {
                        "title": "Workspace",
                        "icon": "workspaces",
                        "link": reverse_lazy("admin:workspace_workspace_changelist"),
                        "permission": lambda r: r.user.has_perm(
                            "workspace.view_workspace"
                        ),
                    },
                    {
                        "title": "System",
                        "icon": "settings",
                        "link": reverse_lazy(
                            "admin:drf_api_logger_apilogsmodel_changelist"
                        ),
                        "permission": lambda r: r.user.has_perm(
                            "drf_api_logger.view_apilogsmodel"
                        ),
                    },
                ],
            }
        ],
    },
    "TABS": [
        {
            "models": [
                "workspace.workspace",
                "workspace.workspacerole",
                "workspace.workspacemembership",
                "workspace.subscription",
                "workspace.organization",
                "workspace.rolepermission",
                "workspace.userpermissionoverride",
            ],
            "items": [
                {
                    "title": "Workspaces",
                    "link": reverse_lazy("admin:workspace_workspace_changelist"),
                    "permission": lambda r: r.user.has_perm("workspace.view_workspace"),
                },
                {
                    "title": "Roles",
                    "link": reverse_lazy("admin:workspace_workspacerole_changelist"),
                    "permission": lambda r: r.user.has_perm(
                        "workspace.view_workspacerole"
                    ),
                },
                {
                    "title": "Members",
                    "link": reverse_lazy(
                        "admin:workspace_workspacemembership_changelist"
                    ),
                    "permission": lambda r: r.user.has_perm(
                        "workspace.view_workspacemembership"
                    ),
                },
                {
                    "title": "Subscriptions",
                    "link": reverse_lazy("admin:workspace_subscription_changelist"),
                    "permission": lambda r: r.user.has_perm(
                        "workspace.view_subscription"
                    ),
                },
                {
                    "title": "Organizations",
                    "link": reverse_lazy("admin:workspace_organization_changelist"),
                    "permission": lambda r: r.user.has_perm(
                        "workspace.view_organization"
                    ),
                },
                {
                    "title": "Access Rules",
                    "link": reverse_lazy("admin:workspace_rolepermission_changelist"),
                    "permission": lambda r: r.user.has_perm(
                        "workspace.view_rolepermission"
                    ),
                },
                {
                    "title": "User Overrides",
                    "link": reverse_lazy(
                        "admin:workspace_userpermissionoverride_changelist"
                    ),
                    "permission": lambda r: r.user.has_perm(
                        "workspace.view_userpermissionoverride"
                    ),
                },
            ],
        },
        {
            "models": [
                "drf_api_logger.apilogsmodel",
                "sites.site",
            ],
            "items": [
                {
                    "title": "API Logs",
                    "link": reverse_lazy(
                        "admin:drf_api_logger_apilogsmodel_changelist"
                    ),
                    "permission": lambda r: r.user.is_staff,
                },
                {
                    "title": "Sites",
                    "link": reverse_lazy("admin:sites_site_changelist"),
                    "permission": lambda r: r.user.has_perm("sites.view_site"),
                },
            ],
        },
        {
            "models": [
                "workspace.user",
                "account.emailaddress",
                "socialaccount.socialaccount",
                "socialaccount.socialapp",
                "socialaccount.socialtoken",
            ],
            "items": [
                {
                    "title": "Users",
                    "link": reverse_lazy("admin:workspace_user_changelist"),
                    "permission": lambda r: r.user.has_perm("workspace.view_user"),
                },
                {
                    "title": "Email addresses",
                    "link": reverse_lazy("admin:account_emailaddress_changelist"),
                    "permission": lambda r: r.user.is_staff,
                },
                {
                    "title": "Social accounts",
                    "link": reverse_lazy(
                        "admin:socialaccount_socialaccount_changelist"
                    ),
                    "permission": lambda r: r.user.is_staff,
                },
                {
                    "title": "Social apps",
                    "link": reverse_lazy("admin:socialaccount_socialapp_changelist"),
                    "permission": lambda r: r.user.is_staff,
                },
                {
                    "title": "Social tokens",
                    "link": reverse_lazy("admin:socialaccount_socialtoken_changelist"),
                    "permission": lambda r: r.user.is_staff,
                },
            ],
        },
    ],
}
