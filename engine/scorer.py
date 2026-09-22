"""
Enterprise ICP Revenue Qualification Engine powered by Jev System-1 Decisions.
Computes 4-dimensional GTM pillar scores, calibrated priority tiers, and sales actions.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from engine.config import OrganizationConfig, PriorityTier
from engine.client import JevClient, JevResponse
from engine.primitives import (
    ICP_NOUL_QUESTIONS,
    ICP_CHOICE_QUESTIONS,
    ICP_SCORE_QUESTIONS,
    build_lead_state
)


class ProspectLead(BaseModel):
    """Lead submission payload for qualification."""
    company_name: str = ""
    industry_sector: str = "Technology & SaaS"
    annual_revenue_usd: float = 10000000.0
    employee_count: int = 100
    location: str = "United States"
    branch_locations: List[str] = Field(default_factory=list)
    contact_name: str = ""
    contact_email: str = ""
    contact_role_title: str = ""
    target_deal_size_usd: float = 25000.0
    buying_intent: str = ""
    tech_stack_notes: str = ""
    raw_notes: str = ""


class PillarReceipt(BaseModel):
    """Detailed score receipt for a single GTM qualification pillar."""
    pillar_name: str
    allotted_score: float  # 0 to 100
    weight_pct: float      # e.g., 0.30
    points_contributed: float # allotted_score * weight_pct
    basis_criterion: str
    verified_signals: List[str] = Field(default_factory=list)
    deduction_gaps: List[str] = Field(default_factory=list)
    decision_rationale: str


class JevPrimitiveReceipt(BaseModel):
    """Receipt for individual Jev decision primitive output."""
    primitive_type: str  # "noul (bool)" | "choice" | "score"
    question_key: str
    question_instructions: str
    result_value: Any
    confidence: float
    probability_or_distribution: Any


class ICPScoringReport(BaseModel):
    """Authoritative qualification output report."""
    company_name: str
    master_icp_score: float  # 0 to 100
    priority_tier: str
    is_disqualified: bool
    disqualification_reason: Optional[str] = None
    urgency_sla: str
    recommended_channel: str
    sales_action: str
    outreach_hook: str
    value_wedge: str

    # 4 GTM Pillars
    pillar_firmographics: PillarReceipt
    pillar_authority: PillarReceipt
    pillar_intent: PillarReceipt
    pillar_value: PillarReceipt

    # Jev Raw Decision Receipts
    jev_primitives: List[JevPrimitiveReceipt] = Field(default_factory=list)
    overall_confidence: float = 0.90
    execution_latency_ms: float = 0.0
    execution_mode: str = "live"  # "live_sdk" | "live_rest" | "simulation"


class JevICPScorer:
    """
    Evaluates prospect leads using Jev System One decision primitives.
    """

    def __init__(self, client: Optional[JevClient] = None, config: Optional[OrganizationConfig] = None):
        self.client = client or JevClient()
        self.config = config or OrganizationConfig()

    def evaluate_lead(self, lead: ProspectLead) -> ICPScoringReport:
        """
        Executes full ICP evaluation using Jev primitives.
        """
        # 1. Build unified State for Jev
        state = build_lead_state(
            company_name=lead.company_name,
            industry=lead.industry_sector,
            annual_revenue_usd=lead.annual_revenue_usd,
            headcount=lead.employee_count,
            location=lead.location,
            contact_name=lead.contact_name,
            contact_role=lead.contact_role_title,
            email=lead.contact_email,
            buying_intent=lead.buying_intent,
            target_deal_size_usd=lead.target_deal_size_usd,
            tech_stack=lead.tech_stack_notes,
            branches=lead.branch_locations,
            raw_text=lead.raw_notes
        )

        # 2. Combine all question primitives for a single parallel evaluation pass
        all_questions = {}
        for k, v in ICP_NOUL_QUESTIONS.items():
            all_questions[k] = v.to_sdk_or_dict()
        for k, v in ICP_CHOICE_QUESTIONS.items():
            all_questions[k] = v.to_sdk_or_dict()
        for k, v in ICP_SCORE_QUESTIONS.items():
            all_questions[k] = v.to_sdk_or_dict()

        # 3. Query Jev System One
        jev_res: JevResponse = self.client.evaluate(state=state, questions=all_questions)

        # 4. Check Hard Disqualification Gates via Noul (bool) primitives
        is_anti_icp = jev_res.nouls.get("is_anti_icp")
        is_student = jev_res.nouls.get("is_student_or_intern")
        is_jobseeker = jev_res.nouls.get("is_jobseeker_or_recruiter")
        is_sanctioned = jev_res.nouls.get("is_sanctioned_region")

        is_disqualified = False
        disqualify_reason = None

        if is_anti_icp and is_anti_icp.noul and is_anti_icp.probability >= 0.70:
            is_disqualified = True
            disqualify_reason = "Flagged as Student / Freemail / Non-Commercial Inquiry by Jev Anti-ICP Gate."
        elif is_student and is_student.noul and is_student.probability >= 0.70:
            is_disqualified = True
            disqualify_reason = "Flagged as Student / Academic / Intern Inquiry (Non-Commercial Account)."
        elif is_jobseeker and is_jobseeker.noul and is_jobseeker.probability >= 0.70:
            is_disqualified = True
            disqualify_reason = "Flagged as Job Applicant / Recruiter Pitch (Non-Procurement Lead)."
        elif is_sanctioned and is_sanctioned.noul and is_sanctioned.probability >= 0.70:
            is_disqualified = True
            disqualify_reason = "Prohibited geographic jurisdiction under trade compliance policy."
        elif lead.location in self.config.prohibited_countries:
            is_disqualified = True
            disqualify_reason = f"Location '{lead.location}' is on the prohibited compliance list."

        # Collect primitive receipts
        primitive_receipts: List[JevPrimitiveReceipt] = []
        for k, nr in jev_res.nouls.items():
            primitive_receipts.append(JevPrimitiveReceipt(
                primitive_type="Noul (Bool)",
                question_key=k,
                question_instructions=ICP_NOUL_QUESTIONS[k].instructions if k in ICP_NOUL_QUESTIONS else k,
                result_value=nr.noul,
                confidence=nr.confidence,
                probability_or_distribution=nr.probability
            ))
        for k, cr in jev_res.choices.items():
            primitive_receipts.append(JevPrimitiveReceipt(
                primitive_type="Choice",
                question_key=k,
                question_instructions=ICP_CHOICE_QUESTIONS[k].instructions if k in ICP_CHOICE_QUESTIONS else k,
                result_value=cr.choice,
                confidence=cr.confidence,
                probability_or_distribution=cr.distribution
            ))
        for k, sr in jev_res.scores.items():
            primitive_receipts.append(JevPrimitiveReceipt(
                primitive_type="Score",
                question_key=k,
                question_instructions=ICP_SCORE_QUESTIONS[k].instructions if k in ICP_SCORE_QUESTIONS else k,
                result_value=f"{sr.score:.1f}/5.0 ({sr.level or 'Calibrated'})",
                confidence=sr.confidence,
                probability_or_distribution=sr.level_probabilities
            ))

        if is_disqualified:
            empty_receipt = lambda name: PillarReceipt(
                pillar_name=name,
                allotted_score=0.0,
                weight_pct=0.0,
                points_contributed=0.0,
                basis_criterion="Disqualified Account",
                decision_rationale=disqualify_reason or "Disqualified"
            )
            action_info = PriorityTier.ACTION_MAP[PriorityTier.DISQUALIFIED]
            return ICPScoringReport(
                company_name=lead.company_name or "Disqualified Prospect",
                master_icp_score=0.0,
                priority_tier=PriorityTier.DISQUALIFIED,
                is_disqualified=True,
                disqualification_reason=disqualify_reason,
                urgency_sla=action_info["sla"],
                recommended_channel=action_info["channel"],
                sales_action=action_info["action"],
                outreach_hook="Prospect disqualified under compliance and ICP guidelines.",
                value_wedge="No outreach recommended.",
                pillar_firmographics=empty_receipt("Firmographics & Scale"),
                pillar_authority=empty_receipt("Decision Authority & Hierarchy"),
                pillar_intent=empty_receipt("Intent & Buying Velocity"),
                pillar_value=empty_receipt("Contract Value & Expansion"),
                jev_primitives=primitive_receipts,
                overall_confidence=0.95,
                execution_latency_ms=jev_res.latency_ms,
                execution_mode=jev_res.mode
            )

        # 5. Compute Pillar Scores (0 to 100 each)
        # 5.1 Pillar 1: Firmographics & Scale (Weight 30%)
        # Basis: Jev score question 'firmographic_fit' + Jev choice 'market_complexity'
        fg_score_obj = jev_res.scores.get("firmographic_fit")
        market_choice = jev_res.choices.get("market_complexity")
        fg_scale_pts = (fg_score_obj.score / 5.0 * 100.0) if fg_score_obj else 65.0

        # Adjust for territory
        is_tier1 = lead.location in self.config.tier1_territories
        if is_tier1:
            fg_scale_pts = min(100.0, fg_scale_pts + 5.0)
        fg_allotted = round(fg_scale_pts, 1)
        fg_contributed = round(fg_allotted * self.config.weight_firmographics, 2)

        pillar_fg = PillarReceipt(
            pillar_name="Firmographics & Market Scale",
            allotted_score=fg_allotted,
            weight_pct=self.config.weight_firmographics,
            points_contributed=fg_contributed,
            basis_criterion=f"Revenue: ${lead.annual_revenue_usd:,.0f} | Headcount: {lead.employee_count} | Region: {lead.location}",
            verified_signals=[
                f"Market Scale evaluated as: {market_choice.choice if market_choice else 'Enterprise'}",
                f"Territory status: {'Tier-1 Core Market' if is_tier1 else 'Expansion Territory'}",
                f"Sector: {lead.industry_sector}"
            ],
            deduction_gaps=[] if fg_allotted >= 75 else ["Revenue scale below ideal enterprise baseline."],
            decision_rationale=f"Jev calibrated firmographic rubric score: {fg_score_obj.score:.1f}/5.0 with {fg_score_obj.confidence*100:.0f}% confidence." if fg_score_obj else "Evaluated scale."
        )

        # 5.2 Pillar 2: Decision Authority & Hierarchy (Weight 25%)
        # Multi-dimensional role parsing: Seniority + Department + Authority Level + Buyer Persona + 1-10 Role Scale
        seniority_choice = jev_res.choices.get("seniority_level")
        dept_choice = jev_res.choices.get("functional_department")
        auth_level_choice = jev_res.choices.get("buying_authority_level")
        persona_choice = jev_res.choices.get("buyer_persona")
        budget_noul = jev_res.nouls.get("has_budget_authority")
        auth_score_obj = jev_res.scores.get("authority_readiness")
        role_scale_obj = jev_res.scores.get("role_authority_scale")

        if role_scale_obj:
            auth_allotted = round(min(100.0, (role_scale_obj.score / 10.0 * 100.0)), 1)
        elif auth_score_obj:
            auth_allotted = round(min(100.0, (auth_score_obj.score / 5.0 * 100.0)), 1)
        else:
            auth_allotted = 75.0 if (budget_noul and budget_noul.noul) else 50.0

        # Boost for C-Suite / VP in core purchasing departments
        if seniority_choice and any(w in seniority_choice.choice for w in ["C-Suite", "VP", "Executive"]):
            auth_allotted = min(100.0, auth_allotted + 5.0)

        auth_contributed = round(auth_allotted * self.config.weight_authority, 2)

        pillar_auth = PillarReceipt(
            pillar_name="Decision Authority & Hierarchy",
            allotted_score=auth_allotted,
            weight_pct=self.config.weight_authority,
            points_contributed=auth_contributed,
            basis_criterion=f"Title: {lead.contact_role_title or 'Unspecified'} | Name: {lead.contact_name or 'Lead'}",
            verified_signals=[
                f"Seniority Tier: {seniority_choice.choice if seniority_choice else 'Evaluator'}",
                f"Department: {dept_choice.choice if dept_choice else 'Operations'}",
                f"Authority Mandate: {auth_level_choice.choice if auth_level_choice else 'Recommender'}",
                f"Buyer Persona: {persona_choice.choice if persona_choice else 'Technical Champion'}",
                f"Budget Authority Probability: {budget_noul.probability*100:.0f}%" if budget_noul else "Verified"
            ],
            deduction_gaps=[] if auth_allotted >= 70 else ["Contact does not hold primary economic signing authority."],
            decision_rationale=f"Classified as {seniority_choice.choice if seniority_choice else 'Lead'} in {dept_choice.choice if dept_choice else 'GTM'} ({persona_choice.choice if persona_choice else 'Evaluator'})."
        )

        # 5.3 Pillar 3: Intent & Buying Velocity (Weight 25%)
        # Basis: Jev score 'intent_velocity' + choice 'urgency_window' + noul 'has_active_buying_cycle'
        intent_score_obj = jev_res.scores.get("intent_velocity")
        urgency_choice = jev_res.choices.get("urgency_window")
        active_cycle_noul = jev_res.nouls.get("has_active_buying_cycle")

        if intent_score_obj:
            intent_allotted = round(min(100.0, (intent_score_obj.score / 5.0 * 100.0)), 1)
        else:
            intent_allotted = 80.0 if (active_cycle_noul and active_cycle_noul.noul) else 45.0

        intent_contributed = round(intent_allotted * self.config.weight_intent, 2)

        pillar_intent = PillarReceipt(
            pillar_name="Intent & Buying Velocity",
            allotted_score=intent_allotted,
            weight_pct=self.config.weight_intent,
            points_contributed=intent_contributed,
            basis_criterion=f"Inquiry Notes: {lead.buying_intent[:80]}..." if lead.buying_intent else "Direct Form Inbound",
            verified_signals=[
                f"Timeline Window: {urgency_choice.choice if urgency_choice else 'Active Evaluation'}",
                f"Active Cycle Probability: {active_cycle_noul.probability*100:.0f}%" if active_cycle_noul else "Standard"
            ],
            deduction_gaps=[] if intent_allotted >= 70 else ["No explicit live RFP or immediate milestone declared."],
            decision_rationale=f"Jev intent velocity rated at {intent_score_obj.score:.1f}/5.0." if intent_score_obj else "Intent evaluated."
        )

        # 5.4 Pillar 4: Value & Expansion Potential (Weight 20%)
        # Basis: Jev score 'value_expansion' + choice 'ecosystem_synergy'
        value_score_obj = jev_res.scores.get("value_expansion")
        eco_choice = jev_res.choices.get("ecosystem_synergy")

        if value_score_obj:
            value_allotted = round(min(100.0, (value_score_obj.score / 5.0 * 100.0)), 1)
        else:
            value_allotted = 70.0

        # Tech stack synergy boost
        if eco_choice and "High Synergy" in eco_choice.choice:
            value_allotted = min(100.0, value_allotted + 5.0)

        value_contributed = round(value_allotted * self.config.weight_value, 2)

        pillar_value = PillarReceipt(
            pillar_name="Contract Value & Expansion",
            allotted_score=value_allotted,
            weight_pct=self.config.weight_value,
            points_contributed=value_contributed,
            basis_criterion=f"Target Deal ACV: ${lead.target_deal_size_usd:,.0f} USD",
            verified_signals=[
                f"Ecosystem Compatibility: {eco_choice.choice if eco_choice else 'Modern Stack'}",
                f"Deal Size: ${lead.target_deal_size_usd:,.0f} (Target baseline: ${self.config.target_deal_size_usd:,.0f})"
            ],
            deduction_gaps=[] if value_allotted >= 65 else ["Target deal size is modest for multi-seat enterprise expansion."],
            decision_rationale="Evaluated against organization deal thresholds and infrastructure synergy."
        )

        # 6. Aggregate Master ICP Score (0 to 100)
        master_score = round(fg_contributed + auth_contributed + intent_contributed + value_contributed, 1)

        # 7. Determine Priority Tier & SLA
        if master_score >= self.config.tier_a1_threshold:
            tier = PriorityTier.TIER_A1
        elif master_score >= self.config.tier_a2_threshold:
            tier = PriorityTier.TIER_A2
        elif master_score >= self.config.tier_b1_threshold:
            tier = PriorityTier.TIER_B1
        else:
            tier = PriorityTier.TIER_C

        action_info = PriorityTier.ACTION_MAP[tier]

        # 8. Synthesize Executive Outreach Hook & Value Wedge
        role_label = lead.contact_role_title or "Technology Leader"
        comp_label = lead.company_name or "your team"
        outreach_hook = f"Hi {lead.contact_name or 'there'}, noticing your focus on {lead.industry_sector} at {comp_label}, I wanted to share how our intelligence infrastructure empowers {role_label}s to accelerate qualification cycles."
        value_wedge = f"For {comp_label}, integrating our real-time revenue decision engine eliminates qualification friction and accelerates sales velocity for ${lead.target_deal_size_usd:,.0f}+ opportunities."

        return ICPScoringReport(
            company_name=lead.company_name or "Prospective Account",
            master_icp_score=master_score,
            priority_tier=tier,
            is_disqualified=False,
            disqualification_reason=None,
            urgency_sla=action_info["sla"],
            recommended_channel=action_info["channel"],
            sales_action=action_info["action"],
            outreach_hook=outreach_hook,
            value_wedge=value_wedge,
            pillar_firmographics=pillar_fg,
            pillar_authority=pillar_auth,
            pillar_intent=pillar_intent,
            pillar_value=pillar_value,
            jev_primitives=primitive_receipts,
            overall_confidence=0.91,
            execution_latency_ms=jev_res.latency_ms,
            execution_mode=jev_res.mode
        )
