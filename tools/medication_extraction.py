"""Extracts structured medication lists from raw MCP tool output. No LLM calls."""

import json


def extract_medications(source_data_json: str, source_type: str) -> str:
    """
    Extracts a structured medication list from raw MCP data.

    Args:
        source_data_json: JSON string from get_discharge_summary,
            get_active_prescription, or get_patient_interview.
        source_type: One of 'discharge', 'prescription', 'interview'.

    Returns:
        JSON array of {name, dose, frequency, route, source} objects.
    """
    data = json.loads(source_data_json)

    if source_type == "discharge":
        raw = data.get("medications_at_discharge", [])
        meds = [
            {
                "name": m["name"].lower().strip(),
                "dose": m.get("dose"),
                "frequency": m.get("frequency"),
                "route": m.get("route"),
                "source": "discharge",
            }
            for m in raw
        ]
    elif source_type == "prescription":
        raw = data.get("medications", [])
        meds = [
            {
                "name": m["name"].lower().strip(),
                "dose": m.get("dose"),
                "frequency": m.get("frequency"),
                "route": m.get("route"),
                "source": "prescription",
            }
            for m in raw
        ]
    elif source_type == "interview":
        raw = data.get("reported_medications", [])
        meds = [
            {
                "name": m["name"].lower().strip(),
                "dose": m.get("dose"),
                "frequency": m.get("frequency"),
                "route": m.get("route"),
                "source": "interview",
                "patient_comment": m.get("patient_comment"),
            }
            for m in raw
        ]
    else:
        return json.dumps({"error": f"Unknown source_type: {source_type}"})

    return json.dumps(meds, ensure_ascii=False)


def extract_discontinued(discharge_data_json: str) -> str:
    """
    Extracts the list of medications explicitly discontinued at discharge.

    Args:
        discharge_data_json: JSON string from get_discharge_summary.

    Returns:
        JSON array of {name, reason} objects.
    """
    data = json.loads(discharge_data_json)
    discontinued = data.get("medications_discontinued_at_discharge", [])
    result = [
        {
            "name": d["name"].lower().strip(),
            "reason": d.get("reason", ""),
        }
        for d in discontinued
    ]
    return json.dumps(result, ensure_ascii=False)
