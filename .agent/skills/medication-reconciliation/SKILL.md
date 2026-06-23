---
name: medication-reconciliation
description: |
  Performs medication reconciliation for synthetic older polymedicated patient cases.
  Use when the task involves comparing hospital discharge medication, active prescription,
  patient-reported medication, allergies, or medication discrepancies.
  Use for detecting omissions, duplications, discontinued medications still taken,
  dose mismatches, patient confusion, and high-risk discrepancies.
  Do NOT use for diagnosis, prescribing, discontinuing medication, changing doses,
  or giving definitive clinical instructions.
---

# Medication Reconciliation Skill

## Purpose

Compare medication information from three synthetic sources:

1. Hospital discharge summary.
2. Active prescription list.
3. Patient or caregiver interview.

Identify discrepancies, classify risk, and generate safe outputs for professional review and patient understanding.

## Required workflow

1. Load synthetic case via `get_synthetic_case(case_id)`.
2. Extract medications from discharge summary via `get_discharge_summary(case_id)`.
3. Extract medications from active prescription via `get_active_prescription(case_id)`.
4. Extract medications from patient interview via `get_patient_interview(case_id)`.
5. Load allergies via `get_allergies(case_id)`.
6. Load high-risk medication reference via `get_high_risk_medications()`.
7. Normalize medication names (brand → generic when possible).
8. Compare the three medication lists.
9. Detect discrepancy types (see below).
10. Classify discrepancy risk (LOW / MEDIUM / HIGH).
11. Generate professional checklist.
12. Generate patient-safe explanation.
13. Run safety policy checks via Policy Server.
14. Return structured JSON output.

## Discrepancy types

- omission
- duplication
- discontinued_medication_still_taken
- new_medication_not_in_prescription
- dose_mismatch
- frequency_mismatch
- route_mismatch
- patient_uncertainty
- possible_allergy_issue
- high_risk_medication_issue
- self_medication_or_otc_issue

## Risk levels

- LOW: informational or clarification issue.
- MEDIUM: needs routine professional review.
- HIGH: potentially clinically relevant; requires prioritized professional review.

Always check: is the medication a high-risk category (anticoagulant, NSAID, diuretic, antidiabetic, antiplatelet, opioid, antiepileptic)?

## Forbidden behavior

Never say:
- "stop taking"
- "start taking"
- "change your dose"
- "you do not need to consult"
- "this is safe"
- "this is dangerous" (without full context and professional framing)

Never issue definitive clinical instructions.

## Required language for high-risk discrepancies

Always include:
- "requires professional review"
- "do not change medication without consulting your clinician"
- "bring this information to your doctor, nurse, or pharmacist"

## Output format

Always return a JSON with these fields:

```json
{
  "case_id": "string",
  "patient_profile": { "age": 0, "sex": "string", "risk_factors": [] },
  "source_summary": {
    "discharge_summary_loaded": true,
    "active_prescription_loaded": true,
    "patient_interview_loaded": true,
    "allergies_loaded": true
  },
  "reconciliation_table": [
    {
      "medication": "string",
      "discharge_summary": "string",
      "active_prescription": "string",
      "patient_reported": "string",
      "discrepancy_type": "string",
      "risk_level": "HIGH|MEDIUM|LOW",
      "rationale": "string",
      "uncertainty": "low|medium|high"
    }
  ],
  "professional_checklist": ["string"],
  "patient_summary": "string",
  "safety_policy": {
    "passed": true,
    "blocked_phrases_detected": [],
    "requires_professional_review": true
  },
  "agent_trace": ["string"]
}
```

## References

- Reconciliation principles: `references/reconciliation_principles.md`
- Discrepancy types detail: `references/discrepancy_types.md`
- High-risk medications: `references/high_risk_medication_categories.md`
- Patient-safe language: `references/patient_safe_language.md`
