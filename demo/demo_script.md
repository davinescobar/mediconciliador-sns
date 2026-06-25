# Demo Script — MediConciliador SNS (Kaggle Capstone)

**Target duration:** 3:50 – 4:30 min (max 5:00 — YouTube required)  
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

Have open in a text editor or browser tab (zoomed in, full screen) for Part 2:
```
MediConciliadorOrchestrator  (SequentialAgent)
├── DataCollectionAgent      LlmAgent + MCPToolset  →  state: case_data
├── AnalysisAgent            LlmAgent + run_full_analysis  →  state: analysis_results
└── CommunicationAgent       LlmAgent + run_policy_check  →  state: reconciliation_report

Standalone (Tab 5 in Streamlit):
└── DrugInfoSearchAgent      LlmAgent + google_search (grounded)
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

### [0:30 – 1:05] Part 2 — Why agents + architecture

**Screen:** Switch to a text editor or browser tab showing the architecture diagram (pasted below in large font, full screen). Keep it visible for the full section. In VS Code: open `submission/kaggle_writeup.md`, navigate to section 2, and zoom in with ⌘+= until the diagram fills the screen.

```
MediConciliadorOrchestrator  (SequentialAgent)
├── DataCollectionAgent      LlmAgent + MCPToolset  →  state: case_data
├── AnalysisAgent            LlmAgent + run_full_analysis  →  state: analysis_results
└── CommunicationAgent       LlmAgent + run_policy_check  →  state: reconciliation_report

Standalone (Tab 5 in Streamlit):
└── DrugInfoSearchAgent      LlmAgent + google_search (grounded)
```

**Narration:**
> "Why agents and not a simple script? A script could compare two formatted lists. But the real inputs here are unstructured: a PDF discharge summary, a handwritten prescription, and what a patient reports in an interview. Parsing those documents, normalizing drug names across brand names and generics, and generating output that adapts its language to two completely different audiences — a clinician and a patient — is a coordination problem. Each step depends on the previous one. Agents handle that dependency chain natively."

> "The system is built on Google's Agent Development Kit. A SequentialAgent orchestrator coordinates three specialized LLM agents: DataCollectionAgent reads the three source documents through the MCP server; AnalysisAgent runs the deterministic reconciliation pipeline; CommunicationAgent generates the professional checklist and the patient summary, enforced by the Policy Server. A fourth agent — DrugInfoSearchAgent — handles pharmacological queries using Gemini's live web grounding."

> "All data is synthetic. The MCP server is read-only. The agent does not write to any database."

---

### [1:05 – 2:30] Part 3 — Live demo (case_001)

**Screen:** Switch to browser — Streamlit app.

#### Step 1 — Case selection (1:05 – 1:15)

> "Let's run the most clinically significant case: case_001. A patient discharged with apixaban — a blood thinner — who is still taking ibuprofen, an anti-inflammatory they were told to stop."

*Action: Select `case_001` from the dropdown.*

---

#### Step 2 — Source documents (1:15 – 1:30)

> "The Sources tab shows the three inputs: the hospital discharge summary, the active prescription, and what the patient reported in the interview."

*Action: Click the Sources tab. Pan across the three columns slowly. Highlight the ibuprofen row.*

> "Ibuprofen is absent from the discharge summary — the hospital stopped it. But the patient is still taking it. That's the discrepancy."

---

#### Step 3 — Run reconciliation (1:30 – 1:40)

> "We trigger the reconciliation."

*Action: Click "Run medication reconciliation". Let the spinner run. Wait for result to appear.*

---

#### Step 4 — Results: discrepancy + risk (1:40 – 2:00)

**Screen:** Results tab, discrepancy card.

> "The agent detected the discrepancy: ibuprofen discontinued at discharge but still taken by the patient. Risk level: HIGH."

*Action: Point to the risk badge (HIGH). Scroll to the professional checklist.*

> "The professional checklist flags: anti-inflammatory drug combined with active anticoagulant — review urgently."

---

#### Step 5 — Patient summary (2:00 – 2:10)

**Screen:** Scroll to patient summary section.

> "The patient summary is plain language — no prescriptive instructions. No 'stop taking', no 'start taking', no 'it is safe to continue'. Just: there may be a question about one of your medications — please confirm with your pharmacist or GP."

---

#### Step 6 — Agent trace (2:10 – 2:30)

**Screen:** Scroll to agent trace section.

> "Every run generates a tool trace. You can see each step: get_discharge_summary, get_active_prescription, get_patient_interview, extract_medications, detect_discrepancies, score_discrepancy_risk, run_policy_check. Full audit trail."

---

### [2:30 – 2:55] Part 4 — Safety and evaluation

**Screen:** Evaluation tab in the app.

**Narration:**
> "The evaluation runner validates the full pipeline against a gold standard — 36 checks: 10 end-to-end pipeline evals and 6 safety policy checks. Discrepancy recall 100%. Risk classification 100%. Safety policy 6/6."

*Action: Show the Evaluation tab or run `python evals/run_evals.py` in terminal.*

> "The Policy Server blocks prescriptive language in every patient output. It runs as a mandatory tool call — the agent is instructed to retry until the check passes."

---

### [2:55 – 3:15] Part 4b — Drug search (Tab 5)

**Screen:** Click Tab 5 "Drug Search" in the Streamlit app.

**Narration:**
> "Tab 5 uses a separate agent with Gemini's Google Search grounding to look up pharmacological information. Ask it about apixaban interactions."

*Action: Type "apixaban interaction with NSAIDs" in the search box and run. Show the grounded response.*

> "This is the same grounding tool from the Day 2 notebook — live web retrieval, cited sources."

---

### [3:15 – 3:35] Part 5 — The build

**Screen:** Show `README.md` or a pre-made summary slide.

**Narration:**
> "Six course concepts, six green checkboxes. Here's how it was built."

*Action: Read or point to each row:*

```
ADK multi-agent system  →  SequentialAgent + 3 LlmAgents + DrugInfoSearchAgent
MCP Server              →  read-only SQLite, 9 tools (mcp/mcp_server.py)
Agent Skill             →  .agent/skills/medication-reconciliation/SKILL.md
Security features       →  Policy Server + prompt injection detection (input_sanitizer.py)
Deployable app          →  streamlit run app.py — 6 tabs, 152 tests green
Antigravity workflow    →  spec-first: blueprint → SKILL.md → agents → tests → app
```

> "The project followed a spec-first sequence — the full architecture was documented before a single line of code was written. The deterministic analysis pipeline replaced an early LLM-based version after the first evaluation run revealed non-reproducible outputs. The Policy Server moved from prompt instructions to a tool-enforced loop after realizing the model could ignore instructions but cannot skip tool calls."

---

### [3:35 – 3:50] Part 6 — Closing

**Screen:** Return to app with case_001 result visible.

**Narration:**
> "Real deployment would require clinical governance, GDPR compliance, EHR integration, professional validation, and a phased rollout. The agent stays a decision-support tool — it flags, explains, and asks for review. It never prescribes."

---

## Timing summary

| Section | Duration | Running total |
|---------|----------|---------------|
| Problem | 0:30 | 0:30 |
| Why agents + Architecture | 0:35 | 1:05 |
| Live demo (case_001) | 1:25 | 2:30 |
| Safety + evals | 0:25 | 2:55 |
| Drug search (Tab 5) | 0:20 | 3:15 |
| The build | 0:20 | 3:35 |
| Closing | 0:15 | 3:50 |

---

## Fallback notes

**If the LLM agent times out or fails:**
- Show `python demo/run_case.py case_001` in terminal — it runs the deterministic pipeline without the LLM and prints the full structured output.
- Say: "This is the deterministic layer underneath the agent — it runs without any API call."
- For Tab 5 (drug search), if it fails: skip it and spend the extra 20 seconds on the agent trace.

**If Streamlit fails to start:**
- Run `python evals/run_evals.py` in terminal and narrate from the terminal output.
- All 36 checks are visible in the output — sufficient to demonstrate the pipeline.

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
