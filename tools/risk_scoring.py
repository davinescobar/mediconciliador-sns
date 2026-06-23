"""Assigns risk level (LOW/MEDIUM/HIGH) to each discrepancy. Rules-based, no LLM."""

import json

_ANTICOAGULANTS = frozenset([
    "warfarin", "apixaban", "rivaroxaban", "dabigatran",
    "acenocoumarol", "heparin", "enoxaparin", "bemiparin",
])
_NSAIDS = frozenset([
    "ibuprofen", "naproxen", "diclofenac", "ketoprofen", "indomethacin",
    "celecoxib", "etoricoxib", "meloxicam", "piroxicam",
])
_HF_DIURETICS = frozenset([
    "furosemide", "torasemide", "hydrochlorothiazide", "spironolactone",
])
_NARROW_TI = frozenset([
    "digoxin", "lithium", "theophylline", "phenytoin", "warfarin",
    "ciclosporin", "tacrolimus",
])
_HIGH_RISK_ANTIDIABETICS = frozenset([
    "insulin", "glibenclamide", "glipizide", "gliclazide",
])


def _med_categories(name: str) -> set[str]:
    cats: set[str] = set()
    if name in _ANTICOAGULANTS:
        cats.add("anticoagulant")
    if name in _NSAIDS:
        cats.add("nsaid")
    if name in _HF_DIURETICS:
        cats.add("hf_diuretic")
    if name in _NARROW_TI:
        cats.add("narrow_ti")
    if name in _HIGH_RISK_ANTIDIABETICS:
        cats.add("high_risk_antidiabetic")
    return cats


def score_discrepancy_risk(
    discrepancies_json: str,
    discharge_meds_json: str = "[]",
    context_json: str = "{}",
) -> str:
    """
    Assigns risk level and rationale to each discrepancy.

    Rules:
    - NSAID + anticoagulant present in discharge → HIGH (interaction risk)
    - Discontinued anticoagulant / narrow-TI / high-risk antidiabetic still taken → HIGH
    - Diuretic omission with heart_failure in risk factors → HIGH
    - Possible duplication → LOW (uncertainty, not escalated until confirmed)
    - Other omissions and undocumented medications → MEDIUM by default

    Args:
        discrepancies_json: JSON array from detect_discrepancies.
        discharge_meds_json: JSON array of normalized discharge medications.
        context_json: JSON dict with optional 'risk_factors' list.

    Returns:
        JSON array with 'risk_level' and 'rationale' added to each discrepancy.
    """
    discrepancies = json.loads(discrepancies_json)
    discharge = json.loads(discharge_meds_json)
    context = json.loads(context_json)

    discharge_names = {m["name"] for m in discharge}
    risk_factors = set(context.get("risk_factors", []))
    has_heart_failure = "heart_failure" in risk_factors
    anticoagulants_in_discharge = discharge_names & _ANTICOAGULANTS

    for d in discrepancies:
        med_name = d["medication"].split(" / ")[0].split(" vs ")[0].strip()
        cats = _med_categories(med_name)
        disc_type = d["type"]
        rationale_parts: list[str] = []

        if disc_type == "discontinued_medication_still_taken":
            if "nsaid" in cats and anticoagulants_in_discharge:
                risk_level = "HIGH"
                rationale_parts.append(
                    "NSAID combined with anticoagulant: high risk of GI bleeding "
                    "and renal impairment, especially in elderly patients"
                )
            elif cats & {"anticoagulant", "narrow_ti", "high_risk_antidiabetic"}:
                risk_level = "HIGH"
                present = cats & {"anticoagulant", "narrow_ti", "high_risk_antidiabetic"}
                rationale_parts.append(
                    f"High-risk drug category ({', '.join(sorted(present))}): "
                    "discontinued medication still being taken"
                )
            elif "nsaid" in cats:
                risk_level = "MEDIUM"
                rationale_parts.append("NSAID still taken after discontinuation: check for interactions")
            else:
                risk_level = "MEDIUM"
                rationale_parts.append("Discontinued medication still taken: requires professional review")

        elif disc_type == "omission_in_prescription":
            if "hf_diuretic" in cats and has_heart_failure:
                risk_level = "HIGH"
                rationale_parts.append(
                    "Diuretic omission in a heart failure patient: "
                    "risk of fluid retention and cardiac decompensation"
                )
            elif cats & {"anticoagulant", "narrow_ti"}:
                risk_level = "HIGH"
                rationale_parts.append(
                    f"High-risk drug omission from prescription ({', '.join(sorted(cats))})"
                )
            elif cats:
                risk_level = "MEDIUM"
                rationale_parts.append(f"Prescription omission in {', '.join(sorted(cats))} category")
            else:
                risk_level = "MEDIUM"
                rationale_parts.append("Prescription omission: verify with prescriber")

        elif disc_type == "possible_duplication":
            risk_level = "LOW"
            rationale_parts.append(
                "Possible OTC/prescription duplication — identity of OTC product "
                "must be confirmed before escalating risk"
            )

        elif disc_type == "undocumented_patient_medication":
            risk_level = "MEDIUM"
            rationale_parts.append("Undocumented medication: source and interactions unknown")

        else:
            risk_level = "MEDIUM"
            rationale_parts.append("Requires professional review")

        d["risk_level"] = risk_level
        d["rationale"] = ". ".join(rationale_parts)

    return json.dumps(discrepancies, ensure_ascii=False, indent=2)
