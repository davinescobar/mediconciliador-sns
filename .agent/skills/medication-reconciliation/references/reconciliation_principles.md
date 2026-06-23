# Reconciliation Principles

Medication reconciliation is the process of comparing a patient's medication orders to all medications the patient has been taking. The goal is to avoid medication errors such as omissions, duplications, dosing errors, or drug interactions.

## Core steps

1. Collect a complete medication history from all sources.
2. Compare medications against each other to identify discrepancies.
3. Classify each discrepancy by type and clinical relevance.
4. Generate a structured summary for professional review.
5. Generate a simplified explanation for the patient or caregiver.

## Sources compared in this MVP

1. Hospital discharge summary (what was indicated at discharge).
2. Active prescription list (what is currently prescribed in the system).
3. Patient or caregiver interview (what the patient reports actually taking).

## Important constraints

- Reconciliation in this MVP is a decision-support tool, not a clinical decision.
- All discrepancies require professional review before any action is taken.
- The agent does not modify any medication list.
- Uncertainty must be explicitly stated when data is incomplete or ambiguous.
