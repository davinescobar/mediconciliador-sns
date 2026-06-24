---
name: validate-agent-skill
description: |
  Validates the Agent Skill requirement for the Kaggle capstone.
  Trigger when asked to audit, validate or review the Agent Skill implementation.
  Use before Kaggle submission to confirm the SKILL.md structure matches Day 3.
source: Day 3 (Agent Skills anatomy), Day 5 (where skills live, trigger-based activation)
---

# Validation: Agent Skill

## What the whitepaper requires (Day 3 + Day 5)

- Skill folder must be at `.agent/skills/<skill-name>/`
- `SKILL.md` is the required file — always loaded by Antigravity workspace manager
- SKILL.md frontmatter: `name`, `description` (used as trigger matching text)
- SKILL.md body: loaded on trigger, describes the workflow
- Optional subdirs: `scripts/`, `references/`, `assets/`
- Progressive disclosure: frontmatter always in context → body loads on trigger → bundled resources load on demand
- Day 5: Skills teach the agent "repeatable engineering habits"

## Checklist — files to inspect

- [ ] `.agent/skills/medication-reconciliation/SKILL.md` — exists, has frontmatter
- [ ] `.agent/skills/medication-reconciliation/references/` — optional but present
- [ ] `.agent/skills/medication-reconciliation/assets/` — optional
- [ ] SKILL.md description field — is it specific enough to trigger on relevant requests?

## Current status (as of 2026-06-24)

| Element | Status |
|---------|--------|
| Skill folder at `.agent/skills/` | ✅ |
| `SKILL.md` present | ✅ |
| Frontmatter with `name` + `description` | ✅ |
| `references/` directory with 4 files | ✅ |
| `assets/` directory | ✅ (exists, empty) |
| Progressive disclosure pattern | ✅ (frontmatter as trigger metadata) |

## Minor gap: assets/ is empty

The Day 3 whitepaper lists `assets/` as holding "diagrams, templates, example outputs".  
Adding a sample reconciliation output JSON here would complete the anatomy exactly.

This is cosmetic — the skill structure is valid as-is.

## Status: COVERED
