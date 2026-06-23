"""
run_policy_check — ADK-compatible tool wrapping PolicyServer.

Exposed as a callable tool to CommunicationAgent so the LLM can
deterministically verify its patient-facing output before finalizing it.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from policy.policy_server import PolicyServer

_server = PolicyServer()


def run_policy_check(patient_summary: str, is_high_risk: bool = False) -> str:
    """
    Checks patient-facing text against MediConciliador safety policies.

    Detects forbidden phrases (direct medication instructions) and verifies
    that HIGH-risk outputs contain the required professional-review disclaimers.

    Args:
        patient_summary: The patient-facing text to validate.
        is_high_risk: True when the case has at least one HIGH-risk discrepancy.

    Returns:
        JSON object with:
          - passed (bool): True if no violations found.
          - blocked_phrases (list): Each item has phrase, severity, reason.
          - missing_required (list): Required phrases absent from the text.
    """
    result = _server.check_patient_output(patient_summary, is_high_risk)
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)
