# MediConciliador SNS

**Safe Medication Reconciliation Agent for Older Polymedicated Patients after Hospital Discharge**

Kaggle Vibe Coding Agents Capstone — built with [Google ADK](https://google.github.io/adk-docs/).

---

## What it does

Compares three medication sources for older patients after hospital discharge:

1. Hospital discharge summary
2. Active prescription list
3. Patient or caregiver interview

Detects discrepancies, classifies risk (LOW / MEDIUM / HIGH), and generates two safe outputs:
- **Professional checklist** for clinician review
- **Patient-safe explanation** in plain Spanish (validated by a deterministic Policy Server)

Uses synthetic data only. No real patient data. No prescribing.

---

## Why it matters

Medication reconciliation failures at hospital discharge are one of healthcare's most preventable sources of harm:

- The **WHO** estimates medication errors cost **$42 billion per year** globally — nearly 1% of total health expenditure ([Medication Without Harm](https://www.who.int/initiatives/medication-without-harm)).
- The **OECD** estimates **1 in 10 hospitalizations** in member countries may be caused by medication-related harm, with avoidable costs exceeding **$54 billion per year** ([OECD, 2022](https://www.oecd.org/en/publications/2022/09/the-economics-of-medication-safety_e79d5329.html)).
- In **Spain**, the ENEAS national study found **37.4% of all hospital adverse events** were medication-related — and **42.8%** were preventable.
- Spanish Ministry of Health data report reconciliation errors reaching **63% of patients at hospital discharge** in high-risk populations.
- **29.7%** of people over 65 in Spain are chronically polymedicated; the figure reaches **44.7%** among those aged 85–94.
- Systematic reviews find approximately **1 in 2 older patients** experiences a medication error in the weeks after discharge, with omissions — a drug simply missing from the new prescription — accounting for nearly half of all discrepancies.
- In the **United States**, the Institute of Medicine (now National Academy of Medicine) estimated **1.5 million preventable adverse drug events per year**. The Joint Commission has made medication reconciliation a **National Patient Safety Goal since 2005**. Drug interaction checking uses the **NLM RxNorm** database — the US National Library of Medicine's standard drug terminology, used here via its free public REST API.

The critical window is the transition home: new drugs added, others discontinued, prescriptions not yet updated, and patients who may not understand which version of their regimen is the right one. MediConciliador SNS automates the comparison of the three sources that together reveal these gaps.

---

## Kaggle capstone requirements

| Requirement | Implementation |
|-------------|---------------|
| ADK multi-agent system | `SequentialAgent` → `DataCollectionAgent` → `AnalysisAgent` → `CommunicationAgent` |
| MCP Server | `mcp/mcp_server.py` — read-only FastMCP server backed by SQLite |
| Agent Skill | `.agent/skills/medication-reconciliation/SKILL.md` |
| Security features | `policy/policy_server.py` — forbidden phrase detection + required disclaimer enforcement; `tools/input_sanitizer.py` — prompt injection detection for user-uploaded documents |
| Deployable app | `streamlit run app.py` — 5-tab Streamlit UI |
| Antigravity workflow | Spec-driven development with skills, `.agents/AGENTS.md`, `specs/` |

---

## Agent architecture

```
MediConciliadorOrchestrator  (SequentialAgent)
├── DataCollectionAgent      LlmAgent + MCPToolset (reads 5 MCP tools)
├── AnalysisAgent            LlmAgent + run_full_analysis (deterministic pipeline)
└── CommunicationAgent       LlmAgent + run_policy_check (policy enforcement loop)

Standalone:
└── DrugInfoSearchAgent      LlmAgent + google_search (grounded, Day 2a of course)
```

Deterministic pipeline inside `AnalysisAgent`:
```
extract_medications → normalize_medication_list → detect_discrepancies
→ score_discrepancy_risk → build_reconciliation_table → format_reconciliation_report
```

---

## Demo cases

| Case | Scenario | Risk |
|------|----------|------|
| `case_001` | NSAID (ibuprofen OTC) + anticoagulant (apixaban) — patient still taking discontinued NSAID | HIGH |
| `case_002` | Diuretic (furosemide) omitted at discharge — heart failure patient | HIGH |
| `case_003` | Brand/generic duplication (omeprazole) — OTC stomach protector vs. prescription PPI | LOW |

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# edit .env and add your GOOGLE_API_KEY

# 3. Run the app
streamlit run app.py
```

The SQLite database (`data/mediconciliador.db`) is pre-populated with the three demo cases. No extra setup needed.

To regenerate it from source JSON:
```bash
python mcp/db_init.py
```

---

## Run tests and evals

```bash
# Unit + integration tests (no API key required)
pytest tests/ -v

# Evaluation vs. gold standard (no API key required)
python evals/run_evals.py
```

Results: 127/127 tests, 36/36 evals.

---

## Project structure

```
agents/
  orchestrator.py          SequentialAgent wiring
  discharge_parser_agent.py  DataCollectionAgent (LlmAgent + MCPToolset)
  reconciliation_agent.py    AnalysisAgent
  communication_agent.py     CommunicationAgent (policy check loop)
  drug_search_agent.py       DrugInfoSearchAgent (google_search)
  callbacks.py               ADK before/after_tool callbacks (observability)

tools/
  medication_extraction.py   Extract structured med lists from MCP output
  medication_normalization.py  Brand → generic mapping
  discrepancy_detection.py   Rules-based discrepancy detection
  risk_scoring.py            Rules-based risk scoring (LOW/MEDIUM/HIGH)
  report_generation.py       Full pipeline + run_full_analysis tool
  drug_interactions.py       NLM RxNorm API + static fallback for interaction checking
  input_sanitizer.py         Prompt injection detection for user-uploaded documents
  policy_check.py            run_policy_check ADK tool wrapper
  trace_logger.py            Tool call trace for observability

mcp/
  mcp_server.py    FastMCP server (read-only SQLite, 9 tools)
  db_init.py       Populates SQLite from JSON source files

policy/
  policy_server.py          Deterministic safety filter
  policies.yaml             Required phrases for HIGH-risk outputs
  forbidden_phrases.yaml    Blocked directives (prescriptive language)

data/
  synthetic_cases.json            3 demo cases (no real patient data)
  gold_standard_discrepancies.json  Expected discrepancies for eval
  high_risk_medications.json        High-risk drug reference list
  mediconciliador.db                Pre-populated SQLite (from db_init.py)

evals/
  run_evals.py       Evaluation runner (precision, recall, safety)
  eval_cases.json    Policy server test cases
  safety_tests.json  Safety behavior checks

.agent/skills/medication-reconciliation/
  SKILL.md           Agent skill definition (Antigravity workflow)
  references/        Reconciliation principles, discrepancy types, safe language

app.py             Streamlit app (5 tabs)
```

---

## Safety constraints

- Synthetic data only. No real patient data.
- Read-only MCP server. No database writes.
- Agent does not prescribe, discontinue, or change medication.
- All HIGH-risk discrepancies require professional review.
- Policy Server blocks prescriptive language in patient outputs at the tool level.
- `before_tool_callback` / `after_tool_callback` log every tool invocation for audit.
