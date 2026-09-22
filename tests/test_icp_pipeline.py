"""
End-to-end Unit Tests for ICP Scoring Engine with Jev Primitives (Live API Only).
"""

import pytest
from unittest.mock import MagicMock
from engine.gtm_engine import GTMScoringEngine, StreamlinedLeadForm, StreamlinedScoringResult
from engine.client import JevClient, JevResponse, NoulResult, ChoiceResult, ScoreResult


def test_gtm_engine_fails_loudly_without_api_key():
    """Verify engine fails loudly without fabricating data when Jev API key is not present."""
    GTMScoringEngine._jev_client = JevClient(api_key="")
    form = StreamlinedLeadForm(
        company_name="Apex Global Logistics",
        industry_sector="Technology, SaaS",
        annual_revenue_usd=50000000.0,
        employee_count=500,
        location="United States",
        contact_name="Elena Vance",
        contact_role_title="VP Procurement"
    )

    res: StreamlinedScoringResult = GTMScoringEngine.evaluate(form)

    assert res.analysis_mode == "failed"
    assert "Jev API Key is required" in res.disqualification_reason or "missing" in res.disqualification_reason.lower()
    assert res.master_icp_score == 0.0


def test_gtm_engine_with_live_mocked_jev_response():
    """Verify GTMScoringEngine correctly computes GTM 4-pillars and tiers from Jev API response."""
    mock_client = MagicMock(spec=JevClient)
    mock_client.has_api_key = True
    mock_client.evaluate.return_value = JevResponse(
        success=True,
        nouls={
            "is_anti_icp": NoulResult(noul=False, probability=0.02, confidence=0.98),
            "is_student_or_intern": NoulResult(noul=False, probability=0.01, confidence=0.99),
            "has_budget_authority": NoulResult(noul=True, probability=0.95, confidence=0.95),
            "has_active_buying_cycle": NoulResult(noul=True, probability=0.90, confidence=0.92)
        },
        choices={
            "seniority_level": ChoiceResult(choice="C-Suite / Founder / Board (+5 pts)", confidence=0.95),
            "functional_department": ChoiceResult(choice="Procurement, Sourcing & Vendor Management", confidence=0.94),
            "buying_authority_level": ChoiceResult(choice="Sole Budget Sign-Off Authority ($50k+ Mandate)", confidence=0.93),
            "buyer_persona": ChoiceResult(choice="Economic Buyer (Signs the contract & owns the P&L)", confidence=0.96),
            "market_complexity": ChoiceResult(choice="Global Multi-National Enterprise (Tier 1)", confidence=0.91),
            "ecosystem_synergy": ChoiceResult(choice="High Synergy (Modern Cloud: AWS/Snowflake/Databricks/Salesforce)", confidence=0.90),
            "urgency_window": ChoiceResult(choice="Immediate Urgency (<30 Days / Live RFP)", confidence=0.89)
        },
        scores={
            "role_authority_scale": ScoreResult(score=9.5, level="Level 10", confidence=0.94),
            "firmographic_fit": ScoreResult(score=4.5, level="Tier-1 Enterprise Leader", confidence=0.91),
            "intent_velocity": ScoreResult(score=4.8, level="High-Velocity Mandate", confidence=0.93),
            "value_expansion": ScoreResult(score=4.0, level="High Contract Value", confidence=0.90)
        },
        latency_ms=150.0,
        mode="live_api"
    )

    GTMScoringEngine._jev_client = mock_client

    form = StreamlinedLeadForm(
        company_name="Apex Global Logistics",
        industry_sector="Technology & Cloud Infrastructure",
        annual_revenue_usd=120000000.0,
        revenue_entered_value=120.0,
        revenue_unit="Millions (M)",
        employee_count=1200,
        location="United States",
        branch_locations=["New York", "London"],
        contact_name="Elena Vance",
        contact_role_title="Senior Vice President of Global Procurement",
        buying_intent="Active RFP for global revenue decision automation.",
        target_deal_size_usd=85000.0,
        deal_entered_value=85.0,
        deal_unit="Thousands (k)"
    )

    res: StreamlinedScoringResult = GTMScoringEngine.evaluate(form)

    assert res.analysis_mode == "live"
    assert res.is_disqualified is False
    assert res.master_icp_score >= 80.0
    assert "Tier A1" in res.priority_tier
    assert res.ai_role.persona_type == "Economic Buyer (Signs the contract & owns the P&L)"
