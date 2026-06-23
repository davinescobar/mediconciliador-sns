"""
MediConciliador SNS — end-to-end demo runner.

Usage:
    cd mediconciliador-sns
    GOOGLE_API_KEY=your_key python demo/run_case.py [case_id]

Default case_id: case_001 (NSAID + anticoagulant, HIGH risk)

The script runs the full SequentialAgent pipeline:
  DataCollectionAgent → AnalysisAgent → CommunicationAgent

And prints the full execution trace plus the final reconciliation report.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv  # type: ignore[import-untyped]

load_dotenv(Path(__file__).parent.parent / ".env")

from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.orchestrator import create_orchestrator


def _print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


async def run_case(case_id: str = "case_001") -> None:
    orchestrator = create_orchestrator()
    runner = InMemoryRunner(agent=orchestrator, app_name="mediconciliador-sns")

    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="demo",
        state={"case_id": case_id},
    )

    _print_section(f"MediConciliador SNS — {case_id}")
    print(f"Running three-agent pipeline: DataCollection → Analysis → Communication")

    agent_steps: list[str] = []
    final_report: str | None = None

    async for event in runner.run_async(
        user_id="demo",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=f"Perform medication reconciliation for {case_id}")],
        ),
    ):
        if hasattr(event, "author") and event.author:
            step = f"[{event.author}]"
            if step not in agent_steps:
                agent_steps.append(step)
                print(f"  → {event.author} running...")

        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text
            if final_text:
                final_report = final_text

    # Retrieve session state
    updated_session = await runner.session_service.get_session(
        app_name=runner.app_name,
        user_id="demo",
        session_id=session.id,
    )
    state = updated_session.state if updated_session else {}

    _print_section("Analysis Results")
    analysis_raw = state.get("analysis_results", "")
    if analysis_raw:
        try:
            analysis = json.loads(analysis_raw)
            print(json.dumps(analysis["summary"], indent=2, ensure_ascii=False))
            print(f"\nRequires professional review: {analysis.get('requires_professional_review')}")
            print("\nDiscrepancies:")
            for d in analysis.get("discrepancies", []):
                print(f"  [{d['risk_level']}] {d['medication']} — {d['type']}")
                print(f"        {d.get('rationale', '')}")
        except (json.JSONDecodeError, KeyError):
            print(analysis_raw[:500])

    _print_section("Tool Execution Trace")
    if analysis_raw:
        try:
            trace = json.loads(analysis_raw).get("trace", [])
            for entry in trace:
                print(f"  {entry['timestamp'][:19]}  {entry['tool']}")
        except (json.JSONDecodeError, KeyError):
            pass

    _print_section("Reconciliation Report (CommunicationAgent)")
    report_raw = state.get("reconciliation_report", final_report or "")
    if report_raw:
        try:
            report = json.loads(report_raw)
            print("\n--- Professional Checklist ---")
            print(report.get("professional_checklist", ""))
            print("\n--- Patient Summary (ES) ---")
            print(report.get("patient_summary", ""))
            print("\n--- Policy Check ---")
            print(json.dumps(report.get("policy_check", {}), indent=2, ensure_ascii=False))
        except (json.JSONDecodeError, KeyError):
            print(report_raw[:1000])

    print()


if __name__ == "__main__":
    case_id = sys.argv[1] if len(sys.argv) > 1 else "case_001"
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not set. Add it to .env or export it.")
        sys.exit(1)
    asyncio.run(run_case(case_id))
