"""
Configuration, GTM Pillar Weights, and Tier Thresholds for ICP Scoring.
"""

from typing import List, Dict
from pydantic import BaseModel, Field


class OrganizationConfig(BaseModel):
    """Authoritative organization qualification criteria."""
    org_name: str = "Enterprise GTM Revenue Intelligence"
    currency_symbol: str = "$"
    currency_code: str = "USD"
    min_deal_size_usd: float = 5000.0
    target_deal_size_usd: float = 25000.0
    ideal_annual_revenue_usd: float = 50000000.0
    min_headcount: int = 25
    ideal_headcount: int = 500

    # Target Sectors
    target_focus_industries: List[str] = Field(default_factory=lambda: [
        "Technology, SaaS & Cloud Infrastructure",
        "Financial Services & FinTech",
        "Healthcare & Life Sciences",
        "Industrial Goods & Manufacturing",
        "Energy, Utilities & Renewables",
        "E-commerce & Retail Tech"
    ])

    # Geographic Tiers & Sanctions
    tier1_territories: List[str] = Field(default_factory=lambda: [
        "United States", "Canada", "United Kingdom", "Germany",
        "France", "Japan", "Australia", "Singapore", "India",
        "United Arab Emirates", "Nordics", "Switzerland"
    ])
    prohibited_countries: List[str] = Field(default_factory=lambda: [
        "North Korea", "Iran", "Syria", "Cuba", "Russia", "Belarus"
    ])

    # GTM 4-Pillar authorative weights (Must sum to 1.0)
    weight_firmographics: float = 0.30
    weight_authority: float = 0.25
    weight_intent: float = 0.25
    weight_value: float = 0.20

    # Tier Thresholds (0-100 Master ICP Score)
    tier_a1_threshold: float = 80.0
    tier_a2_threshold: float = 65.0
    tier_b1_threshold: float = 50.0


class PriorityTier:
    TIER_A1 = "Tier A1: Strategic High-Fit Inbound"
    TIER_A2 = "Tier A2: High-Priority Outbound Target"
    TIER_B1 = "Tier B1: Mid-Market Fast Track"
    TIER_C = "Tier C: Long-Tail / Nurture"
    DISQUALIFIED = "Disqualified: Anti-ICP / Compliance Policy"

    ACTION_MAP: Dict[str, Dict[str, str]] = {
        TIER_A1: {
            "sla": "<2 Hours Executive Callback",
            "channel": "Strategic AE + RevOps Director",
            "action": "Trigger immediate high-touch sequence with bespoke architecture proposal."
        },
        TIER_A2: {
            "sla": "<24 Hours Outbound Touch",
            "channel": "Senior SDR Personalized Outreach",
            "action": "Execute multi-threaded executive outreach focusing on ecosystem integration."
        },
        TIER_B1: {
            "sla": "<48 Hours Qualification",
            "channel": "Inside Sales / Account Executive",
            "action": "Standard qualification call with tailored industry deck and discovery questions."
        },
        TIER_C: {
            "sla": "Automated Marketing Track",
            "channel": "Product Nurture Campaign",
            "action": "Enroll in automated product webinars and monthly educational newsletters."
        },
        DISQUALIFIED: {
            "sla": "No Outreach (Archived)",
            "channel": "Blocked / Anti-ICP Gate",
            "action": "Flagged as disqualified under compliance, student/freemail, or out-of-scope criteria."
        }
    }
