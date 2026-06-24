# Screenshots Guide — MediConciliador SNS

Capture these screenshots before recording the video. They double as assets for
the Kaggle writeup (section images) and as reference frames during editing.

Save all screenshots to `demo/screenshots/` (create the folder).
Name each file as shown — the order matches the submission writeup structure.

---

## Pre-flight

```bash
cd mediconciliador-sns
source .venv/bin/activate
python mcp/mcp_server.py &
streamlit run app.py
```

Open browser at http://localhost:8501 — full screen, 1080p resolution.
Set browser zoom to 100%.

---

## Group 1 — App overview

### SS-01 — Tab 1: Case selection (clean state)
**What to show:** Tab 1 active, dropdown visible, case_001 selected, button visible.
**Zoom:** None. Full app width.
**Used for:** Writeup section 3.5 (Deployable App). Video 0:45.

### SS-02 — Tab 1: Dropdown open
**What to show:** Dropdown expanded showing case_001 through case_010 with titles in English.
**Used for:** Shows the 10 synthetic cases. Useful for social media / README.

---

## Group 2 — Source documents (Tab 2)

### SS-03 — Tab 2: Three columns, case_001
**What to show:** Sources tab with case_001 loaded. Three columns side by side:
- Discharge Summary (apixaban, bisoprolol, omeprazole; ibuprofen DISCONTINUED)
- Active Prescription (apixaban, bisoprolol, omeprazole)
- Patient Interview (adds ibuprofen 600 mg)
**Zoom in:** Highlight the ibuprofen row in the interview column.
**Used for:** Video 0:55–1:10. Writeup section 3.1 (architecture diagram alternative).

---

## Group 3 — Reconciliation results (Tab 3)

### SS-04 — Tab 3: Full results, case_001
**What to show:** Complete results tab — discrepancy table, risk badge (HIGH), professional checklist, patient summary.
**Used for:** Writeup section 6 (Results). Video 1:20.

### SS-05 — Tab 3: Discrepancy card close-up
**What to show:** The ibuprofen discrepancy card zoomed in. Must show:
- Discrepancy type: "Medication discontinued at discharge still reported by patient"
- Medications: ibuprofen
- Risk level: **HIGH** (red badge)
**Used for:** Key visual for the Kaggle writeup. Twitter/LinkedIn.

### SS-06 — Tab 3: Professional checklist
**What to show:** The professional checklist section — clinical rationale, urgent flags.
**Used for:** Writeup section 3.4 (Security / CommunicationAgent output).

### SS-07 — Tab 3: Patient summary
**What to show:** The patient-facing plain-language summary. Must NOT show any prescriptive language ("stop taking", "start taking", etc.)
**Caption:** "Policy-enforced output: no prescriptive language."
**Used for:** Writeup section 3.4 (Security / Policy Server).

### SS-08 — Tab 3: Agent trace
**What to show:** The tool trace section showing the full sequence of tool calls. Should include:
get_discharge_summary → get_active_prescription → get_patient_interview → run_full_analysis → run_policy_check
**Caption:** "Full audit trail — every tool call logged with timestamp."
**Used for:** Writeup section 3.6 (Callbacks). Video 1:50–2:10.

---

## Group 4 — Evaluation (Tab 4)

### SS-09 — Tab 4: Evaluation dashboard
**What to show:** Evaluation results — 36/36 green. Discrepancy recall 100%, risk classification 100%, policy safety 6/6.
**Used for:** Writeup section 6 (Results). Video 2:10–2:35.

### SS-10 — Terminal: pytest 152 green
**What to show:** Terminal output of `pytest tests/ -q` — all 152 passed, no failures.
```
$ pytest tests/ -q
...
152 passed in X.XXs
```
**Used for:** Writeup section 6. README badge alternative. GitHub README.

### SS-11 — Terminal: evals 36/36
**What to show:** Terminal output of `python evals/run_evals.py` — RESULT: PASS — 36/36.
**Used for:** Writeup section 6. Video 2:10.

---

## Group 5 — Drug search (Tab 5)

### SS-12 — Tab 5: Search query
**What to show:** Search box with query typed: "apixaban interaction with NSAIDs"
**Used for:** Video 2:35–2:55.

### SS-13 — Tab 5: Grounded response
**What to show:** DrugInfoSearchAgent response with cited sources (URLs from web grounding).
**Caption:** "Gemini google_search grounding — live web results, cited sources."
**Used for:** Writeup section 3.6 (Grounding, Day 2a). Video 2:55.

---

## Group 6 — New case Tab 6 (live document demo)

### SS-14 — Tab 6: Upload interface (empty)
**What to show:** Tab 6 open, three upload/paste areas visible — Discharge Summary, Active Prescription, Patient Interview.
**Used for:** Video if you demo Tab 6. Writeup section 3.4 (prompt injection).

### SS-15 — Tab 6: Paste case_001 documents
**What to show:** All three text areas filled with the content from
`demo/fake_documents/case_001_nsaid_anticoagulant/`.
- Paste `01_discharge_summary.txt` into Discharge Summary
- Paste `02_active_prescription.txt` into Active Prescription
- Paste `03_patient_interview.txt` into Patient Interview
**Used for:** Demo of Tab 6 — shows real document upload workflow.

### SS-16 — Tab 6: Result after extraction
**What to show:** After clicking "Extract & Analyze" — the agent has extracted medication data from the free text and produced a reconciliation result.
Ideally: same ibuprofen discrepancy detected, HIGH risk, same output as Tab 3.
**Caption:** "Upload free-text clinical documents → automatic extraction + reconciliation."
**Used for:** Writeup section 3.5 (Deployable App / Tab 6). Best for the video if you have time.

---

## Group 7 — Security / code

### SS-17 — Policy Server blocking output
**What to show:** If possible, show the policy check in action — the UI warning when a document with an injection pattern is uploaded, or the policy check result displayed in Tab 3.
**Caption:** "PolicyServer: two-layer safety filter — deterministic + semantic LLM audit."
**Used for:** Writeup section 3.4 (Security).

### SS-18 — Code: orchestrator.py
**What to show:** The SequentialAgent definition in `agents/orchestrator.py` — specifically the `SequentialAgent(sub_agents=[...])` constructor.
**Used for:** Writeup section 3.1 (ADK multi-agent).

### SS-19 — Code: mcp_server.py
**What to show:** One `@mcp.tool()` decorated function in `mcp/mcp_server.py` — showing the FastMCP pattern and the SQLite read-only URI.
**Used for:** Writeup section 3.2 (MCP Server).

### SS-20 — Code: input_sanitizer.py
**What to show:** The regex patterns list in `tools/input_sanitizer.py` (the `INJECTION_PATTERNS` list).
**Caption:** "18 compiled regex patterns for prompt injection detection."
**Used for:** Writeup section 3.4 (Security / prompt injection).

---

## Group 8 — Architecture

### SS-21 — Project tree
**What to show:** Terminal output of `tree -L 2 --dirsfirst` (or equivalent) showing the project structure.
```
mediconciliador-sns/
├── agents/
├── mcp/
├── tools/
├── policy/
├── .agent/skills/
├── evals/
├── tests/
└── app.py
```
**Used for:** Video 0:30–0:45. Writeup section 2 (Architecture).

### SS-22 — GitHub repo (public)
**What to show:** Browser showing https://github.com/davinescobar/mediconciliador-sns — public repo, main branch, README visible.
**Used for:** Submission proof of public repository.

---

## Capture order for efficiency

Record in this order to minimise app switching:

1. Start app → SS-01, SS-02
2. Click Sources tab, load case_001 → SS-03
3. Run reconciliation, wait → SS-04, SS-05, SS-06, SS-07, SS-08
4. Click Evaluation tab → SS-09
5. Switch to terminal → SS-10, SS-11, SS-21
6. Back to browser, Tab 5 → SS-12, SS-13
7. Tab 6, paste documents → SS-14, SS-15, SS-16
8. VS Code or terminal, show code → SS-18, SS-19, SS-20
9. Browser, GitHub → SS-22
10. If needed, show policy warning → SS-17

---

## Notes for Kaggle writeup images

The Kaggle submission form accepts images inline in the writeup notebook.
The most important screenshots for the writeup are:

| Priority | Screenshot | Section |
|----------|-----------|---------|
| MUST HAVE | SS-05 (discrepancy HIGH) | Results |
| MUST HAVE | SS-09 (36/36 evals) | Results |
| MUST HAVE | SS-10 (152 tests) | Results |
| MUST HAVE | SS-08 (agent trace) | Architecture |
| MUST HAVE | SS-13 (drug search grounded) | Section 3.6 |
| NICE TO HAVE | SS-07 (patient summary — no prescriptive language) | Security |
| NICE TO HAVE | SS-16 (Tab 6 result) | Deployable app |
| NICE TO HAVE | SS-21 (project tree) | Architecture |
