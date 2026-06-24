---
name: validate-security
description: |
  Validates the Security Features requirement for the Kaggle capstone.
  Trigger when asked to audit, validate or review security implementation.
  Use before Kaggle submission to assess coverage of Day 4 and Day 5 security patterns.
source: Day 4 (7-Pillar Security Architecture), Day 5 (Policy Server, Zero-Trust Development)
---

# Validation: Security Features

## What the whitepaper requires

### Day 4 — 7-Pillar Security Architecture (relevant to a capstone)

| Pillar | Course description | Implementable without GCP? |
|--------|-------------------|---------------------------|
| 1 — Infrastructure | Kernel-level sandboxes, egress governance | No |
| 2 — Data | Least privilege, read-only data access | Yes |
| 3 — Model | System instructions + rule files = "new source code" | Yes |
| 4 — Application | LLM firewalls, deterministic hooks, MCP Spoofing defense | Yes |
| 5 — IAM | SPIFFE IDs, Zero Ambient Authority, JIT tokens | No |
| 6 — Observability | Execution trace, tool logs, audit trail | Yes |
| 7 — Governance | EU AI Act, Risk-Stratified Attestation | No |

### Day 5 — Policy Server (concrete implementation)

Two layers required:
1. **Structural Gating** (Traffic Lights): deterministic YAML rules — blocked tools by role/environment
2. **Semantic Gating** (Intelligent Referee): secondary LLM validates content against privacy/policy guidelines

Three-step execution per tool call:
1. Structural check (YAML lookup) → block if tool not allowed
2. Semantic check (Gemini prompt) → block if content violates PII/policy
3. Execution: both pass → tool runs; otherwise return "Policy Violation"

### Day 5 — Context Hygiene & Prompt Sanitization

- `context_resolver.py`: replace `[[VARIABLE_NAME]]` placeholders with env vars / session state
- Wired into tool call pipeline as middleware
- Prevents PII leakage via context hallucination

## Checklist — files to inspect

- [ ] `policy/policy_server.py` — PolicyServer class
- [ ] `policy/policies.yaml` — blocked_tools, allowed_tools, patient_output_policy
- [ ] `policy/forbidden_phrases.yaml` — forbidden phrases by language
- [ ] `tools/policy_check.py` — run_policy_check ADK tool
- [ ] `agents/communication_agent.py` — mandatory run_policy_check call in instruction

## Current status (as of 2026-06-24)

| Pillar / Pattern | Implementation | Status |
|-----------------|----------------|--------|
| Pillar 2 — Least privilege | MCP read-only (SELECT only) | ✅ |
| Pillar 3 — Rule files as source | `policies.yaml` + `forbidden_phrases.yaml` | ✅ |
| Pillar 4 — Deterministic hook | `run_policy_check` mandatory before output | ✅ |
| Pillar 6 — Execution trace | ADK callbacks + agent_trace in output | ✅ |
| Day 5 Structural Gating | PolicyServer with forbidden phrase check | ✅ |
| Day 5 `policies.yaml` format | blocked_tools list + allowed_tools list | ✅ |
| **Day 5 Semantic Gating** | **LLM-as-judge on output content** | **❌ PARTIAL** |
| Day 5 Context Hygiene | `context_resolver.py` middleware | ❌ NOT IMPLEMENTED |

## Gap analysis

### Semantic Gating (PARTIAL — arguable)
Day 5 defines Semantic Gating as "a secondary LLM inspects content against PII guidelines".  
The project uses `run_policy_check` which instructs the LlmAgent itself to validate its own output.  
This is self-referential rather than an independent judge.  

**Verdict**: defensible for a capstone — the constraint is enforced and iterated until passed. Not the same as an independent semantic gate. Mention in writeup as "single-agent semantic validation" rather than claiming a full hybrid policy server.

### Context Hygiene (NOT IMPLEMENTED)
Day 5 section 32–35 describes `context_resolver.py` pattern.  
The project does not implement PII masking or placeholder injection.  
**Impact**: low. Project uses only synthetic data, so PII leakage risk is zero. Not worth implementing before deadline.

## Status: COVERED (with honest caveats in writeup)
