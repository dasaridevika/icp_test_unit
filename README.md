# ⚡ Jev ICP Scoring Intelligence

A high-velocity, production-grade **B2B Revenue Intelligence & ICP Qualification Engine** powered by **Jev (TypeSafe AI)** System-1 Decision Primitives (`Noul` / `bool`, `Choice`, and `Score`).

---

## 🏛️ System Architecture

```text
Streamlit UI Inbound Form
               ↓
    Unified State Dictionary (`build_lead_state`)
               ↓
    Parallel Jev System-1 Evaluation (`engine/client.py`)
    ├── Noul (Bool)   → Hard Disqualification & Anti-ICP Check
    ├── Choice        → Role Hierarchy, Buyer Persona & Tech Fit
    └── Score         → Calibrated 4-Pillar Rubric Scoring
               ↓
    Authoritative GTM Scorer (`engine/gtm_engine.py`)
    ├── 4-Pillar Score Computation (Firmographics, Authority, Intent, Value)
    ├── Master ICP Score (0–100) & Calibrated Priority Tiering
    └── Dynamic SLA Routing & Executive Outreach Opener
               ↓
    Interactive Streamlit Studio (`app.py`)
```

---

## ⚡ The 3 Jev Decision Primitives

| Jev Primitive | Question Type | Application in ICP Scoring |
| :--- | :--- | :--- |
| **`Noul` (`bool`)** | Calibrated Boolean Probability ($0.0 - 1.0$) | • Hard anti-ICP gating (student/freemail)<br>• Trade sanctions / restricted regions<br>• Executive budget sign-off authority |
| **`Choice`** | Categorical Classification & Probability Distribution | • Seniority tier (`C-Suite`, `VP`, `Director`, `Manager`, `IC`)<br>• Buyer persona (`Economic Buyer`, `Tech Champion`, `End User`)<br>• Tech stack ecosystem fit (`Modern Cloud`, `Legacy Blocker`) |
| **`Score`** | Rubric / Scale Placement with Confidence | • Firmographic market scale ($1 - 5$)<br>• Intent velocity & RFP readiness ($1 - 5$)<br>• Stakeholder authority ($1 - 5$)<br>• Contract expansion value ($1 - 5$) |

---

## 🔑 Configuration

Set your Jev / TypeSafe API key in your environment or GitHub Secrets:
* Variable Name: `JEV_API_KEY` (or `TYPESAFE_API_KEY`)

---

## 🚀 Getting Started

### 1. Installation

```bash
# Clone or navigate to the repository
cd jev_icp_scoring

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Streamlit Studio

```bash
streamlit run app.py
```

---

## 📐 GTM 4-Pillar Scoring Formula

$$\text{Master ICP Score} = (0.30 \times \text{Firmographics}) + (0.25 \times \text{Authority}) + (0.25 \times \text{Intent}) + (0.20 \times \text{Value})$$

### Priority Tier Thresholds & SLA Matrix

| Priority Tier | Score Threshold | SLA & Action |
| :--- | :---: | :--- |
| **Tier A1: Strategic Inbound** | $\ge 80$ | **<2h** Callback by Senior AE & RevOps Director |
| **Tier A2: High-Priority Outbound** | $\ge 65$ | **<24h** Outreach by Senior SDR |
| **Tier B1: Mid-Market Fast Track** | $\ge 50$ | **<48h** Inside Sales qualification |
| **Tier C: Long-Tail / Nurture** | $< 50$ | Automated marketing track |
| **Disqualified** | Anti-ICP Gate | Blocked / Archived under compliance policy |
