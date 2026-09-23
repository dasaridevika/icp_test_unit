"""
Enterprise ICP Revenue Intelligence - Dynamic GTM Engine powered by Jev System One.
Replaces Cloudflare Workers AI / LLM with ultra-fast Jev System-1 decision primitives
(Noul/bool, Choice, Score) for semantic analysis, role hierarchy, tech synergy, and qualification.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field

from engine.fx import FXEngine
from engine.rules import PolicyEngine, PolicyCheckResult
from engine.client import JevClient, JevResponse
from engine.primitives import (
    ICP_NOUL_QUESTIONS,
    ICP_CHOICE_QUESTIONS,
    ICP_SCORE_QUESTIONS,
    build_lead_state
)


# ==============================================================================
# 1. Output Data Models (Exact Match for Original UI)
# ==============================================================================

class RoleAIAnalysis(BaseModel):
    raw_title: str = ""
    seniority_level: str = "Individual Contributor (+1)"
    seniority_points: int = 1
    persona_type: str = "Technical Champion"
    department: str = "Operations"
    confidence: float = 0.95
    rationale: str = ""
    is_disqualifier: bool = False


class NicheAIAnalysis(BaseModel):
    raw_niche: str = ""
    suggested_sector: str = ""
    market_complexity: str = "Specialized Enterprise"
    fit_points: int = 3
    rationale: str = ""


class IntentAIAnalysis(BaseModel):
    raw_intent: str = ""
    urgency_tier: str = "Active Evaluation (+3)"
    intent_points: int = 3
    timeline_detected: Optional[str] = None
    extracted_signals: List[str] = Field(default_factory=list)
    rationale: str = ""


class TechStackAIAnalysis(BaseModel):
    raw_stack: str = ""
    modern_tools: List[str] = Field(default_factory=list)
    legacy_blockers: List[str] = Field(default_factory=list)
    ecosystem_fit: str = "Standard Modern Cloud (+3)"
    tech_points: int = 3
    rationale: str = ""


class FootprintAIAnalysis(BaseModel):
    headquarters: str = ""
    branch_locations: List[str] = Field(default_factory=list)
    total_locations: int = 1
    geographic_reach: str = "Multi-Region Enterprise"
    tier1_matches: List[str] = Field(default_factory=list)
    prohibited_matches: List[str] = Field(default_factory=list)
    footprint_points: int = 3
    rationale: str = ""


class CompanyStandardsConfig(BaseModel):
    company_name: str = "Blackridge Research & Consulting"
    currency_symbol: str = "$"
    currency_code: str = "USD"
    min_deal_size_usd: float = 5000.0
    target_deal_size_usd: float = 25000.0
    min_company_revenue_usd: float = 5000000.0
    ideal_revenue_usd: float = 50000000.0
    min_headcount: int = 20
    ideal_headcount: int = 500
    target_focus_industries: List[str] = Field(default_factory=lambda: [
        "Energy, Utilities & Renewables",
        "Infrastructure & Construction",
        "Oil, Gas & Petrochemicals",
        "Industrial Goods & Manufacturing",
        "Automotive & Electric Mobility",
        "Chemicals & Materials",
        "Technology & Telecom"
    ])
    tier1_territories: List[str] = Field(default_factory=lambda: [
        "United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "India", "Australia", "Singapore", "United Arab Emirates", "Saudi Arabia"
    ])
    prohibited_countries: List[str] = Field(default_factory=lambda: [
        "North Korea", "Iran", "Syria", "Cuba", "Russia", "Belarus"
    ])
    weight_firmographics: float = 0.30
    weight_authority: float = 0.25
    weight_intent: float = 0.25
    weight_value: float = 0.20
    tier_a1_threshold: float = 80.0
    tier_a2_threshold: float = 65.0
    tier_b1_threshold: float = 50.0


class StreamlinedLeadForm(BaseModel):
    company_name: str = ""
    currency_symbol: str = "$"
    currency_code: str = "USD"
    revenue_entered_value: float = 0.0
    revenue_unit: str = "Standard"
    revenue_display_str: str = ""
    deal_entered_value: float = 0.0
    deal_unit: str = "Standard"
    deal_display_str: str = ""
    industry_sector: str = ""
    sub_vertical: str = ""
    annual_revenue_usd: float = 0.0
    employee_count: int = 0
    location: str = ""
    branch_locations: List[str] = Field(default_factory=list)
    contact_name: str = ""
    contact_email: str = ""
    contact_role_title: str = ""
    buying_role: str = ""
    buying_intent: str = ""
    timeline: str = ""
    target_deal_size_usd: float = 0.0
    tech_stack_notes: Optional[str] = ""
    uses_existing_platform: Optional[str] = ""
    existing_platform: Optional[str] = ""


class FieldScoreReceipt(BaseModel):
    field_name: str = ""
    pillar: str = ""
    raw_value: Any = None
    gtm_points: int = 0
    rationale: str = ""
    is_disqualifier: bool = False


class PillarScoreSummary(BaseModel):
    pillar_name: str
    score: float
    weight_pct: float
    field_receipts: List[FieldScoreReceipt] = Field(default_factory=list)


class ScoringTrackerItem(BaseModel):
    pillar_name: str
    allotted_score: float
    weight_pct: float
    points_contributed: float
    basis_criterion: str
    verified_signals: List[str] = Field(default_factory=list)
    deduction_gaps: List[str] = Field(default_factory=list)
    decision_rationale: str


class StreamlinedScoringResult(BaseModel):
    company_name: str
    master_icp_score: float
    priority_tier: str
    is_disqualified: bool
    disqualification_reason: str
    urgency_sla: str
    recommended_channel: str
    value_wedge: str
    outreach_hook: str
    pillar_firmographics: PillarScoreSummary
    pillar_authority: PillarScoreSummary
    pillar_intent: PillarScoreSummary
    pillar_value: PillarScoreSummary
    ai_role: Optional[RoleAIAnalysis] = None
    ai_niche: Optional[NicheAIAnalysis] = None
    ai_intent: Optional[IntentAIAnalysis] = None
    ai_tech: Optional[TechStackAIAnalysis] = None
    ai_footprint: Optional[FootprintAIAnalysis] = None
    scoring_tracker: List[ScoringTrackerItem] = Field(default_factory=list)
    lead_summary: Dict[str, Any] = Field(default_factory=dict)
    discovery_questions: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    analysis_mode: str = "live"
    degraded_reasons: List[str] = Field(default_factory=list)


# Backward compatibility aliases
LeadFormSubmission = StreamlinedLeadForm
GTMScoringResult = StreamlinedScoringResult


# ==============================================================================
# 2. GTM Scoring Engine powered by Jev System One Decisions
# ==============================================================================

class GTMScoringEngine:
    """
    Evaluates prospect leads using Jev System One decision primitives (bool, choice, score).
    Completely replaces Cloudflare AI Worker with deterministic, ultra-fast parallel evaluations.
    """

    _jev_client: Optional[JevClient] = None

    @classmethod
    def get_jev_client(cls) -> JevClient:
        if cls._jev_client is None or not cls._jev_client.has_api_key:
            cls._jev_client = JevClient()
        return cls._jev_client

    @classmethod
    def evaluate(
        cls,
        form: StreamlinedLeadForm,
        config: Optional[CompanyStandardsConfig] = None,
        worker_url: Optional[str] = None
    ) -> StreamlinedScoringResult:
        cfg = config or CompanyStandardsConfig()
        sym = form.currency_symbol or cfg.currency_symbol or "$"
        curr_code = form.currency_code or "USD"

        # 1. Normalize Native Currency to True USD (FX Engine)
        native_rev, norm_rev_usd = FXEngine.normalize_to_usd(
            form.revenue_entered_value,
            form.revenue_unit,
            curr_code
        )
        native_deal, norm_deal_usd = FXEngine.normalize_to_usd(
            form.deal_entered_value,
            form.deal_unit,
            curr_code
        )

        prospect_rev_str = form.revenue_display_str or f"{sym}{native_rev:,.0f} {curr_code}"
        prospect_deal_str = form.deal_display_str or f"{sym}{native_deal:,.0f} {curr_code}"

        # 2. Deterministic Policy & Compliance Check
        policy_res: PolicyCheckResult = PolicyEngine.evaluate_compliance(
            location=form.location,
            role_title=form.contact_role_title,
            prohibited_countries=cfg.prohibited_countries
        )

        if policy_res.is_disqualified:
            empty_pillar = PillarScoreSummary(pillar_name="Disqualified", score=0.0, weight_pct=0.0, field_receipts=[])
            return StreamlinedScoringResult(
                company_name=form.company_name or "Unspecified",
                master_icp_score=0.0,
                priority_tier="Disqualified: Compliance / Anti-ICP",
                is_disqualified=True,
                disqualification_reason=policy_res.disqualification_reason,
                urgency_sla="No Outreach (Archived)",
                recommended_channel="Do Not Contact",
                value_wedge="Account is blocked by organizational compliance policy.",
                outreach_hook="Disqualified prospect.",
                pillar_firmographics=empty_pillar,
                pillar_authority=empty_pillar,
                pillar_intent=empty_pillar,
                pillar_value=empty_pillar,
                analysis_mode="live",
                degraded_reasons=[],
                lead_summary={
                    "industry": form.industry_sector,
                    "location": form.location,
                    "contact_title": form.contact_role_title
                }
            )

        # 3. Build Unified Jev State
        jev_client = cls.get_jev_client()
        state = build_lead_state(
            company_name=form.company_name,
            industry=form.industry_sector,
            annual_revenue_usd=norm_rev_usd,
            headcount=form.employee_count,
            location=form.location,
            contact_name=form.contact_name,
            contact_role=form.contact_role_title,
            email=form.contact_email,
            buying_intent=form.buying_intent,
            target_deal_size_usd=norm_deal_usd,
            tech_stack=form.tech_stack_notes or form.existing_platform or form.uses_existing_platform or "",
            branches=form.branch_locations
        )

        # 4. Prepare Jev Questions (Noul, Choice, Score)
        all_questions = {}
        for k, v in ICP_NOUL_QUESTIONS.items():
            all_questions[k] = v.to_sdk_or_dict()
        for k, v in ICP_CHOICE_QUESTIONS.items():
            all_questions[k] = v.to_sdk_or_dict()
        for k, v in ICP_SCORE_QUESTIONS.items():
            all_questions[k] = v.to_sdk_or_dict()

        # 5. Evaluate Jev System-1 Decisions in Parallel (Live API Only)
        jev_res: JevResponse = jev_client.evaluate(state=state, questions=all_questions)

        # Fail Loudly if Jev API Key is Missing or API Call Fails
        if not jev_res.success:
            empty_pillar = PillarScoreSummary(pillar_name="Unavailable", score=0.0, weight_pct=0.0, field_receipts=[])
            return StreamlinedScoringResult(
                company_name=form.company_name or "Unspecified",
                master_icp_score=0.0,
                priority_tier="Evaluation Incomplete: Jev API Key Missing",
                is_disqualified=False,
                disqualification_reason=jev_res.error or "Jev API Key is required to perform live qualification.",
                urgency_sla="API Key Required",
                recommended_channel="Hold for API Configuration",
                value_wedge=jev_res.error or "Jev API Key is required. Please set JEV_API_KEY in your GitHub Secrets or environment.",
                outreach_hook="Jev API Offline - Key required for live scoring.",
                pillar_firmographics=empty_pillar,
                pillar_authority=empty_pillar,
                pillar_intent=empty_pillar,
                pillar_value=empty_pillar,
                analysis_mode="failed",
                degraded_reasons=[jev_res.error or "Jev API key not detected."],
                lead_summary={
                    "industry": form.industry_sector,
                    "location": form.location,
                    "contact_title": form.contact_role_title
                }
            )

        # 6. Parse Jev Decision Outputs
        # Anti-ICP gate check
        is_anti_icp = jev_res.nouls.get("is_anti_icp")
        is_student = jev_res.nouls.get("is_student_or_intern")
        if (is_anti_icp and is_anti_icp.noul and is_anti_icp.probability >= 0.70) or (is_student and is_student.noul and is_student.probability >= 0.70):
            empty_pillar = PillarScoreSummary(pillar_name="Disqualified", score=0.0, weight_pct=0.0, field_receipts=[])
            return StreamlinedScoringResult(
                company_name=form.company_name or "Unspecified",
                master_icp_score=0.0,
                priority_tier="Disqualified: Compliance / Anti-ICP",
                is_disqualified=True,
                disqualification_reason="Flagged as Student / Non-Commercial inquiry by Jev Anti-ICP Gate.",
                urgency_sla="No Outreach (Archived)",
                recommended_channel="Do Not Contact",
                value_wedge="Account is disqualified as a non-commercial inquiry.",
                outreach_hook="Disqualified prospect.",
                pillar_firmographics=empty_pillar,
                pillar_authority=empty_pillar,
                pillar_intent=empty_pillar,
                pillar_value=empty_pillar,
                analysis_mode="live",
                degraded_reasons=[]
            )

        # AI Role & Authority Model
        sen_choice = jev_res.choices.get("seniority_level")
        persona_choice = jev_res.choices.get("buyer_persona")
        dept_choice = jev_res.choices.get("functional_department")
        auth_level_choice = jev_res.choices.get("buying_authority_level")
        budget_noul = jev_res.nouls.get("has_budget_authority")
        role_scale_score = jev_res.scores.get("role_authority_scale")

        sen_str = sen_choice.choice if sen_choice else "Individual Contributor (+1)"
        sen_pts = 5 if "+5" in sen_str else (4 if "+4" in sen_str else (3 if "+3" in sen_str else (2 if "+2" in sen_str else 1)))
        
        ai_role = RoleAIAnalysis(
            raw_title=form.contact_role_title,
            seniority_level=sen_str,
            seniority_points=sen_pts,
            persona_type=persona_choice.choice if persona_choice else "Technical Champion",
            department=dept_choice.choice if dept_choice else "Operations",
            confidence=float(sen_choice.confidence if sen_choice else 0.95),
            rationale=f"Jev System One classified role as {sen_str.split('(')[0].strip()} with {auth_level_choice.choice if auth_level_choice else 'recommender'} authority.",
            is_disqualifier=False
        )

        # AI Niche & Market Complexity Model
        niche_choice = jev_res.choices.get("market_complexity")
        mkt_comp = niche_choice.choice if niche_choice else "Specialized Enterprise"
        fit_pts = 5 if "Global" in mkt_comp else (3 if "Specialized" in mkt_comp else 2)
        ai_niche = NicheAIAnalysis(
            raw_niche=form.sub_vertical or form.industry_sector,
            suggested_sector=form.industry_sector,
            market_complexity=mkt_comp,
            fit_points=fit_pts,
            rationale=f"Jev evaluated market complexity as {mkt_comp}."
        )

        # AI Intent & Urgency Model
        urg_choice = jev_res.choices.get("urgency_window")
        active_noul = jev_res.nouls.get("has_active_buying_cycle")
        urg_str = urg_choice.choice if urg_choice else "Active Project (1 to 3 Months)"
        intent_pts = 5 if "<30" in urg_str else (3 if "1 to 3" in urg_str else 1)
        ai_intent = IntentAIAnalysis(
            raw_intent=form.buying_intent,
            urgency_tier=urg_str,
            intent_points=intent_pts,
            timeline_detected=form.timeline or ("< 30 Days" if intent_pts == 5 else "< 90 Days"),
            extracted_signals=["Active RFP mandate" if intent_pts == 5 else "Commercial inquiry"],
            rationale=f"Jev detected buying timeline window: {urg_str}."
        )

        # AI Tech Stack Ecosystem Model
        eco_choice = jev_res.choices.get("ecosystem_synergy")
        eco_str = eco_choice.choice if eco_choice else "Standard Modern Cloud (+3)"
        tech_pts = 5 if "High Synergy" in eco_str else (3 if "Standard" in eco_str else 1)
        
        # Dynamically extract tools from user input notes
        raw_tech_list = [t.strip() for t in (form.tech_stack_notes or "").replace(",", " ").split() if len(t.strip()) > 2]
        
        ai_tech = TechStackAIAnalysis(
            raw_stack=form.tech_stack_notes or "",
            modern_tools=raw_tech_list if "High Synergy" in eco_str or "Standard" in eco_str else [],
            legacy_blockers=raw_tech_list if "Legacy" in eco_str else [],
            ecosystem_fit=eco_str,
            tech_points=tech_pts,
            rationale=f"Jev evaluated ecosystem compatibility as: {eco_str}."
        )

        # AI Global Footprint Model
        branches = [b.strip() for b in form.branch_locations if b.strip()]
        geo_reach = "Global Multi-Region Enterprise" if len(branches) >= 2 else (
            "Cross-Border Multi-Branch" if len(branches) == 1 else "Single-Market Hub"
        )
        ai_footprint = FootprintAIAnalysis(
            headquarters=form.location or "Primary Region",
            branch_locations=branches,
            total_locations=max(1, len(branches) + (1 if form.location else 0)),
            geographic_reach=geo_reach,
            tier1_matches=[b for b in branches if b in cfg.tier1_territories],
            prohibited_matches=[b for b in branches if b in cfg.prohibited_countries],
            footprint_points=5 if "Global" in geo_reach else 3,
            rationale="Multi-branch footprint analysis."
        )

        # -------------------------------------------------------------
        # 4-Pillar Score Computation from Jev Primitives
        # -------------------------------------------------------------
        # 1. Firmographics Scale (0-100)
        fg_score_obj = jev_res.scores.get("firmographic_fit")
        if fg_score_obj:
            firmo_base = min(100.0, (fg_score_obj.score / 3.0 * 85.0) + 15.0) if fg_score_obj.score <= 3.0 else min(100.0, (fg_score_obj.score / 4.0 * 100.0))
        else:
            firmo_base = 70.0

        # Focus industry alignment bonus (+8 pts)
        is_focus_ind = any(ind.lower() in (form.industry_sector or "").lower() for ind in cfg.target_focus_industries) if cfg.target_focus_industries else False
        if is_focus_ind:
            firmo_base = min(100.0, firmo_base + 8.0)
        firmo_score = max(10.0, min(100.0, firmo_base))

        # 2. Decision Authority (0-100)
        if role_scale_score:
            raw_role_score = role_scale_score.score
            if raw_role_score <= 9.0:
                qual_score = (raw_role_score / 9.0 * 85.0) + 15.0
            else:
                qual_score = (raw_role_score / 10.0 * 100.0)
        else:
            qual_score = 90.0 if sen_pts >= 4 else (75.0 if sen_pts >= 3 else 50.0)

        if "C-Suite" in sen_str or sen_pts == 5:
            qual_score = max(qual_score, 92.0)
        elif "VP" in sen_str or sen_pts == 4:
            qual_score = max(qual_score, 82.0)
        qual_score = max(10.0, min(100.0, qual_score))

        # 3. Intent & Readiness (0-100)
        if "Immediate" in urg_str or "<30" in urg_str or "< 1 Month" in (form.timeline or "") or "RFP" in (form.buying_intent or "").upper():
            readiness_score = 92.0
        elif "1 to 3" in urg_str or "Active" in urg_str:
            readiness_score = 78.0
        elif "3 to 6" in urg_str:
            readiness_score = 55.0
        else:
            intent_score_obj = jev_res.scores.get("intent_velocity")
            if intent_score_obj:
                readiness_score = (intent_score_obj.score / 3.0 * 80.0) + 20.0 if intent_score_obj.score <= 3.0 else (intent_score_obj.score / 4.0 * 100.0)
            else:
                readiness_score = 45.0
        readiness_score = max(10.0, min(100.0, readiness_score))

        # 4. Value & Technographics Synergy (0-100)
        stack_text = (form.tech_stack_notes or form.existing_platform or form.uses_existing_platform or "").upper()
        if "High Synergy" in eco_str or any(tool in stack_text for tool in ["SNOWFLAKE", "AWS", "SALESFORCE", "DATABRICKS", "AZURE", "MODERN CLOUD"]):
            techno_score = 90.0
        elif "Standard" in eco_str:
            techno_score = 75.0
        elif "Legacy" in eco_str:
            techno_score = 35.0
        else:
            val_score_obj = jev_res.scores.get("value_expansion")
            if val_score_obj:
                techno_score = (val_score_obj.score / 3.0 * 75.0) + 20.0 if val_score_obj.score <= 3.0 else (val_score_obj.score / 4.0 * 100.0)
            else:
                techno_score = 60.0
        techno_score = max(10.0, min(100.0, techno_score))

        firmo_pts_ui = max(1, min(5, int(round(firmo_score / 20.0))))
        techno_pts_ui = max(1, min(5, int(round(techno_score / 20.0))))

        pillar_firmo = PillarScoreSummary(
            pillar_name="Firmographics Scale",
            score=round(firmo_score, 1),
            weight_pct=cfg.weight_firmographics,
            field_receipts=[
                FieldScoreReceipt(field_name="Company Revenue", pillar="Firmographics", raw_value=prospect_rev_str, gtm_points=firmo_pts_ui, rationale=f"ARR: {prospect_rev_str} (~${norm_rev_usd:,.0f} USD)"),
                FieldScoreReceipt(field_name="Employee Headcount", pillar="Firmographics", raw_value=f"{form.employee_count:,} employees", gtm_points=firmo_pts_ui, rationale=f"Headcount: {form.employee_count:,}"),
                FieldScoreReceipt(field_name="Industry & Jev Niche", pillar="Firmographics", raw_value=f"{form.industry_sector} • {form.sub_vertical or 'General'}", gtm_points=ai_niche.fit_points, rationale=ai_niche.rationale),
                FieldScoreReceipt(field_name="Global Footprint", pillar="Firmographics", raw_value=geo_reach, gtm_points=ai_footprint.footprint_points, rationale=ai_footprint.rationale)
            ]
        )

        auth_val = f"{form.contact_role_title or 'Unspecified'} ({ai_role.persona_type})"
        pillar_auth = PillarScoreSummary(
            pillar_name="Decision Authority",
            score=round(qual_score, 1),
            weight_pct=cfg.weight_authority,
            field_receipts=[
                FieldScoreReceipt(field_name="Decision-Maker Title", pillar="Authority", raw_value=auth_val, gtm_points=ai_role.seniority_points, rationale=ai_role.rationale),
                FieldScoreReceipt(field_name="Buyer Persona", pillar="Authority", raw_value=ai_role.persona_type, gtm_points=3 if "Champion" in ai_role.persona_type else 5, rationale=f"Persona: {ai_role.persona_type}")
            ]
        )

        pillar_intent = PillarScoreSummary(
            pillar_name="Intent & Readiness",
            score=round(readiness_score, 1),
            weight_pct=cfg.weight_intent,
            field_receipts=[
                FieldScoreReceipt(field_name="Urgency & Timeline", pillar="Intent", raw_value=ai_intent.urgency_tier, gtm_points=ai_intent.intent_points, rationale=ai_intent.rationale)
            ]
        )

        pillar_val = PillarScoreSummary(
            pillar_name="Value & Tech Synergy",
            score=round(techno_score, 1),
            weight_pct=cfg.weight_value,
            field_receipts=[
                FieldScoreReceipt(field_name="Target Deal Value", pillar="Value", raw_value=prospect_deal_str, gtm_points=techno_pts_ui, rationale=f"Target ACV: {prospect_deal_str}"),
                FieldScoreReceipt(field_name="Ecosystem Compatibility", pillar="Value", raw_value=ai_tech.ecosystem_fit, gtm_points=ai_tech.tech_points, rationale=ai_tech.rationale)
            ]
        )

        # Aggregate Master ICP Score (0 to 100)
        c_firmo = round(pillar_firmo.score * cfg.weight_firmographics, 2)
        c_auth = round(pillar_auth.score * cfg.weight_authority, 2)
        c_intent = round(pillar_intent.score * cfg.weight_intent, 2)
        c_val = round(pillar_val.score * cfg.weight_value, 2)
        master_score = round(c_firmo + c_auth + c_intent + c_val, 1)

        # Priority Tier Assignment
        if master_score >= cfg.tier_a1_threshold:
            tier = "Tier A1: Strategic Inbound Target"
            sla = "<2 Hours Executive Callback"
            channel = "Senior AE & RevOps Director"
        elif master_score >= cfg.tier_a2_threshold:
            tier = "Tier A2: High Priority Outbound"
            sla = "<24 Hours Outbound Sequence"
            channel = "Senior SDR Strategic Outreach"
        elif master_score >= cfg.tier_b1_threshold:
            tier = "Tier B1: Mid-Market Fast Track"
            sla = "<48 Hours Qualification Call"
            channel = "Inside Sales / AE"
        else:
            tier = "Tier C: Low Priority / Nurture"
            sla = "Automated Marketing Track"
            channel = "Marketing Nurture Campaign"

        # Deliverables Copywriting
        role_t = form.contact_role_title or "Technology Leader"
        comp_t = form.company_name or "your organization"
        outreach_hook = f"Hi {form.contact_name or 'there'}, seeing your focus on {form.sub_vertical or form.industry_sector} at {comp_t}, I wanted to share how our intelligence infrastructure empowers {role_t}s to accelerate qualification cycles."
        value_wedge = f"For {comp_t}, deploying our automated decision engine eliminates evaluation friction and drives pipeline conversion on ${norm_deal_usd:,.0f}+ opportunities."

        discovery_qs = [
            f"How are you currently connecting {form.sub_vertical or form.industry_sector} pipeline intelligence into your core ERP & CRM systems?",
            f"What specific evaluation milestones does {role_t} require before finalizing deployment for this cycle?",
            f"Which operational metrics are critical for proving ROI on ${norm_deal_usd:,.0f} target engagements?"
        ]

        strengths = [
            f"Verified annual ARR of {prospect_rev_str} (~${norm_rev_usd:,.0f} USD).",
            f"Executive stakeholder engagement: {form.contact_name or 'Contact'} ({role_t}).",
            f"Target deal ACV of {prospect_deal_str} aligns with enterprise target."
        ]
        if branches:
            strengths.append(f"Multi-region footprint across {len(branches)} branch hub(s): {', '.join(branches)}.")

        risks = []
        if not form.buying_intent:
            risks.append("Buying intent details are sparse; requires discovery on timeline urgency.")

        tracker_items = [
            ScoringTrackerItem(pillar_name="Firmographics Scale", allotted_score=pillar_firmo.score, weight_pct=cfg.weight_firmographics, points_contributed=c_firmo, basis_criterion="Scale & Complexity", verified_signals=strengths[:2], deduction_gaps=[], decision_rationale="Jev verified firmographic scale."),
            ScoringTrackerItem(pillar_name="Decision Authority", allotted_score=pillar_auth.score, weight_pct=cfg.weight_authority, points_contributed=c_auth, basis_criterion="Executive Stakeholder", verified_signals=[f"Role: {role_t}"], deduction_gaps=[], decision_rationale=ai_role.rationale),
            ScoringTrackerItem(pillar_name="Intent & Readiness", allotted_score=pillar_intent.score, weight_pct=cfg.weight_intent, points_contributed=c_intent, basis_criterion="Buying Velocity", verified_signals=[f"Urgency: {ai_intent.urgency_tier}"], deduction_gaps=risks, decision_rationale=ai_intent.rationale),
            ScoringTrackerItem(pillar_name="Value & Tech Synergy", allotted_score=pillar_val.score, weight_pct=cfg.weight_value, points_contributed=c_val, basis_criterion="Contract Potential", verified_signals=[f"Deal: {prospect_deal_str}"], deduction_gaps=[], decision_rationale=ai_tech.rationale)
        ]

        return StreamlinedScoringResult(
            company_name=form.company_name or "Prospective Account",
            master_icp_score=master_score,
            priority_tier=tier,
            is_disqualified=False,
            disqualification_reason="",
            urgency_sla=sla,
            recommended_channel=channel,
            value_wedge=value_wedge,
            outreach_hook=outreach_hook,
            pillar_firmographics=pillar_firmo,
            pillar_authority=pillar_auth,
            pillar_intent=pillar_intent,
            pillar_value=pillar_val,
            ai_role=ai_role,
            ai_niche=ai_niche,
            ai_intent=ai_intent,
            ai_tech=ai_tech,
            ai_footprint=ai_footprint,
            scoring_tracker=tracker_items,
            lead_summary={
                "company": form.company_name,
                "industry": form.industry_sector,
                "revenue": prospect_rev_str,
                "deal_size": prospect_deal_str,
                "location": form.location,
                "contact": f"{form.contact_name} ({role_t})"
            },
            discovery_questions=discovery_qs,
            key_strengths=strengths,
            key_risks=risks,
            analysis_mode="live",
            degraded_reasons=[]
        )
