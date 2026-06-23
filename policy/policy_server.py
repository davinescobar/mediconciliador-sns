"""
PolicyServer — deterministic safety filter for MediConciliador SNS.

Intercepts patient-facing text before display:
- Detects forbidden phrases (forbidden_phrases.yaml)
- Verifies required phrases are present when is_high_risk=True
- Returns a PolicyCheckResult with passed, blocked_phrases, missing_required
"""

from __future__ import annotations

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
