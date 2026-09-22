"""
Jev (TypeSafe AI) System One Client — Live API Only
Evaluates state against decision primitives (Noul/bool, Choice, Score) via live API calls.
Fails loudly if API key is missing or service is unreachable.
"""

import os
import time
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

logger = logging.getLogger("jev_client")

# API Endpoints
DEFAULT_API_URL = os.environ.get("JEV_API_URL", "https://api.typesafe.ai/v1/system_one")


class NoulResult(BaseModel):
    """Result for a Noul (Boolean) decision primitive."""
    noul: bool
    probability: float
    confidence: float = 1.0
    raw_response: Optional[Dict[str, Any]] = None


class ChoiceResult(BaseModel):
    """Result for a Choice decision primitive."""
    choice: str
    distribution: Dict[str, float] = Field(default_factory=dict)
    confidence: float = 1.0
    raw_response: Optional[Dict[str, Any]] = None


class ScoreResult(BaseModel):
    """Result for a Score decision primitive."""
    score: float
    level: Optional[str] = None
    level_probabilities: Dict[str, float] = Field(default_factory=dict)
    confidence: float = 1.0
    raw_response: Optional[Dict[str, Any]] = None


class JevResponse(BaseModel):
    """Structured response from Jev System One live evaluation."""
    success: bool = True
    nouls: Dict[str, NoulResult] = Field(default_factory=dict)
    choices: Dict[str, ChoiceResult] = Field(default_factory=dict)
    scores: Dict[str, ScoreResult] = Field(default_factory=dict)
    latency_ms: float = 0.0
    mode: str = "live_api"
    error: Optional[str] = None


class JevClient:
    """
    Client for Jev (TypeSafe AI) System-1 Fast Decision Engine.
    Executes live parallel question evaluations. Requires JEV_API_KEY or TYPESAFE_API_KEY.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        # Read API key from parameter, OS environment, or Streamlit Cloud Secrets (st.secrets)
        key_found = (
            api_key or
            os.environ.get("JEV_API_KEY") or
            os.environ.get("TYPESAFE_API_KEY") or
            ""
        ).strip()

        if not key_found:
            try:
                import streamlit as st
                if hasattr(st, "secrets"):
                    key_found = str(
                        st.secrets.get("JEV_API_KEY") or
                        st.secrets.get("TYPESAFE_API_KEY") or
                        ""
                    ).strip()
            except Exception:
                pass

        self.api_key = key_found
        self.api_url = api_url or DEFAULT_API_URL
        self._sdk_client = None

        if self.api_key:
            os.environ["TYPESAFE_API_KEY"] = self.api_key
            os.environ["JEV_API_KEY"] = self.api_key
            try:
                from typesafe_sdk import TypeSafeClient
                self._sdk_client = TypeSafeClient(api_key=self.api_key)
            except Exception as e:
                logger.debug(f"typesafe-sdk initialization: {e}")

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def evaluate(
        self,
        state: Dict[str, Any],
        questions: Dict[str, Any]
    ) -> JevResponse:
        """
        Evaluates questions against state in parallel via live Jev API.
        Fails loudly if API key is missing or endpoint is unreachable.
        """
        if not self.has_api_key:
            err_msg = (
                "Jev API Key is missing. Please provide your API key via "
                "environment variable 'JEV_API_KEY' or GitHub Secrets 'JEV_API_KEY'."
            )
            logger.error(err_msg)
            return JevResponse(
                success=False,
                error=err_msg,
                mode="error_no_key"
            )

        start_time = time.perf_counter()

        # 1. Try SDK invocation
        if self._sdk_client:
            try:
                sdk_resp = self._sdk_client.system_one(state=state, questions=questions)
                latency = (time.perf_counter() - start_time) * 1000
                return self._parse_sdk_response(sdk_resp, latency)
            except Exception as e:
                logger.warning(f"SDK call failed, attempting REST: {e}")

        # 2. Try REST API invocation
        try:
            rest_resp = self._call_rest_api(state, questions)
            latency = (time.perf_counter() - start_time) * 1000
            if rest_resp:
                return self._parse_rest_response(rest_resp, latency)
        except Exception as e:
            err_msg = f"Jev API request failed: {str(e)}"
            logger.error(err_msg)
            return JevResponse(success=False, error=err_msg, mode="error_api_failed")

        err_msg = "Jev API returned an empty or invalid response."
        return JevResponse(success=False, error=err_msg, mode="error_empty_response")

    def _call_rest_api(self, state: Dict[str, Any], questions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Direct HTTPS REST call to TypeSafe / Jev endpoint."""
        serializable_questions = {}
        for q_key, q_obj in questions.items():
            if hasattr(q_obj, "dict"):
                serializable_questions[q_key] = q_obj.dict()
            elif isinstance(q_obj, dict):
                serializable_questions[q_key] = q_obj
            else:
                serializable_questions[q_key] = {
                    "type": getattr(q_obj, "type", "score"),
                    "instructions": getattr(q_obj, "instructions", str(q_obj)),
                    "criteria": getattr(q_obj, "criteria", None)
                }

        payload = {
            "state": state,
            "questions": serializable_questions
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "JevICPScorer/1.0"
        }

        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=20)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")

    def _parse_sdk_response(self, sdk_resp: Any, latency: float) -> JevResponse:
        """Parses output from typesafe_sdk TypeSafeClient SystemOneResponse."""
        nouls = {}
        choices = {}
        scores = {}

        # Parse from official typesafe_sdk response schema (sdk_resp.answers)
        answers = getattr(sdk_resp, "answers", {}) or {}
        for k, ans in answers.items():
            ans_type = getattr(ans, "type", "")
            if ans_type == "noul" or hasattr(ans, "noul"):
                prob = float(getattr(ans, "noul", 0.5))
                nouls[k] = NoulResult(
                    noul=(prob >= 0.5),
                    probability=prob,
                    confidence=1.0
                )
            elif ans_type == "choice" or hasattr(ans, "choice"):
                choices[k] = ChoiceResult(
                    choice=str(getattr(ans, "choice", "")),
                    distribution=getattr(ans, "probabilities", {}),
                    confidence=float(getattr(ans, "confidence", 1.0))
                )
            elif ans_type == "score" or hasattr(ans, "score"):
                legend = getattr(ans, "legend", {})
                score_val = float(getattr(ans, "score", 0.0))
                closest_idx = round(score_val)
                level_name = legend.get(closest_idx) if legend else None
                scores[k] = ScoreResult(
                    score=score_val,
                    level=level_name,
                    level_probabilities={str(lvl): p for lvl, p in getattr(ans, "probabilities", {}).items()},
                    confidence=float(getattr(ans, "confidence", 1.0))
                )

        # Fallback if old SDK schema with separate attributes
        if not nouls and hasattr(sdk_resp, "nouls") and sdk_resp.nouls:
            for k, v in sdk_resp.nouls.items():
                prob = getattr(v, "probability", 0.95 if getattr(v, "noul", False) else 0.05)
                nouls[k] = NoulResult(noul=bool(getattr(v, "noul", prob >= 0.5)), probability=prob, confidence=0.90)

        if not choices and hasattr(sdk_resp, "choices") and sdk_resp.choices:
            for k, v in sdk_resp.choices.items():
                choices[k] = ChoiceResult(choice=getattr(v, "choice", ""), distribution=getattr(v, "distribution", {}), confidence=0.90)

        if not scores and hasattr(sdk_resp, "scores") and sdk_resp.scores:
            for k, v in sdk_resp.scores.items():
                scores[k] = ScoreResult(score=float(getattr(v, "score", 3.0)), level=getattr(v, "level", None), confidence=0.90)

        return JevResponse(
            success=True,
            nouls=nouls,
            choices=choices,
            scores=scores,
            latency_ms=latency,
            mode="live_sdk"
        )

    def _parse_rest_response(self, data: Dict[str, Any], latency: float) -> JevResponse:
        """Parses raw JSON from TypeSafe REST API."""
        nouls = {}
        choices = {}
        scores = {}

        raw_nouls = data.get("nouls", {})
        for k, v in raw_nouls.items():
            prob = float(v.get("probability", 0.9 if v.get("noul") else 0.1))
            nouls[k] = NoulResult(
                noul=bool(v.get("noul", prob >= 0.5)),
                probability=prob,
                confidence=float(v.get("confidence", 0.90)),
                raw_response=v
            )

        raw_choices = data.get("choices", {})
        for k, v in raw_choices.items():
            choices[k] = ChoiceResult(
                choice=str(v.get("choice", "")),
                distribution=v.get("distribution", {}),
                confidence=float(v.get("confidence", 0.90)),
                raw_response=v
            )

        raw_scores = data.get("scores", {})
        for k, v in raw_scores.items():
            scores[k] = ScoreResult(
                score=float(v.get("score", 3.0)),
                level=v.get("level"),
                level_probabilities=v.get("level_probabilities", {}),
                confidence=float(v.get("confidence", 0.90)),
                raw_response=v
            )

        return JevResponse(
            success=True,
            nouls=nouls,
            choices=choices,
            scores=scores,
            latency_ms=latency,
            mode="live_rest"
        )
