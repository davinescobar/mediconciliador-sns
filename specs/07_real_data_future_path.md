# From Synthetic MVP to Real Clinical Deployment

## Purpose

MediConciliador SNS has been built as a synthetic MVP for demonstration purposes.
This document describes the path that would be required to move toward a real clinical deployment.

**Hard boundary of the current MVP:** only synthetic data, no EHR integration, no real prescriptions,
no patient identity, no clinical actions.

---

## 18.1 Clinical governance

Before any real-world use:

- An identified clinical team must own the system (physician, pharmacist, nursing).
- A clinical reviewer must validate every discrepancy type on real anonymised cases.
- Professional responsibility boundaries must be defined: who acts on the agent's output, and how.
- A patient safety committee must approve the scope and guardrails.
- The agent must remain advisory — no autonomous clinical action at any phase.

---

## 18.2 Data protection

Required prior to any use with real data:

- Data Protection Impact Assessment (DPIA) under GDPR / LOPDGDD.
- Legal basis for processing (patient consent or legitimate clinical interest).
- Data minimisation: only fields strictly necessary for reconciliation.
- Anonymisation or pseudonymisation wherever feasible.
- Role-based access control: only treating professionals access patient data.
- Immutable audit logs for all access and outputs.
- Defined retention limits and deletion procedures.
- Data Processing Agreements with any third-party infrastructure providers.

---

## 18.3 Technical integration

Infrastructure work required:

- Secure, authenticated connection to the Electronic Health Record (EHR).
- Secure, authenticated connection to the national electronic prescription system (Receta Electrónica SNS).
- HL7 FHIR interoperability layer if source systems require it.
- Strong authentication (MFA or federated identity via the SNS provider directory).
- Per-role, per-resource permission model — not a global key.
- Strict environment separation: development → staging → production, each with synthetic data in lower environments.
- Encryption in transit (TLS 1.3) and at rest for all patient data stores.
- Immutable, tamper-evident logs (write-once audit trail).

---

## 18.4 Security

Agentic-specific security requirements:

- MCP server must connect only to verified, internal clinical systems — no external APIs.
- Every tool must operate under least-privilege: read-only unless explicitly granted write scope.
- Policy Server must remain mandatory and must intercept all patient-facing outputs.
- Human-in-the-loop is not optional for HIGH-risk discrepancies: no automated dispatch to patient without professional sign-off.
- No automatic write to prescription or EHR at any phase of deployment.
- Full tool trace stored per reconciliation run, tied to the professional user who triggered it.
- Circuit breakers to halt agent execution if downstream systems return unexpected data.
- Drift monitoring: alert if discrepancy detection rates shift unexpectedly.

---

## 18.5 Validation

Required before clinical use:

- Gold standard built with real clinical professionals (pharmacist + physician + nurse).
- Sensitivity and specificity measured per discrepancy type on a held-out anonymised case set.
- False positive rate assessed — must be low enough to remain actionable without alert fatigue.
- False negative rate assessed — HIGH-risk discrepancies must have near-zero miss rate.
- Usability validation with the target professional users.
- Time-savings measured vs current manual reconciliation process.
- Medication error impact measured, with pre/post comparison if possible.
- Prospective evaluation in shadow mode (see phase 3 below) before any clinical impact.

---

## 18.6 Phased deployment

No jump from synthetic MVP to full clinical deployment. Required phases:

```
Phase 1 — Synthetic data only
  Current state. No patient data. No clinical impact.

Phase 2 — Anonymised retrospective cases
  Real historical cases, stripped of identifiers.
  Validates detection accuracy without patient risk.

Phase 3 — Shadow mode with real data, no clinical impact
  Agent runs in parallel with normal workflow.
  Outputs not shown to professionals until validated.
  Measures accuracy against real clinical decisions.

Phase 4 — Draft output for professional review
  Agent output shown to the professional as a draft to review, edit, and approve.
  Professional retains full authority. Agent is a tool.

Phase 5 — Controlled integration with clinical systems
  After phase 4 shows consistent safety and utility.
  Scoped deployment in one unit, one case type, with governance oversight.
  Ongoing monitoring and regular safety review.
```

Even at phase 5, the agent must remain an aid to professional review — not an autonomous prescriber
or decision-maker.

---

## Summary

The MVP demonstrates that the core agentic architecture — multi-agent orchestration, MCP server,
deterministic reconciliation pipeline, safety policy checks, and traceable outputs — is viable.

The path to real clinical use is well-defined but requires:
governance, data protection compliance, technical integration, independent clinical validation,
and a phased rollout with human oversight at every step.

None of those steps are architectural obstacles. They are the normal cost of deploying AI safely
in a clinical environment.
