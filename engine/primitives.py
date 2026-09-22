"""
Jev System One Decision Primitives: Noul (Bool), Choice, Score.
Comprehensive multi-dimensional taxonomy for B2B ICP revenue qualification.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

# Graceful import of typesafe_sdk primitives if available
try:
    from typesafe_sdk import Noul as SdkNoul, Choice as SdkChoice, Score as SdkScore
except ImportError:
    SdkNoul = None
    SdkChoice = None
    SdkScore = None


class JevPrimitiveDefinition(BaseModel):
    """Base schema for a Jev decision question."""
    type: str  # "noul" | "choice" | "score"
    instructions: str
    criteria: Optional[Union[List[str], Dict[str, Optional[str]]]] = None

    def to_sdk_or_dict(self) -> Any:
        """Converts definition to official typesafe_sdk object if installed, else self."""
        if self.type == "noul" and SdkNoul is not None:
            return SdkNoul(instructions=self.instructions)
        if self.type == "choice" and SdkChoice is not None:
            if isinstance(self.criteria, list):
                crit_dict = {str(opt): None for opt in self.criteria}
            elif isinstance(self.criteria, dict):
                crit_dict = self.criteria
            else:
                crit_dict = {}
            return SdkChoice(instructions=self.instructions, criteria=crit_dict)
        if self.type == "score" and SdkScore is not None:
            levels = list(self.criteria) if isinstance(self.criteria, (list, tuple)) else ["Low", "High"]
            return SdkScore(instructions=self.instructions, criteria=levels)
        return self


def create_noul_question(instructions: str) -> JevPrimitiveDefinition:
    """Creates a Noul (Boolean / yes-no probability) question."""
    return JevPrimitiveDefinition(type="noul", instructions=instructions)


def create_choice_question(
    instructions: str,
    options: Union[List[str], Dict[str, Optional[str]]]
) -> JevPrimitiveDefinition:
    """Creates a Choice (categorical classification with distribution) question."""
    return JevPrimitiveDefinition(type="choice", instructions=instructions, criteria=options)


def create_score_question(
    instructions: str,
    levels: List[str]
) -> JevPrimitiveDefinition:
    """Creates a Score (calibrated rubric scale) question."""
    return JevPrimitiveDefinition(type="score", instructions=instructions, criteria=levels)


# ==============================================================================
# Comprehensive B2B ICP Question Suites
# ==============================================================================

ICP_NOUL_QUESTIONS: Dict[str, JevPrimitiveDefinition] = {
    "is_anti_icp": create_noul_question(
        "Is this lead a student, personal inquiry, freemail spam, non-commercial account, or otherwise invalid for B2B commercial sales?"
    ),
    "is_student_or_intern": create_noul_question(
        "Is the contact an undergraduate, graduate student, academic researcher, unpaid intern, or testing from an educational institution?"
    ),
    "is_jobseeker_or_recruiter": create_noul_question(
        "Is the contact a job applicant, external recruiter, headhunter, or pitching employment/resumes rather than software procurement?"
    ),
    "is_sanctioned_region": create_noul_question(
        "Is this company or inquiry located in an internationally prohibited, sanctioned, or restricted territory (e.g. North Korea, Iran, Syria, Russia, Belarus)?"
    ),
    "is_executive_decision_maker": create_noul_question(
        "Does the contact hold executive or department leadership status with direct influence over organizational vendor selection?"
    ),
    "has_budget_authority": create_noul_question(
        "Does the contact hold executive or budgetary signing authority for enterprise software procurement?"
    ),
    "has_active_buying_cycle": create_noul_question(
        "Is the account currently running an active evaluation, formal RFP, migration initiative, or high-urgency timeline (<90 days)?"
    )
}

ICP_CHOICE_QUESTIONS: Dict[str, JevPrimitiveDefinition] = {
    # 1. Granular Seniority Hierarchy
    "seniority_level": create_choice_question(
        "What is the contact's exact seniority level within the corporate hierarchy?",
        [
            "C-Suite / Founder / Board (+5 pts)",
            "VP / Executive Leadership (+4 pts)",
            "Director / Practice Head (+3 pts)",
            "Manager / Team Lead (+2 pts)",
            "Staff / Principal / Lead Specialist (+2 pts)",
            "Senior Individual Contributor (+1 pt)",
            "Junior / Entry Associate (+1 pt)",
            "Academic / Intern / Student (0 pts)"
        ]
    ),
    # 2. Functional Department / Business Unit
    "functional_department": create_choice_question(
        "Which functional department or business unit does this contact belong to?",
        [
            "Engineering, IT & Cloud Infrastructure",
            "Revenue Operations, Sales & GTM",
            "Procurement, Sourcing & Vendor Management",
            "Finance, Accounting & Treasury",
            "Product Management & Strategy",
            "Marketing & Growth Demand Gen",
            "Legal, Risk, Security & Compliance",
            "General Operations & Administration",
            "Academic / Student / Non-Commercial"
        ]
    ),
    # 3. Purchasing & Budget Authority Level
    "buying_authority_level": create_choice_question(
        "What is the contact's procurement and budgetary signing authority?",
        [
            "Sole Budget Sign-Off Authority ($50k+ Mandate)",
            "Committee Co-Signer / Business Sponsor ($25k - $50k)",
            "Technical Approver / Gatekeeper (Architecture Veto)",
            "Evaluation Lead / Recommender (No Signing Power)",
            "Operational End-User Practitioner",
            "Non-Buyer / Student / Intern"
        ]
    ),
    # 4. Buyer Persona Type
    "buyer_persona": create_choice_question(
        "Which buyer persona category best describes this contact's relationship to the purchase?",
        [
            "Economic Buyer (Signs the contract & owns the P&L)",
            "Technical Champion (Evaluates architecture, security & APIs)",
            "Business Champion (Drives internal use case & business value)",
            "Procurement / Sourcing Gatekeeper (Negotiates commercial terms)",
            "End User / Operational Specialist (Daily workflow practitioner)",
            "Non-Buyer / Academic"
        ]
    ),
    # 5. Market Complexity & Enterprise Scale
    "market_complexity": create_choice_question(
        "What is the scale and operational complexity of this enterprise?",
        [
            "Global Multi-National Enterprise (Tier 1)",
            "Specialized Enterprise / Strategic National",
            "Mid-Market Scale & Fast-Growth",
            "SMB / Boutique / Regional"
        ]
    ),
    # 6. Ecosystem & Tech Stack Synergy
    "ecosystem_synergy": create_choice_question(
        "How well does their stated or inferred tech stack integrate with modern cloud data platforms?",
        [
            "High Synergy (Modern Cloud: AWS/Snowflake/Databricks/Salesforce)",
            "Standard Modern SaaS Ecosystem",
            "Neutral / Unspecified Stack",
            "Legacy Monolith Blocker (AS400, on-prem silo)"
        ]
    ),
    # 7. Procurement & Deployment Urgency
    "urgency_window": create_choice_question(
        "What is the estimated procurement and deployment timeline?",
        [
            "Immediate Urgency (<30 Days / Live RFP)",
            "Active Project (1 to 3 Months)",
            "Mid-Term Planning (3 to 6 Months)",
            "Exploratory / Educational (>6 Months)"
        ]
    )
}

ICP_SCORE_QUESTIONS: Dict[str, JevPrimitiveDefinition] = {
    # Continuous 1 to 10 Role Authority & Organizational Leverage Rubric
    "role_authority_scale": create_score_question(
        "Rate the contact's organizational authority, span of control, and deal purchasing leverage on a 1-10 scale:",
        [
            "Level 1: Entry / Junior IC (No signing or evaluation authority)",
            "Level 2: Mid-Level IC / Specialist (Daily operational workflow user)",
            "Level 3: Senior IC / Specialist (Internal evaluator / product recommender)",
            "Level 4: Team Lead / First-Line Manager (Evaluates solutions for small team)",
            "Level 5: Department Manager / Lead Architect (Technical/functional evaluation leader)",
            "Level 6: Senior Manager / Principal Lead (Owns project execution & vendor shortlist)",
            "Level 7: Director / Practice Head (Owns departmental budget & business sponsorship)",
            "Level 8: Senior Director / AVP (Key purchasing influencer & committee co-signer)",
            "Level 9: Vice President / Global Head (Direct P&L and signing mandate for enterprise deals)",
            "Level 10: C-Suite / Founder / Board (Final executive signing authority for the enterprise)"
        ]
    ),
    "firmographic_fit": create_score_question(
        "Rate the prospect's company size, revenue scale, and industry alignment on this scale:",
        [
            "Sub-Scale / Unqualified (<$5M ARR or misaligned industry)",
            "Emerging Scale ($5M - $20M ARR, regional presence)",
            "Core Mid-Market ($20M - $100M ARR, established operations)",
            "Tier-1 Enterprise Leader (>$100M ARR, multi-region footprint)"
        ]
    ),
    "intent_velocity": create_score_question(
        "Rate the prospect's buying urgency, active RFP signals, and evaluation velocity:",
        [
            "Passive / Browsing (No explicit business driver)",
            "Early Stage Research (Benchmarking market solutions)",
            "Active Buying Motion (Defined initiative and budget window)",
            "High-Velocity Mandate (Live RFP, executive sponsorship, urgent milestone)"
        ]
    ),
    "authority_readiness": create_score_question(
        "Rate the procurement readiness and authority of the involved stakeholders:",
        [
            "No Authority (Individual Contributor or non-decision maker)",
            "Influencer (Manager/Senior IC evaluating on behalf of team)",
            "Key Champion (Director with direct ear of budget owner)",
            "Budget Signer (VP / C-Suite with direct signing mandate)"
        ]
    ),
    "value_expansion": create_score_question(
        "Rate the prospective lifetime contract value and multi-seat expansion potential:",
        [
            "Low Contract Value (<$10k ACV, single-seat use case)",
            "Standard Contract Value ($10k - $35k ACV)",
            "High Contract Value ($35k - $100k ACV, multi-team deployment)",
            "Strategic Enterprise Value (>$100k ACV, cross-department expansion)"
        ]
    )
}


def build_lead_state(
    company_name: str,
    industry: str,
    annual_revenue_usd: float,
    headcount: int,
    location: str,
    contact_name: str,
    contact_role: str,
    email: str,
    buying_intent: str,
    target_deal_size_usd: float,
    tech_stack: str = "",
    branches: Optional[List[str]] = None,
    raw_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs a unified, rich state dictionary to feed into Jev System One.
    """
    branch_str = ", ".join(branches) if branches else "None specified"
    state = {
        "company_name": company_name or "Unknown Company",
        "industry_sector": industry or "General B2B",
        "annual_revenue_usd": float(annual_revenue_usd),
        "employee_count": int(headcount),
        "primary_location": location or "Unknown",
        "branch_locations": branch_str,
        "contact_name": contact_name or "Unknown Contact",
        "contact_role_title": contact_role or "Unknown Role",
        "contact_email": email or "",
        "target_deal_size_usd": float(target_deal_size_usd),
        "buying_intent_notes": buying_intent or "No specific notes",
        "tech_stack_infrastructure": tech_stack or "Not specified",
        "lead_document": (
            f"Company: {company_name}\n"
            f"Industry: {industry}\n"
            f"Revenue: ${annual_revenue_usd:,.0f} USD | Headcount: {headcount}\n"
            f"Location: {location} (Branches: {branch_str})\n"
            f"Contact: {contact_name} ({contact_role}) <{email}>\n"
            f"Deal Target: ${target_deal_size_usd:,.0f} USD\n"
            f"Intent & Initiatives: {buying_intent}\n"
            f"Tech Stack: {tech_stack}\n"
            f"{('Raw Prospect Notes: ' + raw_text) if raw_text else ''}"
        )
    }
    return state
