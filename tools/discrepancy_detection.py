"""Detects medication discrepancies by comparing three normalized sources. No LLM calls."""

import json

_PPI_NAMES = frozenset({
    "omeprazole", "pantoprazole", "lansoprazole", "esomeprazole", "rabeprazole",
})


def detect_discrepancies(
    discharge_meds_json: str,
    prescription_meds_json: str,
    interview_meds_json: str,
    discontinued_meds_json: str = "[]",
) -> str:
    """
    Compares three normalized medication lists and returns detected discrepancies.

    Args:
        discharge_meds_json: JSON array from discharge source (normalized).
        prescription_meds_json: JSON array from prescription source (normalized).
        interview_meds_json: JSON array from patient interview (normalized).
        discontinued_meds_json: JSON array of {name, reason} discontinued at discharge.

    Returns:
        JSON array of discrepancy dicts with type, medication, description, sources.
    """
    discharge = json.loads(discharge_meds_json)
    prescription = json.loads(prescription_meds_json)
    interview = json.loads(interview_meds_json)
    discontinued = json.loads(discontinued_meds_json)

    discharge_names = {m["name"] for m in discharge}
    prescription_names = {m["name"] for m in prescription}
    interview_names = {m["name"] for m in interview}
    discontinued_names = {d["name"].lower().strip() for d in discontinued}

    discrepancies: list[dict] = []

    # 1. Discontinued medication still reported by patient
    for name in discontinued_names & interview_names:
        discrepancies.append({
            "medication": name,
            "type": "discontinued_medication_still_taken",
            "description": (
                f"{name} was explicitly discontinued at hospital discharge "
                "but the patient reports still taking it."
            ),
            "sources_present": ["interview"],
            "sources_absent": ["discharge_current", "prescription"],
            "discontinued_at_discharge": True,
        })

    # 2. In discharge summary but absent from active prescription
    for name in discharge_names - prescription_names:
        discrepancies.append({
            "medication": name,
            "type": "omission_in_prescription",
            "description": (
                f"{name} appears in the hospital discharge summary but is "
                "missing from the active prescription."
            ),
            "sources_present": ["discharge"],
            "sources_absent": ["prescription"],
        })

    # 3. Possible PPI duplication: unidentified OTC product vs prescribed PPI
    if "unidentified_ppi" in interview_names:
        prescribed_ppis = discharge_names & _PPI_NAMES
        if prescribed_ppis:
            discrepancies.append({
                "medication": f"unidentified_ppi / {', '.join(sorted(prescribed_ppis))}",
                "type": "possible_duplication",
                "description": (
                    "Patient reports taking an unidentified stomach protector "
                    f"while also prescribed {', '.join(sorted(prescribed_ppis))}. "
                    "Possible PPI duplication — identity of OTC product is uncertain."
                ),
                "sources_present": ["interview"],
                "uncertainty": "high",
            })

    # 4. Undocumented medication: patient taking something not in any official record
    known_names = discharge_names | prescription_names | discontinued_names | {"unidentified_ppi"}
    for name in interview_names - known_names:
        discrepancies.append({
            "medication": name,
            "type": "undocumented_patient_medication",
            "description": (
                f"{name} is reported by the patient but is not documented "
                "in the discharge summary or the active prescription."
            ),
            "sources_present": ["interview"],
            "sources_absent": ["discharge", "prescription"],
        })

    return json.dumps(discrepancies, ensure_ascii=False, indent=2)
