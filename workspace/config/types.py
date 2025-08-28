from enum import Enum
from typing import TypedDict


class Resource(str, Enum):
    WORKSPACE_USERS = "workspace_users"
    ORGANIZATION = "organization"
    SUBSCRIPTION = "subscription"
    INVITES = "invites"
    ROLES = "roles"


class Action(str, Enum):
    VIEW = "view"
    CHANGE = "change"


class PermissionCode(str, Enum):
    WORKSPACE_USERS_VIEW = f"{Resource.WORKSPACE_USERS.value}.{Action.VIEW.value}"
    WORKSPACE_USERS_CHANGE = f"{Resource.WORKSPACE_USERS.value}.{Action.CHANGE.value}"

    ROLES_VIEW = f"{Resource.ROLES.value}.{Action.VIEW.value}"
    ROLES_CHANGE = f"{Resource.ROLES.value}.{Action.CHANGE.value}"

    SUBSCRIPTION_VIEW = f"{Resource.SUBSCRIPTION.value}.{Action.VIEW.value}"
    SUBSCRIPTION_CHANGE = f"{Resource.SUBSCRIPTION.value}.{Action.CHANGE.value}"

    INVITES_VIEW = f"{Resource.INVITES.value}.{Action.VIEW.value}"
    INVITES_CHANGE = f"{Resource.INVITES.value}.{Action.CHANGE.value}"

    ORGANIZATION_VIEW = f"{Resource.ORGANIZATION.value}.{Action.VIEW.value}"
    ORGANIZATION_CHANGE = f"{Resource.ORGANIZATION.value}.{Action.CHANGE.value}"


class WorkspacePlanLimits(TypedDict):
    users: int
    campaigns: int
    planning: int


class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"


class SubscriptionInterval(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
