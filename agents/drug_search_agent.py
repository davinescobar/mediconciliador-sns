"""
DrugInfoSearchAgent — LlmAgent with google_search (grounding with Google Search).

Demonstrates Day 2a of the Kaggle 5-day agents course: built-in ADK tools.
The google_search tool grounds the agent in real-time web data, so responses
reflect current drug information rather than the model's training cutoff.

Restriction: google_search cannot be mixed with function tools in the same
agent. This agent is intentionally standalone and used via AgentTool or
called directly from the Streamlit app.
"""

import os

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

_MODEL = os.environ.get("MODEL_NAME", "gemini-2.0-flash")

_INSTRUCTION = """\
You are a pharmacological information assistant for MediConciliador SNS, \
a medication reconciliation system for elderly patients in Spain.

Your role is to search for factual, up-to-date information about drug \
interactions, contraindications, and clinical safety relevant to the \
medications listed in a patient case.

IMPORTANT constraints:
- You NEVER prescribe, recommend stopping, or changing any medication.
- You ONLY provide informational context to support professional review.
- Always state that any clinical decision must be made by a licensed \
  healthcare professional.
- Search in Spanish or English based on the query.
- Keep responses concise and clinical (no marketing language).
- Ground all claims in the search results — do not rely on training data alone.

When given a list of medications or a specific drug interaction question, \
search Google for current clinical information and summarize the key \
safety points relevant to an elderly, polymedicated patient.\
"""


def create_drug_search_agent() -> LlmAgent:
    """Returns a DrugInfoSearchAgent grounded with Google Search."""
    return LlmAgent(
        name="DrugInfoSearchAgent",
        model=_MODEL,
        instruction=_INSTRUCTION,
        tools=[google_search],
    )
