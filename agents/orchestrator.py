"""
MediConciliadorOrchestrator

SequentialAgent that coordinates three LlmAgent sub-agents:
  1. DataCollectionAgent — fetches case data via MCP
  2. AnalysisAgent       — runs deterministic reconciliation pipeline
  3. CommunicationAgent  — generates professional checklist + patient summary

Each sub-agent writes its output to session state via output_key.
The next sub-agent reads it through {key} placeholders in its instruction.
"""

from google.adk.agents import SequentialAgent

from agents.discharge_parser_agent import create_data_collection_agent
from agents.reconciliation_agent import create_analysis_agent
from agents.communication_agent import create_communication_agent


def create_orchestrator() -> SequentialAgent:
    """Returns the MediConciliadorOrchestrator ready to run a case end-to-end."""
    return SequentialAgent(
        name="MediConciliadorOrchestrator",
        sub_agents=[
            create_data_collection_agent(),
            create_analysis_agent(),
            create_communication_agent(),
        ],
    )
