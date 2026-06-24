"""
CommunicationAgent — generates the professional checklist and patient-safe summary.

Reads analysis_results from session state, produces two outputs:
1. Professional checklist for the clinician.
2. Patient-safe explanation in plain Spanish (non-directive, passes policy check).

Uses run_policy_check to deterministically validate the patient summary before
finalizing the output. If the check fails, the agent must revise and retry.

Output is stored in session state under 'reconciliation_report'.
"""

import os

from google.adk.agents import LlmAgent
from google.genai import types

from tools.policy_check import run_policy_check

_MODEL = os.environ.get("MODEL_NAME", "gemini-3.1-flash-lite")

# ADK Day 2b: HttpRetryOptions prevents a transient 429/503 from killing the pipeline mid-demo
_GENERATE_CONFIG = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=5, initial_delay=1.0, exp_base=2.0)
    )
)

_INSTRUCTION = """\
You are the communication agent for MediConciliador SNS.

The reconciliation analysis has produced the following results:
{analysis_results}

Your task: generate the two required outputs following this exact sequence.

---
## STEP 1 — PROFESSIONAL CHECKLIST

For each discrepancy in the analysis results, generate a numbered review item:
- Medication name and discrepancy type
- Risk level with clinical rationale
- Specific questions or actions for the clinician to verify

---
## STEP 2 — DRAFT PATIENT SUMMARY (in Spanish)

Write a brief explanation for the patient and caregiver that:
- Acknowledges that some information about their medications needs to be reviewed
- States clearly that they should bring this document to their next appointment
- Does NOT include any of these FORBIDDEN phrases:
  "deje de tomar", "suspenda", "empiece a tomar", "cambie la dosis",
  "no necesita consultar", "puede tomarlo sin problema", "es seguro continuar",
  "es peligroso continuar", "tome este medicamento", "no tome este medicamento"
- MUST include: "requiere revisión profesional"
- MUST include: "no cambie la medicación sin consultar"
- MUST include: "lleve esta información a su profesional sanitario"

---
## STEP 3 — CALL run_policy_check

Call the tool run_policy_check with:
- patient_summary: the patient summary text you just wrote
- is_high_risk: true if the analysis contains any HIGH-risk discrepancy, false otherwise

If the result has passed=false:
- Revise the patient_summary to fix all blocked_phrases and add missing_required phrases
- Call run_policy_check again with the revised text
- Repeat until passed=true

---
## STEP 4 — OUTPUT JSON

Output a JSON object with these exact keys:
- "professional_checklist": string with the full checklist
- "patient_summary": string with the final approved patient summary in Spanish
- "policy_check": the exact JSON object returned by the last run_policy_check call

Output ONLY the JSON object. No markdown, no explanation, no code fences.\
"""


def create_communication_agent() -> LlmAgent:
    """Returns a configured CommunicationAgent with policy enforcement via tool."""
    # ADK Day 5: the agent is instructed to loop on run_policy_check until passed=true — safety is tool-enforced, not prompt-suggested
    return LlmAgent(
        name="CommunicationAgent",
        model=_MODEL,
        instruction=_INSTRUCTION,
        tools=[run_policy_check],
        output_key="reconciliation_report",
        generate_content_config=_GENERATE_CONFIG,
    )
