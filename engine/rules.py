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
        prohibited_countries: Optional[List[str]] = None
    ) -> PolicyCheckResult:
        result = PolicyCheckResult()
        loc_lower = (location or "").lower().strip()

        # 1. Dynamic Sanctions / Prohibited Territories Check
        if prohibited_countries:
            for country in prohibited_countries:
                c_clean = country.strip().lower()
                if c_clean and c_clean in loc_lower:
                    result.is_disqualified = True
                    result.matched_rule = "SANCTIONED_TERRITORY"
                    result.disqualification_reason = f"Prohibited territory detected: '{country.strip()}' is blocked by compliance policy."
                    return result

        return result
