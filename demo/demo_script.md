# Demo Script — MediConciliador SNS (Kaggle Capstone)

**Target duration:** 3:30 – 4:30 min (max 5:00 — YouTube required)  
**Language:** English  
**Platform:** YouTube (Kaggle requirement — Loom does not qualify)  
**Format:** Screen recording + narration (no face cam required)  
**Resolution:** 1080p minimum

---

## Pre-recording checklist

Run these steps before hitting record.

```bash
# 1. Start MCP server in background (keep terminal open)
cd mediconciliador-sns
source .venv/bin/activate
python mcp/mcp_server.py &

# 2. Verify tests pass
pytest tests/ -q

# 3. Start Streamlit
streamlit run app.py
```

Confirm in browser before recording:
- [ ] Dropdown shows case_001 through case_010 (10 synthetic cases)
- [ ] "Run medication reconciliation" button is visible
- [ ] No error banners on screen
- [ ] Browser tab title reads "MediConciliador SNS"
- [ ] Tab 5 (Drug Search) loads and accepts queries

Have open in separate terminals (for the project structure shot):
```
mediconciliador-sns/
├── agents/       ← orchestrator + 8 LlmAgent subagents
├── mcp/          ← MCP server (read-only, SQLite, 9 tools)
├── tools/        ← deterministic pipeline tools
├── policy/       ← Policy Server + guardrails
├── .agent/       ← Agent Skill (SKILL.md)
├── evals/        ← evaluation runner (36 checks)
├── tests/        ← 131 pytest tests
└── app.py        ← Streamlit UI (6 tabs)
```

---

## Recording sequence

### [0:00 – 0:30] Part 1 — The problem

**Screen:** Slide or blank background. Optional: show a simple diagram of 3 document icons (discharge / prescription / patient).

**Narration:**
> "After hospital discharge, older patients often receive three separate medication lists — one from the hospital, one from their primary care physician, and what they report taking themselves. These lists don't always match. That mismatch is called a medication discrepancy, and it's one of the leading causes of preventable harm in elderly care."

> "The scale of this problem is significant: the WHO estimates medication errors cost 42 billion dollars a year globally. The OECD estimates 1 in 10 hospitalizations may be caused by medication-related harm. In the United States, the Institute of Medicine estimated 1.5 million preventable adverse drug events every year — and the Joint Commission has made medication reconciliation a National Patient Safety Goal since 2005. This is a universal problem."

> "MediConciliador SNS is a multi-agent AI system that compares all three sources, detects discrepancies, classifies risk, and generates safe outputs for professional review. It uses the NLM RxNorm database — the US National Library of Medicine's standard drug terminology — so the interaction checking works across both US and international drug names."

---

### [0:30 – 0:45] Part 2 — The agent architecture

**Screen:** Show the terminal with the project tree (run `tree -L 2 --dirsfirst` or use a pre-made slide).

**Narration:**
> "The system is built on Google's Agent Development Kit. A SequentialAgent orchestrator coordinates eight specialized LLM agents — from parsing discharge summaries and normalizing medication names, to risk triage and communication — plus a dedicated drug search agent powered by Gemini's grounding tools."

> "All data is synthetic. The MCP server is read-only. The agent does not write to any database."

---

### [0:45 – 2:10] Part 3 — Live demo (case_001)

**Screen:** Switch to browser — Streamlit app.

#### Step 1 — Case selection (0:45 – 0:55)

> "Let's run the most clinically significant case: case_001. A patient discharged with apixaban — a blood thinner — who is still taking ibuprofen, an anti-inflammatory they were told to stop."

*Action: Select `case_001` from the dropdown.*

---

#### Step 2 — Source documents (0:55 – 1:10)

> "The Sources tab shows the three inputs: the hospital discharge summary, the active prescription, and what the patient reported in the interview."

*Action: Click the Sources tab. Pan across the three columns slowly. Highlight the ibuprofen row.*

> "Ibuprofen is absent from the discharge summary — the hospital stopped it. But the patient is still taking it. That's the discrepancy."

---

#### Step 3 — Run reconciliation (1:10 – 1:20)

> "We trigger the reconciliation."

*Action: Click "Run medication reconciliation". Let the spinner run. Wait for result to appear.*

---

#### Step 4 — Results: discrepancy + risk (1:20 – 1:40)

**Screen:** Results tab, discrepancy card.

> "The agent detected the discrepancy: ibuprofen discontinued at discharge but still taken by the patient. Risk level: HIGH."

*Action: Point to the risk badge (HIGH). Scroll to the professional checklist.*

> "The professional checklist flags: anti-inflammatory drug combined with active anticoagulant — review urgently."

---

#### Step 5 — Patient summary (1:40 – 1:50)

**Screen:** Scroll to patient summary section.

> "The patient summary is plain language — no prescriptive instructions. No 'stop taking', no 'start taking', no 'it is safe to continue'. Just: there may be a question about one of your medications — please confirm with your pharmacist or GP."

---

#### Step 6 — Agent trace (1:50 – 2:10)

**Screen:** Scroll to agent trace section.

> "Every run generates a tool trace. You can see each step: get_discharge_summary, get_active_prescription, get_patient_interview, extract_medications, detect_discrepancies, score_discrepancy_risk, run_policy_check. Full audit trail."

---

### [2:10 – 2:35] Part 4 — Safety and evaluation

**Screen:** Evaluation tab in the app.

**Narration:**
> "The evaluation runner validates the full pipeline against a gold standard — 36 checks: 10 end-to-end pipeline evals and 6 safety policy checks. Discrepancy recall 100%. Risk classification 100%. Safety policy 6/6."

*Action: Show the Evaluation tab or run `python evals/run_evals.py` in terminal.*

> "The Policy Server blocks prescriptive language in every patient output. It runs as a mandatory tool call — the agent is instructed to retry until the check passes."

---

### [2:35 – 2:55] Part 4b — Drug search (Tab 5)

**Screen:** Click Tab 5 "Drug Search" in the Streamlit app.

**Narration:**
> "Tab 5 uses a separate agent with Gemini's Google Search grounding to look up pharmacological information. Ask it about apixaban interactions."

*Action: Type "apixaban interaction with NSAIDs" in the search box and run. Show the grounded response.*

> "This is the same grounding tool from the Day 2 notebook — live web retrieval, cited sources."

---

### [2:55 – 3:15] Part 5 — Course concepts

**Screen:** Show `README.md` or a pre-made summary slide.

**Narration:**
> "Six course concepts, six green checkboxes."

*Action: Read or point to each row:*

```
ADK multi-agent system  →  SequentialAgent + 8 LlmAgents (agents/orchestrator.py)
MCP Server              →  read-only SQLite, 9 tools (mcp/mcp_server.py)
Agent Skill             →  .agent/skills/medication-reconciliation/SKILL.md
Security features       →  Policy Server + prompt injection detection (input_sanitizer.py)
Deployable app          →  streamlit run app.py — 6 tabs, 152 tests green
Antigravity workflow    →  spec-first: blueprint → SKILL.md → agents → tests → app
```

---

### [3:15 – 3:30] Part 6 — Closing

**Screen:** Return to app with case_001 result visible.

**Narration:**
> "Real deployment would require clinical governance, GDPR compliance, EHR integration, professional validation, and a phased rollout. The agent stays a decision-support tool — it flags, explains, and asks for review. It never prescribes."

---

## Timing summary

| Section | Duration | Running total |
|---------|----------|---------------|
| Problem | 0:30 | 0:30 |
| Architecture | 0:15 | 0:45 |
| Live demo (case_001) | 1:25 | 2:10 |
| Safety + evals | 0:25 | 2:35 |
| Drug search (Tab 5) | 0:20 | 2:55 |
| Course concepts | 0:20 | 3:15 |
| Closing | 0:15 | 3:30 |

---

## Fallback notes

**If the LLM agent times out or fails:**
- Show `python demo/run_case.py case_001` in terminal — it runs the deterministic pipeline without the LLM and prints the full structured output.
- Say: "This is the deterministic layer underneath the agent — it runs without any API call."
- For Tab 5 (drug search), if it fails: skip it and spend the extra 20 seconds on the agent trace.

**If Streamlit fails to start:**
- Run `python evals/run_evals.py` in terminal and narrate from the terminal output.
- All 15 checks are visible in the output — sufficient to demonstrate the pipeline.

**If GOOGLE_API_KEY is not available:**
- The deterministic pipeline (`tools/report_generation.py`) runs without it.
- The LLM agents require it. Note in narration that the evaluation suite is entirely deterministic.

---

## Test suite summary (for Kaggle notebook or README)

```
$ pytest tests/ -q
152 passed

$ python evals/run_evals.py
RESULT: PASS — 36/36 evaluations
```

Coverage by area:
- `test_mcp_read_only.py` — MCP server, 9 tools, read-only enforcement
- `test_extraction.py` — medication extraction and normalization
- `test_reconciliation.py` — discrepancy detection, run_full_analysis
- `test_risk_scoring.py` — risk classification for all discrepancy types
- `test_policy_server.py` — forbidden phrase detection, HIGH-risk required phrases
- `test_drug_interactions.py` — NLM RxNorm API + static fallback
- `test_input_sanitizer.py` — prompt injection detection (18 patterns)
- Integration tests (4) — end-to-end with real LLM (requires GOOGLE_API_KEY)
