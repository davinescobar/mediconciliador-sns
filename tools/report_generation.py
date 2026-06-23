"""
Report formatting and full analysis pipeline.

build_reconciliation_table   — builds the complete cross-source medication table.
format_reconciliation_report — structures scored discrepancies into a report dict.
run_full_analysis            — single-call pipeline used by AnalysisAgent.
"""

import json

from tools.medication_extraction import extract_medications, extract_discontinued
from tools.medication_normalization import normalize_medication_list
from tools.discrepancy_detection import detect_discrepancies
from tools.risk_scoring import score_discrepancy_risk
from tools.trace_logger import log_tool_call, get_trace, clear_trace


def build_reconciliation_table(
    discharge_norm_json: str,
    prescription_norm_json: str,
    interview_norm_json: str,
    discontinued_json: str,
    scored_json: str,
) -> list[dict]:
    """
    Builds the complete reconciliation table: one row per unique medication
    across all three sources, with its status in each and any linked discrepancy.
    """
    discharge = json.loads(discharge_norm_json)
    prescription = json.loads(prescription_norm_json)
    interview = json.loads(interview_norm_json)
    discontinued = json.loads(discontinued_json)
    scored = json.loads(scored_json)

    discharge_by_name = {m["name"]: m for m in discharge}
    prescription_by_name = {m["name"]: m for m in prescription}
    interview_by_name = {m["name"]: m for m in interview}
    discontinued_by_name = {d["name"]: d for d in discontinued}

    risk_by_med: dict[str, dict] = {}
    for d in scored:
        for part in d.get("medication", "").split("/"):
            key = part.strip()
            if key and key not in risk_by_med:
                risk_by_med[key] = d

    all_names = (
        set(discharge_by_name)
        | set(prescription_by_name)
        | set(interview_by_name)
        | set(discontinued_by_name)
    )

    def _cell(med: dict | None) -> str:
        if not med:
            return "—"
        parts = [p for p in (med.get("dose"), med.get("frequency")) if p]
        return " · ".join(parts) if parts else "presente"

    rows = []
    for name in sorted(all_names):
        disc = risk_by_med.get(name, {})
        discharge_cell = (
            "SUSPENDIDO"
            if name in discontinued_by_name and name not in discharge_by_name
            else _cell(discharge_by_name.get(name))
        )
        rows.append({
            "medication": name,
            "discharge_summary": discharge_cell,
            "active_prescription": _cell(prescription_by_name.get(name)),
            "patient_interview": _cell(interview_by_name.get(name)),
            "discrepancy_type": disc.get("type"),
            "risk_level": disc.get("risk_level"),
        })

    _risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    rows.sort(key=lambda r: (_risk_order.get(r["risk_level"], 3), r["medication"]))
    return rows


def format_reconciliation_report(
    case_id: str,
    discrepancies_json: str,
    trace_json: str = "[]",
    reconciliation_table_json: str = "[]",
) -> str:
    """
    Structures scored discrepancies into a final report dict.

    Args:
        case_id: The case identifier.
        discrepancies_json: JSON array from score_discrepancy_risk.
        trace_json: JSON array of tool call trace entries.
        reconciliation_table_json: JSON array from build_reconciliation_table.

    Returns:
        JSON object with summary, reconciliation_table, discrepancies,
        requires_professional_review, trace.
    """
    discrepancies = json.loads(discrepancies_json)
    trace = json.loads(trace_json)

    high = sum(1 for d in discrepancies if d.get("risk_level") == "HIGH")
    medium = sum(1 for d in discrepancies if d.get("risk_level") == "MEDIUM")
    low = sum(1 for d in discrepancies if d.get("risk_level") == "LOW")

    report = {
        "case_id": case_id,
        "summary": {
            "total_discrepancies": len(discrepancies),
            "high_risk": high,
            "medium_risk": medium,
            "low_risk": low,
        },
        "requires_professional_review": high > 0 or medium > 0,
        "reconciliation_table": json.loads(reconciliation_table_json),
        "discrepancies": discrepancies,
        "trace": trace,
    }
    return json.dumps(report, ensure_ascii=False, indent=2)


def run_full_analysis(case_data_json: str) -> str:
    """
    Runs the complete deterministic medication reconciliation pipeline.

    Single entry point for AnalysisAgent. Extracts, normalizes, detects
    discrepancies, scores risk, and returns a structured report.

    Args:
        case_data_json: JSON object with keys: case_id, discharge_summary,
            active_prescription, patient_interview, risk_factors.
            Produced by DataCollectionAgent via output_key="case_data".

    Returns:
        JSON reconciliation report (same structure as format_reconciliation_report).
    """
    clear_trace()
    case_data = json.loads(case_data_json)
    case_id = case_data.get("case_id", "unknown")
    risk_factors = case_data.get("risk_factors", [])

    discharge_json = json.dumps(case_data["discharge_summary"], ensure_ascii=False)
    prescription_json = json.dumps(case_data["active_prescription"], ensure_ascii=False)
    interview_json = json.dumps(case_data["patient_interview"], ensure_ascii=False)

    log_tool_call("extract_medications", {"source_type": "discharge"})
    discharge_meds = extract_medications(discharge_json, "discharge")

    log_tool_call("extract_medications", {"source_type": "prescription"})
    prescription_meds = extract_medications(prescription_json, "prescription")

    log_tool_call("extract_medications", {"source_type": "interview"})
    interview_meds = extract_medications(interview_json, "interview")

    log_tool_call("extract_discontinued")
    discontinued_meds = extract_discontinued(discharge_json)

    log_tool_call("normalize_medication_list", {"source": "discharge"})
    discharge_norm = normalize_medication_list(discharge_meds)

    log_tool_call("normalize_medication_list", {"source": "prescription"})
    prescription_norm = normalize_medication_list(prescription_meds)

    log_tool_call("normalize_medication_list", {"source": "interview"})
    interview_norm = normalize_medication_list(interview_meds)

    log_tool_call("detect_discrepancies")
    discrepancies = detect_discrepancies(
        discharge_norm,
        prescription_norm,
        interview_norm,
        discontinued_meds,
    )

    context = {"risk_factors": risk_factors}
    log_tool_call("score_discrepancy_risk", {"context": context})
    scored = score_discrepancy_risk(
        discrepancies,
        discharge_meds_json=discharge_norm,
        context_json=json.dumps(context),
    )

    log_tool_call("build_reconciliation_table", {"case_id": case_id})
    recon_table = build_reconciliation_table(
        discharge_norm,
        prescription_norm,
        interview_norm,
        discontinued_meds,
        scored,
    )

    log_tool_call("format_reconciliation_report", {"case_id": case_id})
    return format_reconciliation_report(
        case_id=case_id,
        discrepancies_json=scored,
        trace_json=json.dumps(get_trace(), ensure_ascii=False),
        reconciliation_table_json=json.dumps(recon_table, ensure_ascii=False),
    )
