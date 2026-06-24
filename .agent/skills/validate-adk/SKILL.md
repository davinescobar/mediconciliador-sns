---
name: validate-adk
description: |
  Validates the ADK multi-agent system requirement for the Kaggle capstone.
  Trigger when asked to validate, audit or review the ADK implementation.
  Use before video recording or Kaggle submission to catch missing elements.
source: Day 1 (context engineering), Day 2 (tools + MCPToolset), Day 3 (session services, callbacks)
---

# Validation: ADK Multi-Agent System

## What the whitepaper requires (Day 1–3)

- `SequentialAgent` (or `ParallelAgent` / `LoopAgent`) as orchestrator
- Multiple `LlmAgent` sub-agents, each with a single responsibility
- `MCPToolset` integration on at least one agent
- `output_key` for session-state passing between agents
- `DatabaseSessionService` or `InMemorySessionService` wired to the Runner
- ADK callbacks: `before_tool_callback` and `after_tool_callback` for observability
- `generate_config` with `HttpRetryOptions` — every notebook in the course uses this

## Checklist — files to inspect

- [ ] `agents/orchestrator.py` — SequentialAgent defined; sub_agents list
- [ ] `agents/discharge_parser_agent.py` — MCPToolset, output_key, callbacks
- [ ] `agents/reconciliation_agent.py` — output_key, callbacks
- [ ] `agents/communication_agent.py` — run_policy_check tool, output_key
- [ ] `agents/drug_search_agent.py` — google_search grounding
- [ ] `app.py` — Runner with session service wired

## Current status (as of 2026-06-24)

| Element | File | Status |
|---------|------|--------|
| SequentialAgent | orchestrator.py | ✅ |
| 3 core LlmAgents | agents/*.py | ✅ |
| MCPToolset | discharge_parser_agent.py | ✅ |
| output_key | all agents | ✅ |
| DatabaseSessionService | app.py (main pipeline) | ✅ |
| Callbacks before/after | DataCollectionAgent, AnalysisAgent | ✅ |
| google_search grounding | drug_search_agent.py | ✅ |
| **HttpRetryOptions** | **none** | **❌ MISSING** |

## Gap: HttpRetryOptions

Every notebook in the course configures retry:

```python
from google.genai import types

generate_config = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=5,
            initial_delay=1.0,
            exp_base=2.0,
        )
    )
)

agent = LlmAgent(
    name="...",
    model=_MODEL,
    generate_content_config=generate_config,
    ...
)
```

**Risk without it:** a single 429 or 503 during the demo video kills the run.  
**Fix:** ~8 lines added to each LlmAgent factory function.
