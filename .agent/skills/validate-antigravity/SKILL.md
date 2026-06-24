---
name: validate-antigravity
description: |
  Validates the Antigravity workflow requirement for the Kaggle capstone.
  Trigger when asked to audit, validate or review the spec-driven development workflow.
  Use before submission to confirm the development process artifacts are present and consistent.
source: Day 1 (vibe coding vs agentic engineering, Agent Skills pattern), Day 5 (Spec-Driven Development, BDD)
---

# Validation: Antigravity Workflow

## What the whitepaper requires (Day 1 + Day 5)

### Day 1 definition
- Antigravity = spec-first / context-engineering driven agentic development
- "Code is disposable, specs are permanent"
- Agent Skills (SKILL.md) as dynamic context — teach repeatable engineering habits
- CLAUDE.md / AGENTS.md as system prompt layer
- Progression: intent → blueprint → skills → agents → tests

### Day 5 definition (Spec-Driven Development)
- Good specification: Full Technical Design + Visual Aids + Background + Scenarios
- Spec stored in `specs/` folder checked into version control
- BDD format (Gherkin: Scenario / Given / When / Then) is the "ultimate tool for turning vague intent into precise architectural design"
- Specs live in three places: Chat Interface (session-only), `specs/` folder (version-controlled), `.agent/skills/` (reusable)

## Checklist — files to inspect

- [ ] `specs/00_project_blueprint.md` — Full Technical Design present
- [ ] `specs/06_bdd_scenarios.feature` — BDD Gherkin scenarios present
- [ ] `CLAUDE.md` — project system prompt / DNA file
- [ ] `.agent/skills/medication-reconciliation/SKILL.md` — reusable skill
- [ ] Evidence of spec-first process: blueprint predates code (check git log if available)

## Current status (as of 2026-06-24)

| Element | File | Status |
|---------|------|--------|
| Project blueprint | `specs/00_project_blueprint.md` | ✅ |
| BDD scenarios | `specs/06_bdd_scenarios.feature` | ✅ |
| CLAUDE.md (project DNA) | `mediconciliador-sns/CLAUDE.md` | ✅ |
| AGENTS.md | `mediconciliador-sns/AGENTS.md` | ✅ |
| Agent Skill (SKILL.md) | `.agent/skills/medication-reconciliation/` | ✅ |
| Spec-first evidence | All specs created in session 1 before any code | ✅ |
| Code regenerability | Deterministic pipeline in `tools/` separable from LLM | ✅ |

## Status: FULLY COVERED

The project demonstrates the Antigravity workflow more completely than most examples:  
BDD Gherkin scenarios + Markdown blueprint + CLAUDE.md + AGENTS.md + SKILL.md.  
This is textbook Day 5 Spec-Driven Development.
