from typing import Dict
from .types import PlanTier, WorkspacePlanLimits

PLAN_LIMITS: Dict[PlanTier, WorkspacePlanLimits] = {
    PlanTier.FREE: {"users": 3, "campaigns": 3, "planning": 1},
    PlanTier.PRO: {"users": 10, "campaigns": 50, "planning": 5},
    PlanTier.BUSINESS: {"users": 50, "campaigns": 500, "planning": 20},
}

PLAN_CHOICES = [tier.value for tier in PlanTier]


def limits_for(plan: str | PlanTier) -> WorkspacePlanLimits:
    tier = PlanTier(plan) if isinstance(plan, str) else plan
    return PLAN_LIMITS.get(tier, PLAN_LIMITS[PlanTier.FREE])
