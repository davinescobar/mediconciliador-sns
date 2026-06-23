# Video Plan — MediConciliador SNS Kaggle Submission

## Format
- Duration: 2-3 minutes
- Screen recording + narration
- Language: English (Kaggle audience)
- Resolution: 1080p minimum

## Checklist before recording

- [ ] app.py running locally with all 3 cases
- [ ] case_001 end-to-end working (discharge + prescription + interview → HIGH risk)
- [ ] Agent trace visible in UI
- [ ] Safety policy result visible in UI
- [ ] Evaluation screen showing metrics
- [ ] All 6 course concepts visible in demo

## Slide for course requirements

Create a simple slide or in-app panel showing:
```
MediConciliador SNS — Course Concepts Demonstrated

1. ADK multi-agent system → agents/orchestrator.py + subagents
2. MCP Server → mcp/mcp_server.py (read-only, SQLite)
3. Agent Skill → .agent/skills/medication-reconciliation/SKILL.md
4. Security features → policy/policy_server.py + guardrails
5. Deployable app → streamlit run app.py
6. Antigravity workflow → spec-driven development with skills
```

## Recording order

1. Open terminal → show project structure (tree)
2. `streamlit run app.py`
3. Select case_001 in UI
4. Walk through 4 screens
5. Show SKILL.md in editor (Antigravity concept)
6. Show agent trace
7. Show course requirements slide
