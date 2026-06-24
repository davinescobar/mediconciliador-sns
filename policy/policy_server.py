"""
PolicyServer — two-layer safety filter for MediConciliador SNS.

Layer 1 (structural): deterministic forbidden-phrase detection via YAML rules.
Layer 2 (semantic): LLM-based detection of implicit clinical directives that
evade the structural filter. Only runs when structural check passes.

Returns a PolicyCheckResult with passed, blocked_phrases, missing_required.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class PolicyCheckResult:
    passed: bool
    blocked_phrases: list[dict] = field(default_factory=list)
    missing_required: list[str] = field(default_factory=list)


class PolicyServer:
    def __init__(self, policy_dir: Path | None = None) -> None:
        if policy_dir is None:
            policy_dir = Path(__file__).parent

        with open(policy_dir / "forbidden_phrases.yaml", encoding="utf-8") as f:
            phrases_data = yaml.safe_load(f)

        self._forbidden: list[dict] = []
        for lang in ("spanish", "english"):
            for item in phrases_data.get("phrases", {}).get(lang, []):
                self._forbidden.append(item)

        with open(policy_dir / "policies.yaml", encoding="utf-8") as f:
            policies = yaml.safe_load(f)

        patient_policy = policies.get("patient_output_policy", {})
        self._required_high_risk_es: list[str] = patient_policy.get(
            "required_phrases_for_high_risk_es", []
        )

    def check_semantic(self, text: str) -> tuple[bool, str]:
        # Day 5: second-layer LLM gating — catches implicit directives that bypass the structural filter
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return (True, "")

        try:
            from google import genai

            model = os.environ.get("MODEL_NAME", "gemini-3.1-flash-lite")
            client = genai.Client(api_key=api_key)
            prompt = (
                "You are a clinical safety auditor reviewing patient-facing text from a "
                "medication reconciliation system.\n\n"
                "Does the following text contain IMPLICIT clinical directives — instructions "
                "that could lead a patient to change their medication behavior WITHOUT using "
                "explicit forbidden phrases? Safe texts are purely informational and direct the "
                "patient to consult a professional.\n\n"
                f"Text:\n---\n{text}\n---\n\n"
                "Respond with ONLY a JSON object (no markdown):\n"
                '{"safe": true, "reason": ""} if the text is safe.\n'
                '{"safe": false, "reason": "<brief reason>"} ONLY if it contains implicit directives.'
            )
            response = client.models.generate_content(model=model, contents=prompt)
            raw = (response.text or "").strip()
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return (bool(data.get("safe", True)), str(data.get("reason", "")))
        except Exception:
            pass

        return (True, "")

    def check_patient_output(
        self, text: str, is_high_risk: bool = False
    ) -> PolicyCheckResult:
        text_lower = text.lower()

        blocked: list[dict] = []
        for item in self._forbidden:
            if item["phrase"].lower() in text_lower:
                blocked.append(
                    {
                        "phrase": item["phrase"],
                        "severity": item["severity"],
                        "reason": item["reason"],
                    }
                )

        # Semantic check only runs when structural passes — it guards against evasion, not duplication
        if not blocked:
            semantic_passed, semantic_reason = self.check_semantic(text)
            if not semantic_passed:
                blocked.append(
                    {
                        "phrase": "[implicit directive detected]",
                        "severity": "high",
                        "reason": semantic_reason,
                    }
                )

        missing_required: list[str] = []
        if is_high_risk:
            for req in self._required_high_risk_es:
                if req.lower() not in text_lower:
                    missing_required.append(req)

        return PolicyCheckResult(
            passed=len(blocked) == 0 and len(missing_required) == 0,
            blocked_phrases=blocked,
            missing_required=missing_required,
        )
