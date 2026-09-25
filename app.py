"""
Enterprise ICP Revenue Intelligence Studio (v3.4)
High-Velocity AI Lead Qualifier & Dynamic Company Standards Studio.
100% Pure Python • Deterministic {-5 to +5} Scoring • AI Text Field Intelligence.
"""

import streamlit as st
import json
import os
import html
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from engine.gtm_engine import (
        CompanyStandardsConfig,
        StreamlinedLeadForm,
        GTMScoringEngine,
        StreamlinedScoringResult,
        ScoringTrackerItem
    )
except (ImportError, ModuleNotFoundError):
    sys.path.insert(0, str(ROOT_DIR / "engine"))
    from gtm_engine import (
        CompanyStandardsConfig,
        StreamlinedLeadForm,
        GTMScoringEngine,
        StreamlinedScoringResult,
        ScoringTrackerItem
    )

# HTML Sanitizer Helper (Defined globally at top of module)
def esc(val: Any) -> str:
    if val is None:
        return ""
    return html.escape(str(val))


# Page Configuration
st.set_page_config(
    page_title="Enterprise ICP Revenue Intelligence Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional RevOps UI Styling with High Visual Hierarchy
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, label {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1380px;
    }

    /* Hero Header */
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #0F172A 0%, #4338CA 50%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        line-height: 1.25;
    }

    .hero-subtitle {
        color: #475569 !important;
        font-size: 0.88rem;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }

    .pill-badge-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 6px;
    }

    .hero-pill {
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .hero-pill-ai {
        background: #EEF2FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
    }

    /* Status Bar Styling */
    .status-bar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        font-size: 0.88rem;
        color: #334155;
        padding: 2px 4px;
    }

    .status-bar-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .status-pill {
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: 700;
        color: #0F172A;
        font-size: 0.82rem;
    }

    /* Field Labels - Clean spacing & readable typography */
    label[data-testid="stWidgetLabel"] {
        margin-bottom: 4px !important;
        display: flex !important;
        align-items: center !important;
    }

    label[data-testid="stWidgetLabel"] p {
        font-size: 0.83rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        letter-spacing: 0.1px;
        margin: 0 !important;
        line-height: 1.3 !important;
    }

    /* Form Container Card Headers */
    .form-card-header {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0F172A !important;
        background: #F8FAFC;
        padding: 10px 14px;
        border-radius: 8px;
        border-left: 4px solid #4F46E5;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .form-card-header span.tag {
        font-size: 0.72rem;
        font-weight: 700;
        background: #EEF2FF;
        color: #4F46E5;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #C7D2FE;
        text-transform: uppercase;
    }

    /* Section Card Header in Settings Dialog */
    .settings-section-title {
        font-size: 0.92rem;
        font-weight: 800;
        color: #1E293B !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 6px;
        margin-top: 2px;
        margin-bottom: 12px;
    }

    /* Sleek Output Cards */
    .master-score-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 60%, #311042 100%);
        border: 1px solid rgba(167, 139, 250, 0.35);
        border-radius: 16px;
        padding: 26px 30px;
        color: #FFFFFF !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4), 0 8px 10px -6px rgba(15, 23, 42, 0.4);
        margin-bottom: 22px;
    }

    .ai-feature-card {
        background: linear-gradient(145deg, #0F172A 0%, #1E1B4B 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 14px;
        padding: 20px;
        color: #F8FAFC !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .ai-feature-card:hover {
        border-color: rgba(167, 139, 250, 0.6);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.25);
    }

    .metric-pillar-card {
        background: linear-gradient(145deg, #0F172A 0%, #1A2238 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 20px;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.18);
    }

    .action-routing-card {
        background: linear-gradient(135deg, #1E1B4B 0%, #2E1065 50%, #4C0519 100%);
        border: 1px solid rgba(244, 114, 182, 0.4);
        border-radius: 16px;
        padding: 24px 28px;
        color: #FFFFFF !important;
        box-shadow: 0 8px 24px rgba(236, 72, 153, 0.18);
        margin-top: 18px;
        margin-bottom: 22px;
    }

    /* Badges */
    .badge-a1 {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.35);
    }

    .badge-a2 {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #FFFFFF !important;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
    }

    .badge-b1 {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #FFFFFF !important;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.35);
    }

    .badge-disq {
        background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
        color: #FFFFFF !important;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.35);
    }

    .tag-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    .tag-purple {
        background: rgba(167, 139, 250, 0.2);
        color: #C4B5FD !important;
        border: 1px solid rgba(167, 139, 250, 0.4);
    }

    .tag-cyan {
        background: rgba(56, 189, 248, 0.2);
        color: #7DD3FC !important;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }

    .tag-emerald {
        background: rgba(52, 211, 153, 0.2);
        color: #6EE7B7 !important;
        border: 1px solid rgba(52, 211, 153, 0.4);
    }

    .tag-amber {
        background: rgba(251, 191, 36, 0.2);
        color: #FDE68A !important;
        border: 1px solid rgba(251, 191, 36, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "company_config" not in st.session_state:
    st.session_state["company_config"] = CompanyStandardsConfig(
        company_name="Blackridge Research & Consulting",
        min_deal_size_usd=5000.0,
        target_deal_size_usd=25000.0,
        min_company_revenue_usd=5000000.0,
        ideal_revenue_usd=50000000.0,
        min_headcount=20,
        ideal_headcount=500,
        target_focus_industries=[
            "Energy, Utilities & Renewables",
            "Infrastructure & Construction",
            "Oil, Gas & Petrochemicals",
            "Industrial Goods & Manufacturing",
            "Automotive & Electric Mobility",
            "Chemicals & Materials",
            "Technology & Telecom"
        ],
        tier1_territories=[
            "United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "India", "Australia", "Singapore", "United Arab Emirates", "Saudi Arabia"
        ],
        prohibited_countries=[
            "North Korea", "Iran", "Syria", "Cuba", "Russia", "Belarus"
        ]
    )

cfg: CompanyStandardsConfig = st.session_state["company_config"]


# ==============================================================================
# SETTINGS MODAL DIALOG (UNIFORMLY ALIGNED & PROFESSIONAL)
# ==============================================================================
@st.dialog("⚙️ Company ICP Standards & Target Rules", width="medium")
def show_settings_dialog():
    st.caption("Configure company identifier, focus target industries, and geographic territory rules:")

    with st.form("modal_company_standards_form"):
        with st.container(border=True):
            s_name = st.text_input("Company / Org Identifier", value=cfg.company_name)
            
            s_focus_ind_raw = st.text_input(
                "Sweet-Spot Focus Industries (+5 Pts Bonus)",
                value=", ".join(cfg.target_focus_industries) if cfg.target_focus_industries else "Technology, SaaS & IT, Manufacturing & Industrial Goods, Energy, Utilities & Renewables"
            )
            s_focus_ind = [i.strip() for i in s_focus_ind_raw.split(",") if i.strip()]

            s_t1_geo = st.text_input(
                "Tier 1 Supported Territories",
                value=", ".join(cfg.tier1_territories)
            )
            s_proh_geo = st.text_input(
                "Sanctioned / Prohibited Territories (Hard Disqualification)",
                value=", ".join(cfg.prohibited_countries)
            )

            s_api_key = st.text_input(
                "🔑 Jev / TypeSafe API Key (Session Override)",
                value=st.session_state.get("user_jev_api_key", ""),
                type="password",
                help="Enter your JEV_API_KEY here to activate live AI scoring directly in this session."
            )

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        save_btn = st.form_submit_button("💾 Save Settings", type="primary", use_container_width=True)

    if save_btn:
        if s_api_key.strip():
            st.session_state["user_jev_api_key"] = s_api_key.strip()
        new_cfg = CompanyStandardsConfig(
            company_name=s_name,
            min_deal_size_usd=cfg.min_deal_size_usd,
            target_deal_size_usd=cfg.target_deal_size_usd,
            min_company_revenue_usd=cfg.min_company_revenue_usd,
            ideal_revenue_usd=cfg.ideal_revenue_usd,
            min_headcount=cfg.min_headcount,
            ideal_headcount=cfg.ideal_headcount,
            target_focus_industries=s_focus_ind,
            tier1_territories=[t.strip() for t in s_t1_geo.split(",") if t.strip()],
            prohibited_countries=[p.strip() for p in s_proh_geo.split(",") if p.strip()],
            weight_firmographics=cfg.weight_firmographics,
            weight_authority=cfg.weight_authority,
            weight_intent=cfg.weight_intent,
            weight_value=cfg.weight_value,
            tier_a1_threshold=cfg.tier_a1_threshold,
            tier_a2_threshold=cfg.tier_a2_threshold,
            tier_b1_threshold=cfg.tier_b1_threshold
        )
        st.session_state["company_config"] = new_cfg
        st.rerun()


# Currency Configuration Map
CURRENCY_OPTIONS = {
    "USD ($)": "$",
    "INR (₹)": "₹",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "CAD (C$)": "C$",
    "AUD (A$)": "A$",
    "AED (AED)": "AED ",
    "SGD (S$)": "S$",
    "JPY (¥)": "¥"
}

# Metric Scale Multipliers (Global & Regional)
SCALE_UNITS = {
    "Millions (M)": 1_000_000,
    "Crores (Cr)": 10_000_000,
    "Billions (B)": 1_000_000_000,
    "Lakhs (L)": 100_000,
    "Thousands (k)": 1_000,
    "Exact / Standard": 1
}

if "selected_curr" not in st.session_state:
    st.session_state["selected_curr"] = "USD ($)"

curr_label = st.session_state["selected_curr"]
curr_sym = CURRENCY_OPTIONS.get(curr_label, "$")
curr_code = curr_label.split()[0]

# ==============================================================================
# HERO HEADER BAR & CONTROLS
# ==============================================================================
head_col1, head_col2 = st.columns([5.5, 2.3])

with head_col1:
    st.markdown("""
    <div>
        <div class="hero-title">⚡ Enterprise ICP Revenue Intelligence Studio</div>
        <div class="hero-subtitle">High-Velocity Lead Qualification • AI Semantic Analysis • Deterministic GTM Scoring Engine</div>
        <div class="pill-badge-row">
            <span class="hero-pill hero-pill-ai">🤖 AI Persona Classifier</span>
            <span class="hero-pill hero-pill-ai">⚡ AI Timeline Signal</span>
            <span class="hero-pill">⚖️ 4-Pillar Weighted Score</span>
            <span class="hero-pill">🎯 Dynamic Org Thresholds</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    c_cur, c_sett = st.columns([1.1, 1])
    with c_cur:
        selected_curr = st.selectbox(
            "Currency",
            options=list(CURRENCY_OPTIONS.keys()),
            index=list(CURRENCY_OPTIONS.keys()).index(st.session_state["selected_curr"]),
            label_visibility="collapsed",
            help="Select reporting and evaluation currency"
        )
        if selected_curr != st.session_state["selected_curr"]:
            st.session_state["selected_curr"] = selected_curr
            st.rerun()
    with c_sett:
        if st.button("⚙️ Settings", use_container_width=True, help="Configure company standards, margins, and weights"):
            show_settings_dialog()

# Clean Status Indicator Bar
st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown(f"""
    <div class="status-bar-container">
        <div class="status-bar-item">
            <span>🏢</span>
            <span>Standards Org: <strong class="status-pill">{esc(cfg.company_name)}</strong></span>
        </div>
        <div class="status-bar-item">
            <span>🎯</span>
            <span>Target Verticals: <strong class="status-pill">{len(cfg.target_focus_industries)} Focus Sectors</strong></span>
        </div>
        <div class="status-bar-item">
            <span>💱</span>
            <span>Currency: <strong class="status-pill">{esc(curr_label)}</strong></span>
            <span style="color:#CBD5E1;">&bull;</span>
            <span style="color:#059669; font-weight:700;">🤖 AI Engine Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# MAIN LEAD QUALIFICATION FORM (CLEAN, BOLD HEADINGS, NO PLACEHOLDER DATA)
# ==============================================================================
with st.form("lead_qualification_form"):
    col_f1, col_f2 = st.columns(2, gap="large")

    with col_f1:
        with st.container(border=True):
            st.markdown("""
            <div class="form-card-header">
                <span>🏢 1. Account Scale & Firmographics</span>
                <span class="tag">Firmographic Pillar</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Row 1: Company Name & Headquarters
            c1_r1_a, c1_r1_b = st.columns(2)
            with c1_r1_a:
                f_company = st.text_input("Company Name", value=st.session_state.get("f_company", ""))
            with c1_r1_b:
                f_loc = st.text_input("Headquarters", value=st.session_state.get("f_loc", ""))

            # Row 2: Industry & Headcount
            c1_r2_a, c1_r2_b = st.columns(2)
            with c1_r2_a:
                f_ind = st.text_input("Industry", value=st.session_state.get("f_ind", ""))
            with c1_r2_b:
                f_hc = st.number_input(
                    "Headcount",
                    min_value=0,
                    max_value=10_000_000,
                    value=max(0, int(st.session_state.get("f_hc", 0))),
                    step=25,
                    format="%d",
                    help="Employee headcount"
                )

            # Row 3: Annual Revenue & Revenue Currency
            c1_r3_a, c1_r3_b = st.columns(2)
            with c1_r3_a:
                f_rev_val = st.number_input(
                    "Annual Revenue",
                    min_value=0.0,
                    max_value=100_000_000_000.0,
                    value=float(st.session_state.get("f_rev_val", 0.0)),
                    step=1.0,
                    format="%.2f",
                    help="Revenue amount in selected unit"
                )
            with c1_r3_b:
                f_rev_curr = st.selectbox(
                    "Revenue Currency",
                    list(CURRENCY_OPTIONS.keys()),
                    index=list(CURRENCY_OPTIONS.keys()).index(st.session_state.get("f_rev_curr", curr_label))
                )

            # Row 4: Revenue Scale Unit
            c1_r4_a, _ = st.columns(2)
            with c1_r4_a:
                f_rev_unit = st.selectbox(
                    "Revenue Scale Unit",
                    list(SCALE_UNITS.keys()),
                    index=list(SCALE_UNITS.keys()).index(st.session_state.get("f_rev_unit", "Millions (M)"))
                )

            rev_mult = SCALE_UNITS.get(f_rev_unit, 1)
            f_rev_total = float(f_rev_val) * rev_mult
            rev_sym = CURRENCY_OPTIONS.get(f_rev_curr, "$")
            rev_code = f_rev_curr.split()[0]
            
            if f_rev_val > 0:
                if f_rev_unit != "Exact / Standard":
                    rev_stated_str = f"{rev_sym}{f_rev_val:g} {f_rev_unit} ({rev_sym}{f_rev_total:,.0f} {rev_code})"
                else:
                    rev_stated_str = f"{rev_sym}{f_rev_total:,.0f} {rev_code}"
            else:
                rev_stated_str = f"{rev_sym}0 {rev_code}"

    with col_f2:
        with st.container(border=True):
            st.markdown("""
            <div class="form-card-header">
                <span>👤 2. Decision Authority, Intent & Commercials</span>
                <span class="tag">AI Signal Engine</span>
            </div>
            """, unsafe_allow_html=True)

            # Row 1: Contact Name & Role Title
            c2_r1_a, c2_r1_b = st.columns(2)
            with c2_r1_a:
                f_name = st.text_input("Contact Name", value=st.session_state.get("f_name", ""))
            with c2_r1_b:
                f_role = st.text_input("Role Title", value=st.session_state.get("f_role", ""))

            # Row 2: Buying Role & Timeline (Manual Text Entry)
            c2_r2_a, c2_r2_b = st.columns(2)
            with c2_r2_a:
                f_buying_role = st.text_input(
                    "Buying Role",
                    value=st.session_state.get("f_buying_role", "")
                )
            with c2_r2_b:
                f_timeline = st.text_input(
                    "Timeline",
                    value=st.session_state.get("f_timeline", "")
                )

            # Row 3: Buying Intent & Uses Existing Platform (Optional)
            c2_r3_a, c2_r3_b = st.columns(2)
            with c2_r3_a:
                f_intent = st.text_input("Buying Intent", value=st.session_state.get("f_intent", ""))
            with c2_r3_b:
                f_platform = st.text_input(
                    "Uses Existing Platform",
                    value=st.session_state.get("f_platform", ""),
                    help="Optional: whether the prospect uses an incumbent or existing tool"
                )

            # Row 4: Budget Range & Budget Currency
            c2_r4_a, c2_r4_b = st.columns(2)
            with c2_r4_a:
                f_deal_val = st.number_input(
                    "Budget Range",
                    min_value=0.0,
                    max_value=1_000_000_000.0,
                    value=float(st.session_state.get("f_deal_val", 0.0)),
                    step=1.0,
                    format="%.2f",
                    help="Allocated budget / contract size"
                )
            with c2_r4_b:
                f_deal_curr = st.selectbox(
                    "Budget Currency",
                    list(CURRENCY_OPTIONS.keys()),
                    index=list(CURRENCY_OPTIONS.keys()).index(st.session_state.get("f_deal_curr", curr_label))
                )

            # Row 5: Budget Scale Unit
            c2_r5_a, _ = st.columns(2)
            with c2_r5_a:
                f_deal_unit = st.selectbox(
                    "Budget Scale Unit",
                    list(SCALE_UNITS.keys()),
                    index=list(SCALE_UNITS.keys()).index(st.session_state.get("f_deal_unit", "Thousands (k)"))
                )

            deal_mult = SCALE_UNITS.get(f_deal_unit, 1)
            f_deal_total = float(f_deal_val) * deal_mult
            deal_sym = CURRENCY_OPTIONS.get(f_deal_curr, "$")
            deal_code = f_deal_curr.split()[0]
            
            if f_deal_val > 0:
                if f_deal_unit != "Exact / Standard":
                    deal_stated_str = f"{deal_sym}{f_deal_val:g} {f_deal_unit} ({deal_sym}{f_deal_total:,.0f} {deal_code})"
                else:
                    deal_stated_str = f"{deal_sym}{f_deal_total:,.0f} {deal_code}"
            else:
                deal_stated_str = f"{deal_sym}0 {deal_code}"

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2, _ = st.columns([2, 1, 3])
    with c_btn1:
        calc_btn = st.form_submit_button("🚀 Run AI Analysis & Qualify Lead", type="primary", use_container_width=True)
    with c_btn2:
        clear_btn = st.form_submit_button("🔄 Reset Form", use_container_width=True)

if clear_btn:
    st.session_state["f_company"] = ""
    st.session_state["f_loc"] = ""
    st.session_state["f_ind"] = ""
    st.session_state["f_rev_val"] = 0.0
    st.session_state["f_rev_unit"] = "Millions (M)"
    st.session_state["f_deal_val"] = 0.0
    st.session_state["f_deal_unit"] = "Thousands (k)"
    st.session_state["f_hc"] = 0
    st.session_state["f_name"] = ""
    st.session_state["f_role"] = ""
    st.session_state["f_buying_role"] = ""
    st.session_state["f_timeline"] = ""
    st.session_state["f_intent"] = ""
    st.session_state["f_platform"] = ""
    if "streamlined_res" in st.session_state:
        del st.session_state["streamlined_res"]
    st.rerun()

# Process Form Evaluation
if calc_btn:
    if not f_company.strip():
        st.warning("⚠️ Please provide a Company Name to qualify the account.")
    else:
        st.session_state["f_company"] = f_company
        st.session_state["f_loc"] = f_loc
        st.session_state["f_ind"] = f_ind
        st.session_state["f_rev_val"] = f_rev_val
        st.session_state["f_rev_curr"] = f_rev_curr
        st.session_state["f_rev_unit"] = f_rev_unit
        st.session_state["f_deal_val"] = f_deal_val
        st.session_state["f_deal_curr"] = f_deal_curr
        st.session_state["f_deal_unit"] = f_deal_unit
        st.session_state["f_hc"] = f_hc
        st.session_state["f_name"] = f_name
        st.session_state["f_role"] = f_role
        st.session_state["f_buying_role"] = f_buying_role
        st.session_state["f_timeline"] = f_timeline
        st.session_state["f_intent"] = f_intent
        st.session_state["f_platform"] = f_platform

        submission = StreamlinedLeadForm(
            company_name=f_company.strip(),
            currency_symbol=rev_sym,
            currency_code=rev_code,
            revenue_entered_value=float(f_rev_val),
            revenue_unit=f_rev_unit,
            revenue_display_str=rev_stated_str,
            deal_entered_value=float(f_deal_val),
            deal_unit=f_deal_unit,
            deal_display_str=deal_stated_str,
            industry_sector=f_ind.strip(),
            sub_vertical=f_ind.strip(),
            annual_revenue_usd=float(f_rev_total),
            employee_count=int(f_hc),
            location=f_loc.strip(),
            branch_locations=[],
            contact_name=f_name.strip(),
            contact_email="",
            contact_role_title=f_role.strip(),
            buying_role=f_buying_role.strip(),
            buying_intent=f_intent.strip(),
            timeline=f_timeline.strip(),
            target_deal_size_usd=float(f_deal_total),
            tech_stack_notes=f_platform.strip(),
            uses_existing_platform=f_platform.strip(),
            existing_platform=f_platform.strip()
        )
        st.session_state["last_lead_submission"] = submission
        with st.spinner("🤖 Evaluating prospect across GTM 4-Pillar ICP standards..."):
            res: StreamlinedScoringResult = GTMScoringEngine.evaluate(submission, cfg)
        st.session_state["streamlined_res"] = res
        st.rerun()





# ==============================================================================
# OUTPUT: SLEEK CARD INTELLIGENCE SUITE
# ==============================================================================
if "streamlined_res" in st.session_state:
    st.markdown("---")
    res: StreamlinedScoringResult = st.session_state["streamlined_res"]

    # Handle Fail-Loud AI Error Mode
    if getattr(res, "analysis_mode", "live") == "failed":
        st.error(f"⚠️ **Jev AI Engine Unreachable**: {esc(res.disqualification_reason)}")
        
        with st.container(border=True):
            st.markdown("### 🔑 Enter Jev API Key to Activate Scoring")
            st.markdown(
                "You can paste your **JEV_API_KEY** directly below for this session, or configure it permanently in "
                "**Streamlit Cloud Secrets** (`Manage app ➔ Settings ➔ Secrets` as `JEV_API_KEY = \"your_api_key\"`)."
            )
            with st.form("quick_key_entry_form"):
                quick_key_input = st.text_input(
                    "Jev / TypeSafe API Key",
                    type="password",
                    placeholder="Enter or paste your Jev API Key here...",
                    help="Your key is stored securely in this session."
                )
                q_col1, _ = st.columns([2, 3])
                with q_col1:
                    save_q_key = st.form_submit_button("⚡ Save Key & Qualify Lead", type="primary", use_container_width=True)

                if save_q_key and quick_key_input.strip():
                    st.session_state["user_jev_api_key"] = quick_key_input.strip()
                    if "last_lead_submission" in st.session_state:
                        with st.spinner("🤖 Running Jev AI System-1 Evaluation..."):
                            re_res = GTMScoringEngine.evaluate(st.session_state["last_lead_submission"], cfg)
                            st.session_state["streamlined_res"] = re_res
                    st.rerun()
    else:
        badge_class = "badge-disq" if res.is_disqualified else ("badge-a1" if "A1" in res.priority_tier else ("badge-a2" if "A2" in res.priority_tier else "badge-b1"))
        fit_color = "#EF4444" if res.is_disqualified else ("#10B981" if res.master_icp_score >= 70 else ("#3B82F6" if res.master_icp_score >= 55 else "#F59E0B"))

        branch_badge = f"<span>&bull;</span><span>Branches: <strong style='color:#38BDF8;'>{len(res.lead_summary.get('branches', []))} Locations</strong></span>" if res.lead_summary.get('branches') else ""

        # 1. Master Score Obsidian Banner
        st.markdown(f"""<div class="master-score-card">
<div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
<div>
<div style="font-size:0.80rem; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
GTM Revenue Intelligence Report &bull; {esc(cfg.company_name)}
</div>
<div style="font-size:1.9rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px; margin-bottom:6px;">
{esc(res.company_name) or 'Unspecified Account'}
</div>
<div style="display:flex; align-items:center; gap:14px; font-size:0.92rem; color:#CBD5E1; flex-wrap:wrap;">
<span>Industry: <strong style="color:#FFFFFF;">{esc(res.lead_summary.get('industry', 'N/A'))}</strong></span>
<span>&bull;</span>
<span>HQ: <strong style="color:#FFFFFF;">{esc(res.lead_summary.get('location') or 'Global')}</strong></span>
{branch_badge}
<span>&bull;</span>
<span>SLA: <strong style="color:#38BDF8;">{esc(res.urgency_sla)}</strong></span>
</div>
</div>
<div style="text-align:right;">
<div style="font-size:0.78rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:4px;">
Master ICP Score
</div>
<div style="font-size:2.8rem; font-weight:800; color:{fit_color}; line-height:1; letter-spacing:-1px; margin-bottom:8px;">
{res.master_icp_score:.1f}<span style="font-size:1.2rem; color:#94A3B8; font-weight:500;">/100</span>
</div>
<div>
<span class="{badge_class}">{esc(res.priority_tier)}</span>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        if res.is_disqualified:
            st.error(f"❌ **Hard Disqualification Detected**: {esc(res.disqualification_reason)}")

        # 2. 🤖 AI Semantic Strategic Intelligence Grid (GTM Partners Taxonomy)
        if not res.is_disqualified:
            st.markdown("<h4 style='color:#0F172A; font-weight:700; margin-bottom:12px;'>🤖 AI Strategic Intelligence & GTM Readiness</h4>", unsafe_allow_html=True)
            ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)

            with ai_col1:
                market_str = res.ai_niche.market_complexity if res.ai_niche else "Established Market"
                niche_rat = res.ai_niche.rationale if res.ai_niche else ""
                reach_str = res.ai_footprint.geographic_reach if res.ai_footprint else "Single Market"
                st.markdown(f"""<div class="ai-feature-card">
<div>
<div style="font-size:0.75rem; font-weight:700; color:#38BDF8; text-transform:uppercase; letter-spacing:0.8px;">
🏢 1. Firmographics
</div>
<div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:6px; line-height:1.3;">
{esc(market_str)}
</div>
<div style="margin-top:8px; display:flex; gap:6px; flex-wrap:wrap;">
<span class="tag-chip tag-cyan">{esc(res.lead_summary.get('industry', 'General'))}</span>
<span class="tag-chip tag-emerald">{esc(reach_str)}</span>
</div>
</div>
<div style="margin-top:14px; font-size:0.82rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
<div style="font-style:italic; color:#7DD3FC;">"{esc(niche_rat)}"</div>
</div>
</div>""", unsafe_allow_html=True)

            with ai_col2:
                fit_str = res.ai_tech.ecosystem_fit if res.ai_tech else "Standard Fit"
                tech_rat = res.ai_tech.rationale if res.ai_tech else ""
                st.markdown(f"""<div class="ai-feature-card">
<div>
<div style="font-size:0.75rem; font-weight:700; color:#34D399; text-transform:uppercase; letter-spacing:0.8px;">
💻 2. Technographics
</div>
<div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:6px; line-height:1.3;">
{esc(fit_str)}
</div>
<div style="margin-top:8px;">
<span class="tag-chip tag-emerald">Ecosystem Fit</span>
</div>
</div>
<div style="margin-top:14px; font-size:0.82rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
<div style="font-style:italic; color:#6EE7B7;">"{esc(tech_rat)}"</div>
</div>
</div>""", unsafe_allow_html=True)

            with ai_col3:
                persona_str = res.ai_role.persona_type if res.ai_role else "End User"
                sen_str = res.ai_role.seniority_level if res.ai_role else "Standard"
                dept_str = res.ai_role.department if res.ai_role else "General"
                rat_str = res.ai_role.rationale if res.ai_role else ""
                st.markdown(f"""<div class="ai-feature-card">
<div>
<div style="font-size:0.75rem; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:0.8px;">
👤 3. Qualifying Characteristics
</div>
<div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:6px; line-height:1.3;">
{esc(persona_str)}
</div>
<div style="margin-top:8px;">
<span class="tag-chip tag-purple">{esc(sen_str)}</span>
</div>
</div>
<div style="margin-top:14px; font-size:0.82rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
<div style="color:#94A3B8; font-size:0.76rem;">Dept: <strong style="color:#E2E8F0;">{esc(dept_str)}</strong></div>
<div style="font-style:italic; margin-top:4px; color:#A78BFA;">"{esc(rat_str)}"</div>
</div>
</div>""", unsafe_allow_html=True)

            with ai_col4:
                urgency_str = res.ai_intent.urgency_tier if res.ai_intent else "Moderate Urgency"
                timeline_str = res.ai_intent.timeline_detected or "Standard Inbound"
                intent_rat = res.ai_intent.rationale if res.ai_intent else ""
                st.markdown(f"""<div class="ai-feature-card">
<div>
<div style="font-size:0.75rem; font-weight:700; color:#FBBF24; text-transform:uppercase; letter-spacing:0.8px;">
⚡ 4. Readiness to Buy
</div>
<div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:6px; line-height:1.3;">
{esc(urgency_str)}
</div>
<div style="margin-top:8px;">
<span class="tag-chip tag-amber">{esc(timeline_str)}</span>
</div>
</div>
<div style="margin-top:14px; font-size:0.82rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
<div style="font-style:italic; color:#FDE68A;">"{esc(intent_rat)}"</div>
</div>
</div>""", unsafe_allow_html=True)

            # 3. ⚡ 4-Dimensional Revenue Intelligence Score Cards
            st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#0F172A; font-weight:700; margin-bottom:12px;'>⚡ GTM Partners 4-Pillar Revenue Scores</h4>", unsafe_allow_html=True)
            p1, p2, p3, p4 = st.columns(4)

            pillars = [
                (p1, "1. FIRMOGRAPHICS", res.pillar_firmographics, cfg.weight_firmographics, "#38BDF8"),
                (p2, "2. TECHNOGRAPHICS", res.pillar_value, cfg.weight_value, "#34D399"),
                (p3, "3. QUALIFYING FIT", res.pillar_authority, cfg.weight_authority, "#A78BFA"),
                (p4, "4. READINESS TO BUY", res.pillar_intent, cfg.weight_intent, "#FBBF24")
            ]

            for col, title, p_res, weight, col_accent in pillars:
                with col:
                    diff = p_res.score - 50.0
                    diff_str = f"+{diff:.0f} pts" if diff >= 0 else f"{diff:.0f} pts"
                    st.markdown(f"""<div class="metric-pillar-card">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div style="font-size:0.72rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.6px;">
{esc(title)}
</div>
<div style="font-size:0.72rem; font-weight:700; color:{col_accent};">
{weight*100:.0f}% Weight
</div>
</div>
<div style="font-size:2.1rem; font-weight:800; color:#FFFFFF; margin:8px 0; letter-spacing:-0.5px;">
{p_res.score:.0f} <span style="font-size:1.0rem; font-weight:500; color:#94A3B8;">/100</span>
</div>
<div style="font-size:0.80rem; font-weight:600; color:{col_accent};">
{diff_str} vs baseline
</div>
</div>""", unsafe_allow_html=True)

            # 3.5 📊 Scoring Audit Trail & Decision Tracker
            if res.scoring_tracker:
                st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
                with st.expander("📊 4-Pillar Scoring Audit Trail & Decision Tracker (Why & On What Basis Score Was Allotted)", expanded=True):
                    st.caption("Detailed GTM audit ledger documenting exact criteria, positive scoring drivers, and deduction factors for every pillar:")
                    for item in res.scoring_tracker:
                        with st.container(border=True):
                            tc1, tc2, tc3 = st.columns([3, 1, 1])
                            with tc1:
                                st.markdown(f"**{esc(item.pillar_name)}**")
                                st.markdown(f"<div style='font-size:0.82rem; color:#475569;'><strong>Decision Basis:</strong> {esc(item.basis_criterion)}</div>", unsafe_allow_html=True)
                            with tc2:
                                st.markdown(f"<div style='text-align:right;'><span style='font-size:1.15rem; font-weight:800; color:#4338CA;'>{item.allotted_score:.0f}</span> / 100<br/><span style='font-size:0.75rem; color:#64748B;'>Weight: {item.weight_pct * 100:.0f}%</span></div>", unsafe_allow_html=True)
                            with tc3:
                                st.markdown(f"<div style='text-align:right;'><span style='font-size:1.15rem; font-weight:800; color:#059669;'>+{item.points_contributed:.1f}</span> pts<br/><span style='font-size:0.75rem; color:#64748B;'>to Master Score</span></div>", unsafe_allow_html=True)

                            st.markdown(f"<div style='font-size:0.84rem; color:#334155; margin-top:4px;'><em>💡 {esc(item.decision_rationale)}</em></div>", unsafe_allow_html=True)
                            
                            if item.verified_signals or item.deduction_gaps:
                                sc_a, sc_b = st.columns(2)
                                with sc_a:
                                    if item.verified_signals:
                                        st.markdown("<div style='font-size:0.78rem; font-weight:700; color:#059669;'>✓ Verified Positive Drivers:</div>", unsafe_allow_html=True)
                                        for sig in item.verified_signals:
                                            st.markdown(f"<div style='font-size:0.78rem; color:#065F46;'>• {esc(sig)}</div>", unsafe_allow_html=True)
                                chi_b = sc_b
                                with chi_b:
                                    if item.deduction_gaps:
                                        st.markdown("<div style='font-size:0.78rem; font-weight:700; color:#D97706;'>⚠ Missing / Deduction Factors:</div>", unsafe_allow_html=True)
                                        for gap in item.deduction_gaps:
                                            st.markdown(f"<div style='font-size:0.78rem; color:#92400E;'>• {esc(gap)}</div>", unsafe_allow_html=True)

            # 4. 🎯 Next Best Action & Routing Card
            st.markdown(f"""<div class="action-routing-card">
<div style="font-size:0.78rem; font-weight:700; color:#F472B6; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
🎯 Strategic Next Best Action & Routing &bull; SLA: {esc(res.urgency_sla)}
</div>
<div style="font-size:1.25rem; font-weight:700; color:#FFFFFF; margin-bottom:10px;">
Channel: <span style="color:#FDE68A;">{esc(res.recommended_channel)}</span>
</div>
<div style="font-size:0.92rem; color:#F1F5F9; line-height:1.5; margin-bottom:12px;">
<strong>Strategic Value Wedge:</strong> {esc(res.value_wedge)}
</div>
<div style="background:rgba(0,0,0,0.3); border-left:4px solid #F472B6; padding:12px 16px; border-radius:8px;">
<div style="font-size:0.76rem; font-weight:700; color:#F472B6; text-transform:uppercase; letter-spacing:0.5px;">🔥 Recommended 1-Sentence Outreach Hook (Ready to Copy):</div>
<div style="font-size:0.92rem; color:#FFFFFF; font-style:italic; margin-top:4px;">"{esc(res.outreach_hook)}"</div>
</div>
</div>""", unsafe_allow_html=True)

            # 5. Strengths vs Risks
            c_why, c_risk = st.columns(2)
            with c_why:
                with st.container(border=True):
                    st.markdown("#### 🟢 Verified ICP Strengths & Scale Drivers")
                    if res.key_strengths:
                        for s in res.key_strengths:
                            clean_s = s.lstrip("✓").lstrip("•").strip()
                            st.success(f"✓ {esc(clean_s)}")
                    else:
                        st.info("Standard baseline profile.")
            with c_risk:
                with st.container(border=True):
                    st.markdown("#### ⚠️ Enterprise Discovery Risks & Considerations")
                    if res.key_risks:
                        for r in res.key_risks:
                            clean_r = r.lstrip("⚠").lstrip("•").strip()
                            st.warning(f"⚠ {esc(clean_r)}")
                    else:
                        st.success("✓ Zero critical risks detected.")

            # 6. Structured Consultative Discovery Prompts
            if res.discovery_questions:
                with st.expander("❓ Consultative Discovery Questions (For SDR & AE Qualification Calls)", expanded=True):
                    for i, q in enumerate(res.discovery_questions, 1):
                        clean_q = q.lstrip("•").lstrip(f"{i}.").strip()
                        st.markdown(f"**{i}. Discovery Prompt:** *{esc(clean_q)}*")


