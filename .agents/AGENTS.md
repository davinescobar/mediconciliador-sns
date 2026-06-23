# AGENTS.md — MediConciliador SNS

## Project role

You are helping build MediConciliador SNS, a safe medication reconciliation agent for older polymedicated patients after hospital discharge.

This is a Kaggle MVP. It must use only synthetic data.

Read `specs/00_project_blueprint.md` before implementing anything. Read `CLAUDE.md` at the start of every session.

## Hard rules

- Do not use real patient data.
- Do not create integrations with real clinical systems.
- Do not connect to electronic prescription systems.
- Do not connect to EHR systems.
- Do not send emails or external messages.
- Do not prescribe, discontinue, start, or change medication.
- Do not generate clinical instructions that sound definitive.
- Always frame outputs as support for professional review.
- High-risk discrepancies must be escalated for professional review.
- If uncertain, explicitly mark uncertainty.

## Development rules

- Follow spec-driven development.
- Read `specs/00_project_blueprint.md` before implementing.
- Generate tests before implementing core logic.
- Keep changes small and reviewable.
- Prefer deterministic scripts for extraction, comparison, policy checks, and risk scoring.
- Use the LLM for reasoning, explanation, and summarization — not for hidden irreversible actions.
- Use synthetic data only.
- Do not add speculative features outside the MVP.

## Architecture rules

- Use ADK-style agent orchestration.
- Keep tools read-only unless explicitly specified.
- MCP server must expose synthetic data only.
- Policy Server must intercept all generated patient-facing outputs.
- All agent runs must produce a trace.

## Output rules

Patient-facing outputs must:
- be clear;
- be non-alarming;
- avoid definitive treatment instructions;
- explain that medication changes require professional review.

Professional-facing outputs must:
- include source comparison;
- include discrepancy type;
- include risk level;
- include rationale;
- include recommended review questions.
