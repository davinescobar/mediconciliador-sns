"""
Integration tests for the ADK multi-agent pipeline.

TestOrchestratorStructure  — always runs, verifies agent graph wiring (no LLM call)
TestOrchestratorIntegration — requires GOOGLE_API_KEY, runs full end-to-end pipeline
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from agents.orchestrator import create_orchestrator
from tools.policy_check import run_policy_check
from tools.report_generation import run_full_analysis


# ── Structural tests (no LLM call) ───────────────────────────────────────────


class TestOrchestratorStructure:
    """Verifies the ADK agent graph is wired correctly. No API call required."""

    def setup_method(self):
        self.orchestrator = create_orchestrator()

    def test_is_sequential_agent(self):
        assert isinstance(self.orchestrator, SequentialAgent)

    def test_has_three_sub_agents(self):
        assert len(self.orchestrator.sub_agents) == 3

    def test_sub_agent_names_in_pipeline_order(self):
        names = [a.name for a in self.orchestrator.sub_agents]
        assert names == ["DataCollectionAgent", "AnalysisAgent", "CommunicationAgent"]

    def test_all_sub_agents_are_llm_agents(self):
        for agent in self.orchestrator.sub_agents:
            assert isinstance(agent, LlmAgent)

    def test_output_keys_form_pipeline_chain(self):
        data_agent, analysis_agent, comm_agent = self.orchestrator.sub_agents
        assert data_agent.output_key == "case_data"
        assert analysis_agent.output_key == "analysis_results"
        assert comm_agent.output_key == "reconciliation_report"

    def test_data_collection_agent_uses_mcp_toolset(self):
        data_agent = self.orchestrator.sub_agents[0]
        assert any(isinstance(t, McpToolset) for t in data_agent.tools)

    def test_analysis_agent_uses_run_full_analysis(self):
        assert run_full_analysis in self.orchestrator.sub_agents[1].tools

    def test_communication_agent_uses_run_policy_check(self):
        assert run_policy_check in self.orchestrator.sub_agents[2].tools


# ── End-to-end integration tests (requires GOOGLE_API_KEY) ───────────────────


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY"),
    reason="requires GOOGLE_API_KEY",
)
class TestOrchestratorIntegration:
    """Full pipeline test for case_001. Runs once per session via setup_class."""

    @classmethod
    def setup_class(cls):
        from google.adk.runners import InMemoryRunner
        from google.genai import types

        async def _run() -> dict:
            orchestrator = create_orchestrator()
            runner = InMemoryRunner(agent=orchestrator, app_name="mediconciliador-test")
            session = await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id="test",
                state={"case_id": "case_001"},
            )
            async for _ in runner.run_async(
                user_id="test",
                session_id=session.id,
                new_message=types.Content(
                    role="user",
                    parts=[types.Part(text="Perform medication reconciliation for case_001")],
                ),
            ):
                pass
            updated = await runner.session_service.get_session(
                app_name=runner.app_name,
                user_id="test",
                session_id=session.id,
            )
            return dict(updated.state) if updated else {}

        cls._state = asyncio.run(_run())

    def test_all_three_state_keys_populated(self):
        assert "case_data" in self._state, "DataCollectionAgent did not write case_data"
        assert "analysis_results" in self._state, "AnalysisAgent did not write analysis_results"
        assert "reconciliation_report" in self._state, "CommunicationAgent did not write reconciliation_report"

    def test_analysis_results_structure(self):
        report = json.loads(self._state["analysis_results"])
        assert "discrepancies" in report
        assert "summary" in report
        assert "requires_professional_review" in report

    def test_case_001_detects_high_risk_discrepancy(self):
        report = json.loads(self._state["analysis_results"])
        assert report["summary"]["high_risk"] >= 1
        assert report["requires_professional_review"] is True

    def test_patient_summary_passes_policy_check(self):
        report = json.loads(self._state["reconciliation_report"])
        assert report["policy_check"]["passed"] is True
