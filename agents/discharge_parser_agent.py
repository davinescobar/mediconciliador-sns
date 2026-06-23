"""
DataCollectionAgent — fetches all clinical data for a case via MCP tools.

Calls five MCP tools in sequence (discharge summary, active prescription,
patient interview, allergies, high-risk medications) and returns a JSON object
with all collected data stored in session state under 'case_data'.
"""

import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

from agents.callbacks import after_tool_log, before_tool_log

_MCP_SERVER_PATH = Path(__file__).parent.parent / "mcp" / "mcp_server.py"
_MODEL = os.environ.get("MODEL_NAME", "gemini-2.0-flash")

_INSTRUCTION = """\
You are the data collection agent for MediConciliador SNS, a medication reconciliation \
system for elderly patients in Spain.

Your task: collect all clinical data for the case with case_id="{case_id}" from the \
MCP data server.

Call these five tools IN THIS ORDER:
1. get_discharge_summary with case_id="{case_id}"
2. get_active_prescription with case_id="{case_id}"
3. get_patient_interview with case_id="{case_id}"
4. get_allergies with case_id="{case_id}"
5. get_high_risk_medications (no arguments)

After all five tool calls, output a single JSON object with EXACTLY these keys:
- "case_id": "{case_id}"
- "discharge_summary": <full JSON from tool 1, parsed as object>
- "active_prescription": <full JSON from tool 2, parsed as object>
- "patient_interview": <full JSON from tool 3, parsed as object>
- "allergies": <allergies list from tool 4>
- "high_risk_medications": <full JSON from tool 5, parsed as array>
- "risk_factors": <risk_factors list — extract from get_risk_factors if available, \
or leave as empty list []>

Output ONLY the JSON object. No markdown, no explanation, no code fences.\
"""


def create_data_collection_agent() -> LlmAgent:
    """Returns a configured DataCollectionAgent (LlmAgent with MCPToolset)."""
    toolset = McpToolset(
        connection_params=StdioServerParameters(
            command="python",
            args=[str(_MCP_SERVER_PATH)],
        )
    )
    return LlmAgent(
        name="DataCollectionAgent",
        model=_MODEL,
        instruction=_INSTRUCTION,
        tools=[toolset],
        output_key="case_data",
        before_tool_callback=before_tool_log,
        after_tool_callback=after_tool_log,
    )
