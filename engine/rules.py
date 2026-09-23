"""
Deterministic Policy & Compliance Layer.
Short-circuits scoring before calling any LLM if hard constraints or sanctions are triggered.
"""

from typing import List, Optional, Tuple
try:
    from pydantic import BaseModel, Field
except (ImportError, ModuleNotFoundError):
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
    def Field(default=None, default_factory=None):
        if default_factory is not None:
            return default_factory()
        return default


DISQUALIFYING_ROLES = [
    "student", "intern", "graduate student", "unemployed", "job seeker",
    "freelancer looking for work", "academic research only", "hobbyist"
]


class PolicyCheckResult(BaseModel):
    is_disqualified: bool = False
    disqualification_reason: str = ""
    matched_rule: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class PolicyEngine:
    """
    Evaluates hard deterministic rules before external AI calls.
    """

    @classmethod
    def evaluate_compliance(
        cls,
        location: str,
        role_title: str,
        prohibited_countries: Optional[List[str]] = None,
        min_deal_size_usd: float = 0.0,
        target_deal_size_usd: float = 0.0
    ) -> PolicyCheckResult:
        result = PolicyCheckResult()
        loc_lower = (location or "").lower().strip()
        role_lower = (role_title or "").lower().strip()

        # 1. Sanctions / Prohibited Territories Check
        prohibited = prohibited_countries or [
            "North Korea", "Iran", "Syria", "Cuba", "Russia", "Belarus"
        ]
        for country in prohibited:
            c_clean = country.strip().lower()
            if c_clean and c_clean in loc_lower:
                result.is_disqualified = True
                result.matched_rule = "SANCTIONED_TERRITORY"
                result.disqualification_reason = f"Prohibited / Sanctioned territory detected: '{country.strip()}' is blocked by corporate compliance policy."
                return result

        # 2. Anti-ICP Persona / Disqualifier Roles Check
        for disq_role in DISQUALIFYING_ROLES:
            if disq_role in role_lower:
                result.is_disqualified = True
                result.matched_rule = "ANTI_ICP_ROLE"
                result.disqualification_reason = f"Non-commercial persona detected: '{role_title}' does not have enterprise buying authority."
                return result

        return result
