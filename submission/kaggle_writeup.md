# MediConciliador SNS — Kaggle Vibe Coding Agents Capstone

**Track:** Agents for Good  
**Repository:** https://github.com/davinescobar/mediconciliador-sns

---

## 1. The Problem

Every year, millions of older patients are discharged from hospitals in Spain carrying a medication list that does not match what they were actually taking before admission. The hospital adds new drugs, discontinues others, and changes doses — but the primary care record, the pharmacy prescription, and the patient's own understanding of their regimen often diverge in dangerous ways.

This is known as *medication reconciliation*: the process of comparing a patient's medication orders to all of the medications the patient has been taking, and resolving any discrepancies. It is particularly critical for elderly polymedicated patients — those taking five or more drugs — because the interactions and omissions that go unnoticed at discharge become the leading cause of preventable hospital readmissions within 30 days.

The clinical consequences are severe. A patient with heart failure whose diuretic was inadvertently dropped from the discharge summary will return in acute decompensation within days. A patient still taking an over-the-counter NSAID who was prescribed an anticoagulant during hospitalization faces a significant bleeding risk. A duplicated proton pump inhibitor — brand name in the prescription, generic equivalent from the pharmacy OTC shelf — contributes to polypharmacy without benefit.

In Spain's National Health System (SNS), this reconciliation task falls on primary care pharmacists and general practitioners. It is largely manual, time-consuming, and dependent on the patient or caregiver being able to accurately report everything they take. The information is fragmented across three sources that rarely agree: the hospital discharge summary, the active prescription on file with the primary care physician, and what the patient actually says during the follow-up interview.

MediConciliador SNS is a multi-agent AI system that automates the comparison of these three sources, detects discrepancies with clinical context, classifies risk, and generates two safe outputs: a structured checklist for the clinician and a plain-language summary for the patient. It is built for demonstration and educational purposes using synthetic data only.

### Scale of the problem

The evidence for this problem is strong and well-documented. The World Health Organization estimates medication errors cost **$42 billion per year** globally — nearly 1% of total health expenditure — and has made medication safety in polypharmacy and care transitions a global patient safety priority ([WHO, *Medication Without Harm*](https://www.who.int/initiatives/medication-without-harm)). The OECD estimates that **1 in 10 hospitalizations** in member countries may be caused by medication-related harm, with preventable costs exceeding **$54 billion per year** from avoidable admissions and extended stays ([OECD, 2022](https://www.oecd.org/en/publications/2022/09/the-economics-of-medication-safety_e79d5329.html)).

In Spain, the ENEAS national study found that **37.4% of all hospital adverse events were medication-related**, and **42.8% were preventable**. Spanish Ministry of Health guidance documents — developed with ISMP-España — report that reconciliation errors can reach **63% of patients at hospital discharge** in high-risk populations. Of Spain's roughly 9 million people over 65, **29.7% are chronically polymedicated** (five or more active drugs); among those aged 85–94, the figure reaches **44.7%**.

Systematic reviews on post-discharge safety find that approximately **1 in 2 older patients** experiences a medication error in the weeks after hospital discharge, with omissions — a drug simply absent from the updated prescription — accounting for nearly half of all reconciliation discrepancies (Michaelsen et al., *Pharmacy*, 2015; Alqenae et al., *Drug Safety*, 2020). These errors rarely surface until a patient returns to primary care, calls a pharmacist, or is readmitted to the emergency department.

The problem is equally documented in the **United States**: the Institute of Medicine (now National Academy of Medicine) estimated **1.5 million preventable adverse drug events per year** across US healthcare settings. The Joint Commission designated medication reconciliation a **National Patient Safety Goal in 2005**, and it remains one today. Drug interaction checking in MediConciliador SNS uses the **NLM RxNorm API** — the US National Library of Medicine's standard drug terminology, freely available with no authentication — so the system works with both US and international drug names out of the box.

---

## 2. System Architecture

MediConciliador SNS is built on Google's Agent Development Kit (ADK) and follows a SequentialAgent pipeline in which three specialized LlmAgents pass structured state to one another through ADK's session state mechanism.

```
MediConciliadorOrchestrator  (SequentialAgent)
├── DataCollectionAgent      LlmAgent + MCPToolset  →  state: case_data
├── AnalysisAgent            LlmAgent + run_full_analysis  →  state: analysis_results
└── CommunicationAgent       LlmAgent + run_policy_check  →  state: reconciliation_report

Standalone (Tab 5 in Streamlit):
└── DrugInfoSearchAgent      LlmAgent + google_search (grounded)
```

**DataCollectionAgent** connects to the MCP server via MCPToolset and calls five tools in sequence — discharge summary, active prescription, patient interview, allergies, high-risk medication reference — collecting all clinical data for a case into a single JSON object stored in session state.

**AnalysisAgent** reads that JSON and calls `run_full_analysis`, a deterministic Python pipeline that extracts medication lists from each source, normalizes brand names to generics, detects discrepancies by type (omission, addition, duplication, discontinuation), and scores each discrepancy's risk level as LOW, MEDIUM, or HIGH. No LLM is involved in this step — the analysis is rule-based and produces identical results on every run.

**CommunicationAgent** reads the analysis results and generates two outputs: a professional checklist with clinical rationale for each discrepancy, and a plain-Spanish patient summary. Before finalizing the output, it is required by its instruction to call `run_policy_check`, a deterministic safety tool that validates the patient text against a YAML-defined list of forbidden phrases and required disclaimers. If the check fails, the agent revises and retries until it passes.

A **PolicyServer** sits behind `run_policy_check` and adds a second semantic layer: for text that passes the structural forbidden-phrase check, it calls an independent Gemini instance to detect implicit clinical directives not caught by the explicit rule set.

The **MCP Server** (`mcp/mcp_server.py`) is a FastMCP server backed by SQLite. All 9 tools are read-only, enforced at the SQLite URI level (`mode=ro`). The server runs as a subprocess launched by the ADK agent's MCPToolset.

The **Streamlit app** (`app.py`) provides a 5-tab UI: case selection, source documents, reconciliation results, evaluation dashboard, and pharmacological search. A sixth tab allows clinicians to upload or paste documents from real (non-production) cases for ad-hoc analysis using a GPT-based extraction step.

---

## 3. Six Course Concepts Implemented

### 3.1 ADK Multi-Agent System (Day 1 + Day 3)

**Files:** `agents/orchestrator.py`, `agents/discharge_parser_agent.py`, `agents/reconciliation_agent.py`, `agents/communication_agent.py`

The orchestrator uses ADK's `SequentialAgent` to guarantee that each sub-agent runs in order, with the output of each step available to the next via `output_key`. DataCollectionAgent writes to `case_data`; AnalysisAgent reads `{case_data}` in its instruction template and writes to `analysis_results`; CommunicationAgent reads `{analysis_results}` and writes to `reconciliation_report`.

This is the core multi-agent pattern from Day 3: state flows through the pipeline without any explicit message-passing code. The SequentialAgent handles the scheduling; the `output_key` parameter on each `LlmAgent` handles the state write; the `{key}` placeholder in the next agent's instruction handles the read.

### 3.2 MCP Server (Day 2b)

**Files:** `mcp/mcp_server.py`, `mcp/mcp_client.py`, `mcp/db_init.py`

The MCP server exposes 9 read-only tools over the MCP protocol using `FastMCP`. Each tool is defined with a single `@mcp.tool()` decorator and delegates to a private `_fetch_*` function that connects to SQLite with a read-only URI. The read-only constraint is enforced at the database connection level, not in application logic — no code path can accidentally write to the database.

DataCollectionAgent connects to the server via `McpToolset` with `StdioServerParameters`, which launches the MCP server as a subprocess. From the agent's perspective, the 9 MCP tools appear alongside any other ADK tools.

The private `_fetch_*` functions are importable by the test suite without starting the MCP server, which is why the 35 MCP-specific tests run in under a second.

### 3.3 Agent Skill (Antigravity Workflow)

**Files:** `.agent/skills/medication-reconciliation/SKILL.md`, `specs/00_project_blueprint.md`

The project follows the spec-first Antigravity workflow introduced in the course. The entire system was designed before a single line of code was written: the blueprint (`specs/00_project_blueprint.md`) defines the problem, the architecture, the data model, the tool taxonomy, the safety constraints, and the evaluation criteria.

The SKILL.md file formalizes the agent's capability as a reusable skill: it defines the skill's inputs (three clinical documents), outputs (professional checklist + patient summary), constraints (no prescribing, no real data), and the invocation protocol. Six additional validation skills in `.agent/skills/validate-*/` document exactly how each Kaggle capstone requirement is met, one per concept.

### 3.4 Security Features (Day 5)

**Files:** `policy/policy_server.py`, `policy/forbidden_phrases.yaml`, `policy/policies.yaml`, `tools/policy_check.py`

The PolicyServer implements a two-layer safety filter. Layer 1 is deterministic: it checks patient-facing text against a YAML list of forbidden phrases in Spanish and English (e.g., "deje de tomar", "stop taking", "cambie la dosis") and verifies that HIGH-risk outputs contain three required professional-review disclaimers. Layer 2 is semantic: it calls an independent Gemini instance with a clinical auditor prompt to detect implicit directives that evade the structural filter.

Crucially, policy enforcement is wired into the agent's tool loop, not just mentioned in the prompt. CommunicationAgent's instruction requires it to call `run_policy_check` and retry until `passed=true` — the LLM cannot finalize output without a policy-passing result. This implements the tool-enforced safety loop described in Day 5.

**Prompt injection protection for user-uploaded documents.** The "New Case" tab allows clinicians to upload or paste free-text clinical documents. Before any LLM call, `tools/input_sanitizer.py` scans each document for injection patterns (e.g., "ignore previous instructions", "you are now", `<system>` tags, developer-mode triggers) using compiled regex with 18 signatures. Detected patterns produce a visible UI warning. The extraction prompt additionally wraps the document in `<DOCUMENT>` delimiters with an explicit instruction to ignore any commands embedded in the content — a defense-in-depth approach that treats the LLM as the second line of defense, not the first.

**NLM RxNorm drug interaction checking.** The deterministic analysis pipeline calls `tools/drug_interactions.py` after risk scoring to enrich the reconciliation report with a `drug_interactions` field. It first queries the public NLM RxNorm REST API (free, no authentication required) with a 4-second timeout: CUI lookup at `/REST/rxcui.json`, then interaction pairs at `/REST/interaction/list.json`. On any network failure or timeout, it falls back to the static `data/high_risk_medications.json` table, which cross-references 20 drug categories (anticoagulants, NSAIDs, SSRIs, azole antifungals, etc.) using their `key_interactions` fields. The fallback ensures the feature is available during demos without internet access.

### 3.5 Deployable App

**Files:** `app.py`, `requirements.txt`

The Streamlit application (`streamlit run app.py`) provides a complete UI over the agent pipeline. Tab 1 selects a synthetic case; Tab 2 shows the raw source documents; Tab 3 displays the reconciliation results with a color-coded discrepancy table; Tab 4 shows the evaluation metrics; Tab 5 runs DrugInfoSearchAgent with live Google Search grounding; Tab 6 accepts PDF or plain text uploads and runs an extraction + analysis flow.

The app runs the ADK pipeline in a background thread using `asyncio.run_coroutine_threadsafe` to avoid blocking the Streamlit main thread. Session state is backed by `DatabaseSessionService` (ADK's SQLite-backed session store).

### 3.6 ADK Built-in Tools: Grounding and Callbacks (Day 2a + Day 4a)

**Files:** `agents/drug_search_agent.py`, `agents/callbacks.py`

`DrugInfoSearchAgent` uses ADK's built-in `google_search` tool to ground pharmacological information in real-time web results. The agent explicitly cannot be mixed with function tools in the same agent — a constraint noted in the code — so it runs standalone from the Streamlit Tab 5.

`agents/callbacks.py` implements `before_tool_callback` and `after_tool_callback`, which are wired into DataCollectionAgent and AnalysisAgent. Every tool call is logged to a thread-local trace list with timestamps. The trace is serialized into the analysis report and surfaces in the Streamlit UI and the evaluation runner, enabling the trajectory coverage metric in `evals/run_evals.py`.

---

## 4. Design Decisions and Tradeoffs

**Deterministic analysis, not LLM analysis.** The core reconciliation logic — medication extraction, normalization, discrepancy detection, risk scoring — is implemented as deterministic Python rules, not LLM inference. This was a deliberate choice: medication safety decisions must be auditable, reproducible, and testable without an API key. The trade-off is reduced flexibility (the rules don't handle every possible discrepancy type), but the gain in reliability and testability is essential for a clinical context. The LLM's role is limited to data collection (parsing unstructured source documents) and communication (generating natural language summaries).

**Sequential over parallel agents.** A `SequentialAgent` was chosen over a `ParallelAgent` because each step depends on the output of the previous one. DataCollectionAgent must complete before AnalysisAgent can run; AnalysisAgent must complete before CommunicationAgent can generate output. Parallelizing these would require a fan-out/fan-in pattern with no benefit — the bottleneck is the MCP network calls and the LLM inference, not CPU.

**Tool-enforced policy, not prompt-suggested.** The original temptation was to include safety instructions in the prompt and trust the model to follow them. The final design enforces safety through the tool loop: the agent is required to call `run_policy_check` and cannot finalize its output without a `passed=true` result. If the agent produces forbidden language, the tool returns a specific list of violations, and the instruction requires revision and retry. This shifts safety from a soft constraint (the model might ignore a prompt instruction) to a hard constraint (the tool enforces the policy regardless of model behavior).

**HttpRetryOptions on all agents.** All four LlmAgents are configured with `GenerateContentConfig(http_options=HttpOptions(retry_options=HttpRetryOptions(attempts=5, initial_delay=1.0, exp_base=2.0)))`. A single transient 429 or 503 during a live demo would fail the entire sequential pipeline. The exponential backoff with 5 attempts means a rate-limit spike of up to ~30 seconds is handled silently.

**MCP read-only at the database layer.** The MCP server could enforce read-only access through code (no INSERT, UPDATE, DELETE methods) or through the database connection. The project does both, but the primary enforcement is the SQLite `mode=ro` URI parameter. This means even if a code path were added that called SQLite directly, it would fail at the driver level.

---

## 5. Limitations and Responsible AI Considerations

MediConciliador SNS is a prototype for educational and demonstration purposes. It is not a medical device, and it must not be used with real patient data or in clinical decision-making.

**Synthetic data only.** All 10 cases in the system were hand-crafted to represent realistic but entirely fictional patients. No real clinical records were used at any point in development or testing. The synthetic cases cover a range of discrepancy types and risk levels, but they do not represent the full diversity of real clinical scenarios.

**No prescribing or discontinuation.** The system is explicitly designed to surface discrepancies for professional review, not to make recommendations. The PolicyServer blocks any patient-facing text that gives medication instructions (starting, stopping, changing doses). The professional checklist frames every finding as a question for the clinician to verify, not a directive to follow.

**LLM non-determinism.** The DataCollectionAgent and CommunicationAgent use a language model, whose outputs vary across runs. The deterministic analysis pipeline mitigates this for the core reconciliation logic, but the professional checklist and patient summary will differ between runs. In a production system, this would require human review of every LLM-generated output before it reaches a patient.

**Local demo only.** The application runs locally and has not been deployed to a cloud environment. A production system would require authentication, audit logging, data residency compliance, and regulatory approval as a clinical decision-support tool.

**Semantic gating reliability.** The second-layer semantic policy check calls Gemini to detect implicit clinical directives. This check can produce false positives (blocking safe text) or false negatives (passing unsafe text that evades both layers). It is a defense-in-depth measure, not a primary safety mechanism.

---

## 6. Results

**Test suite:** 152 tests across 10 test modules, covering MCP read-only enforcement, medication extraction and normalization, discrepancy detection, risk scoring, policy server structural gating, tool callback behavior, agent construction, end-to-end integration with a live LLM, drug interaction checking (NLM + static fallback), and prompt injection detection. All 152 pass.

**Evaluation pipeline:** 36 behavioral evaluations across 10 synthetic cases, measuring discrepancy recall and precision against a gold-standard JSON dataset, risk classification accuracy, tool trajectory coverage (verified that the required 5 tool calls appear in every run), and safety policy behavior for 6 edge-case policy scenarios. All 36 pass.

**Demo cases:** Three primary cases cover the highest-impact real-world scenarios: (1) case_001 — NSAID/anticoagulant interaction, HIGH risk; (2) case_002 — diuretic omission at discharge in a heart failure patient, HIGH risk; (3) case_003 — PPI brand/generic duplication, LOW risk. The agent correctly identifies and classifies all three scenarios, generates a policy-compliant patient summary, and produces a structured professional checklist with clinical rationale.

The evaluation methodology separates behavioral correctness (does the agent detect the right discrepancies?) from code correctness (do the functions do what they are supposed to do?), following the distinction introduced in ADK Day 4b. The deterministic pipeline makes both types of evaluation fast and reproducible without requiring an API key.

---

## 7. Project Journey

MediConciliador SNS followed a strict spec-first sequence. The full architecture — problem framing, agent topology, data model, tool taxonomy, safety constraints, and evaluation criteria — was written in `specs/00_project_blueprint.md` before a single line of code existed. The `SKILL.md` file came next, formalizing what the agent could and could not do. Only then were the agents, tools, and tests written — in that order.

Three decisions changed significantly during development.

**The analysis pipeline became deterministic.** The first version of AnalysisAgent used the LLM to identify discrepancies directly from the source documents. After the first evaluation run, the results were non-reproducible: the same case returned different discrepancy counts across runs, making it impossible to define a reliable gold standard. The pipeline was rewritten as deterministic Python — medication extraction, normalization, comparison, and risk scoring all produce identical results on every run. The LLM's role was narrowed to parsing unstructured input and generating natural language output.

**The Policy Server became tool-enforced.** The original safety design placed forbidden-phrase instructions in the CommunicationAgent's prompt and trusted the model to follow them. Testing revealed that prompt instructions are a soft constraint — the model occasionally produced patient-facing text with implicit clinical directives that evaded the explicit rule set. The design was changed to require `run_policy_check` as a mandatory tool call, with a retry loop until `passed=true`. Safety shifted from something the model was asked to do to something the architecture enforced.

**Drug interaction checking was added late.** The original risk scoring relied entirely on the static `data/high_risk_medications.json` table, which cross-referenced 9 drug categories. After reviewing the evaluation gaps, two issues were clear: the static table had incomplete coverage, and there was no dynamic lookup for drug pairs not in the table. The NLM RxNorm API integration was added in the final development session, alongside expanding the static table from 9 to 20 categories. The static table now serves as the fallback when the API is unavailable — so the feature works during demos without internet access.

The test suite grew from 47 tests at the end of the first agent implementation to 152 tests at submission, reflecting incremental coverage added alongside each new tool and security feature rather than a test-first approach throughout. The evaluation suite was fixed at 36 checks early and served as the primary acceptance criterion for the full pipeline.
