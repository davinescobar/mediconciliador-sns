# MediConciliador SNS — Contexto del proyecto

Lee este archivo al inicio de cada sesión antes de tocar cualquier código.

## Qué es este proyecto

MVP para la competición **Vibe Coding Agents Capstone Project de Kaggle**.

Agente de conciliación de medicación para pacientes mayores polimedicados tras alta hospitalaria en España. Compara tres fuentes sintéticas (informe de alta, receta activa, entrevista al paciente), detecta discrepancias, clasifica riesgo y genera outputs seguros para profesional y paciente.

**Solo datos sintéticos. Sin datos reales. Sin prescripción. Sin modificación de tratamientos.**

Spec completa: `specs/00_project_blueprint.md`

---

## Requisitos de la competición → estado actual

| # | Requisito | Archivos clave | Estado |
|---|-----------|---------------|--------|
| 1 | **ADK multi-agent system** | `agents/orchestrator.py`, `agents/*.py` | LISTO |
| 2 | **MCP Server** | `mcp/mcp_server.py`, `mcp/mcp_client.py` | LISTO |
| 3 | **Agent Skill** | `.agent/skills/medication-reconciliation/SKILL.md` | LISTO |
| 4 | **Security features** | `policy/policy_server.py`, `policy/policies.yaml` | LISTO |
| 5 | **Deployable app** | `app.py` | LISTO |
| 6 | **Antigravity workflow** | `.agent/skills/`, `specs/` (este repo) | LISTO |

Actualiza esta tabla al cerrar cada sesión.

---

## Arquitectura de agentes

```
MediConciliadorOrchestrator (agents/orchestrator.py)
├── DischargeSummaryParserAgent    ← agents/discharge_parser_agent.py
├── ActivePrescriptionAgent        ← agents/prescription_agent.py
├── PatientInterviewAgent          ← agents/interview_agent.py
├── MedicationNormalizerAgent      ← agents/normalizer_agent.py
├── ReconciliationAgent            ← agents/reconciliation_agent.py
├── RiskTriageAgent                ← agents/risk_triage_agent.py
├── PatientCommunicationAgent      ← agents/communication_agent.py
├── ProfessionalChecklistAgent     ← (dentro de reconciliation_agent)
└── SafetyPolicyAgent              ← agents/safety_policy_agent.py
```

---

## Herramientas MCP (read-only)

Definidas en `mcp/mcp_server.py`. Solo SELECT en SQLite:

```
get_case_list()
get_synthetic_case(case_id)
get_discharge_summary(case_id)
get_active_prescription(case_id)
get_patient_interview(case_id)
get_allergies(case_id)
get_risk_factors(case_id)
get_high_risk_medications()
get_reconciliation_guidance()
```

---

## Casos sintéticos para la demo

- `case_001` — AINE + anticoagulante (apixaban + ibuprofeno). Riesgo HIGH.
- `case_002` — Omisión de diurético al alta (furosemida). Riesgo MEDIUM/HIGH.
- `case_003` — Duplicidad marca/genérico (omeprazol). Riesgo LOW/MEDIUM.

Datos en `data/synthetic_cases.json`.
Golden dataset en `data/gold_standard_discrepancies.json`.

---

## Reglas duras (no negociables)

1. Sin datos reales de pacientes.
2. Sin integración con sistemas clínicos reales.
3. Sin acceso a receta electrónica real.
4. Sin prescribir, suspender ni cambiar medicación.
5. Sin escritura en ninguna base de datos (MCP = solo lectura).
6. Discrepancias de riesgo HIGH → siempre piden revisión profesional.
7. Policy Server intercepta todos los outputs dirigidos al paciente.
8. Toda ejecución genera una traza de herramientas.

Frases prohibidas en outputs al paciente:
- "deje de tomar", "suspenda", "empiece a tomar"
- "cambie la dosis", "no necesita consultar"
- "puede tomarlo sin problema", "es seguro continuar"

---

## Trayectoria ideal del agente

```
get_synthetic_case → get_discharge_summary → get_active_prescription
→ get_patient_interview → get_allergies → get_high_risk_medications
→ extract_medications → normalize_medications → compare_medication_lists
→ score_discrepancy_risk → generate_professional_checklist
→ generate_patient_summary → run_policy_check
```

---

## Archivos por área de trabajo

| Área | Archivos |
|------|---------|
| Datos | `data/synthetic_cases.json`, `data/gold_standard_discrepancies.json`, `data/high_risk_medications.json` |
| MCP | `mcp/mcp_server.py`, `mcp/mcp_client.py` |
| Agentes | `agents/orchestrator.py`, `agents/*.py` |
| Herramientas | `tools/*.py` — incluye `drug_interactions.py` (NLM RxNorm + fallback) e `input_sanitizer.py` (prompt injection) |
| Seguridad | `policy/policies.yaml`, `policy/forbidden_phrases.yaml`, `policy/policy_server.py` |
| Skill | `.agent/skills/medication-reconciliation/SKILL.md` |
| UI | `app.py` |
| Evaluación | `evals/run_evals.py`, `evals/eval_cases.json` |
| Tests | `tests/*.py` |

---

## Roadmap de sesiones

| Sesión | Objetivo | Criterio de éxito |
|--------|---------|------------------|
| 1 (esta) | Scaffold + corpus | Árbol de archivos creado, CLAUDE.md listo |
| 2 | MCP Server funcional | Devuelve datos sintéticos via SQLite |
| 3 ✅ | Agentes ADK | 47/47 tests verde. SequentialAgent + 3 LlmAgents. `demo/run_case.py` listo. |
| 4 ✅ | Policy Server | 34/34 tests verde. PolicyServer + run_policy_check tool. CommunicationAgent usa el tool. |
| 5 ✅ | Streamlit app | 4 pantallas funcionando. app.py operativo. |
| 6 | Evaluación | `run_evals.py` reporta métricas vs golden dataset |
| 7 ✅ | Tests + demo | 116/116 pytest verde, 15/15 evals verde, demo_script.md completo |
