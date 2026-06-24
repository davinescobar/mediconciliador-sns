"""
AnalysisAgent — runs the full deterministic reconciliation pipeline.

Reads case_data from session state (set by DataCollectionAgent), calls
run_full_analysis to detect discrepancies and score risk, and stores
the analysis report in session state under 'analysis_results'.
"""

import os

from google.adk.agents import LlmAgent
from google.genai import types

from agents.callbacks import after_tool_log, before_tool_log
from tools.report_generation import run_full_analysis

_MODEL = os.environ.get("MODEL_NAME", "gemini-3.1-flash-lite")

# ADK Day 2b: HttpRetryOptions prevents a transient 429/503 from killing the pipeline mid-demo
_GENERATE_CONFIG = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=5, initial_delay=1.0, exp_base=2.0)
    )
)

_INSTRUCTION = """\
You are the analysis agent for MediConciliador SNS.

The data collection agent has gathered the following case data:
{case_data}

Your task: run the medication reconciliation analysis.

Call the tool run_full_analysis with the argument case_data_json set to the full \
JSON string of the case data shown above.

Return ONLY the JSON output from the tool — no explanation, no markdown.\
"""


def create_analysis_agent() -> LlmAgent:
    """Returns a configured AnalysisAgent (LlmAgent with run_full_analysis tool)."""
    return LlmAgent(
        name="AnalysisAgent",
        model=_MODEL,
        instruction=_INSTRUCTION,
        tools=[run_full_analysis],
        output_key="analysis_results",
        before_tool_callback=before_tool_log,
        after_tool_callback=after_tool_log,
        generate_content_config=_GENERATE_CONFIG,
    )
