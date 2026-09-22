"""
Unit Tests for Jev Decision Primitives: Noul (Bool), Choice, and Score.
"""

import pytest
from engine.client import JevClient, JevResponse, NoulResult, ChoiceResult, ScoreResult
from engine.primitives import (
    create_noul_question,
    create_choice_question,
    create_score_question,
    build_lead_state,
    ICP_NOUL_QUESTIONS,
    ICP_CHOICE_QUESTIONS,
    ICP_SCORE_QUESTIONS
)


def test_noul_primitive_creation():
    """Test Noul (bool) question structure."""
    noul_q = create_noul_question("Is this lead a valid business account?")
    assert noul_q.type == "noul"
    assert "valid business" in noul_q.instructions


def test_choice_primitive_creation():
    """Test Choice question structure."""
    options = ["Tier 1 Enterprise", "Mid-Market", "SMB"]
    choice_q = create_choice_question("What is the enterprise scale?", options)
    assert choice_q.type == "choice"
    assert len(choice_q.criteria) == 3
    assert "Tier 1 Enterprise" in choice_q.criteria


def test_score_primitive_creation():
    """Test Score (rubric) question structure."""
    levels = ["Level 1", "Level 2", "Level 3", "Level 4"]
    score_q = create_score_question("Score the buying readiness:", levels)
    assert score_q.type == "score"
    assert len(score_q.criteria) == 4


def test_jev_client_fails_loudly_without_key():
    """Test JevClient fails loudly when no API key is provided."""
    client = JevClient(api_key="")
    state = build_lead_state(
        company_name="Snowflake Inc.",
        industry="Cloud & Big Data",
        annual_revenue_usd=2000000000.0,
        headcount=7000,
        location="United States",
        contact_name="Benoit Dageville",
        contact_role="Co-Founder & VP Product",
        email="benoit@snowflake.com",
        buying_intent="Immediate RFP for enterprise intelligence platform integration.",
        target_deal_size_usd=100000.0
    )

    questions = {"is_anti_icp": ICP_NOUL_QUESTIONS["is_anti_icp"]}
    response: JevResponse = client.evaluate(state=state, questions=questions)

    assert response.success is False
    assert "API Key is missing" in response.error


def test_jev_client_parse_rest_response():
    """Test parsing of raw Jev REST API response."""
    client = JevClient(api_key="mock_key_for_testing")
    mock_raw_data = {
        "nouls": {
            "is_anti_icp": {"noul": False, "probability": 0.05, "confidence": 0.95}
        },
        "choices": {
            "seniority_level": {
                "choice": "C-Suite / Founder / Board (+5 pts)",
                "distribution": {"C-Suite / Founder / Board (+5 pts)": 0.92, "VP / Executive Leadership (+4 pts)": 0.08},
                "confidence": 0.92
            }
        },
        "scores": {
            "firmographic_fit": {"score": 4.5, "level": "Tier-1 Enterprise Leader", "confidence": 0.90}
        }
    }

    parsed = client._parse_rest_response(mock_raw_data, latency=120.0)
    assert parsed.success is True
    assert parsed.nouls["is_anti_icp"].noul is False
    assert "C-Suite" in parsed.choices["seniority_level"].choice
    assert parsed.scores["firmographic_fit"].score == 4.5
