---
name: validate-deployable
description: |
  Validates the Deployable App requirement for the Kaggle capstone.
  Trigger when asked to audit, validate or review the app deployment status.
  Use before submission to confirm the app runs end-to-end without errors.
source: Day 5 (production-grade development, agents-cli deploy)
---

# Validation: Deployable App

## What the whitepaper requires (Day 5)

- "Production-grade" means: working app + test coverage + evaluation + guardrails
- Day 5 mentions `agents-cli deploy` for Cloud Run or Vertex AI Agent Engine as the deployment target
- For Kaggle: local Streamlit demo is accepted (confirmed via Kaggle rubric)
- The Summary box in Day 5 says: "agents-cli deploy for sandboxed deployment to Cloud Run or Vertex AI Agent Engine"

## Checklist — files to inspect

- [ ] `app.py` — 6 tabs all functional
- [ ] `requirements.txt` — all dependencies listed
- [ ] `.env.example` or README start instructions — someone else can run this
- [ ] `tests/` — 131 passing tests
- [ ] `evals/run_evals.py` — 36/36 green

## Current status (as of 2026-06-24)

| Element | Status |
|---------|--------|
| Streamlit app (6 tabs) | ✅ |
| 131 pytest tests green | ✅ |
| 36/36 evals green | ✅ |
| requirements.txt | ✅ |
| README with run instructions | ✅ |
| Local demo works | ✅ |
| Cloud deployment | ❌ (not required for Kaggle) |

## Start command

```bash
cd mediconciliador-sns
source .venv/bin/activate
streamlit run app.py
```

Requires `GOOGLE_API_KEY` in `.env`. Deterministic pipeline runs without it.

## Status: FULLY COVERED
