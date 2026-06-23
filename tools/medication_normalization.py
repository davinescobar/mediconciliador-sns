"""Normalizes medication names: brand → generic. No LLM calls."""

import json

_BRAND_TO_GENERIC: dict[str, str] = {
    # NSAIDs
    "nurofen": "ibuprofen",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "voltaren": "diclofenac",
    "voltarol": "diclofenac",
    # PPIs
    "losec": "omeprazole",
    "omeprazol": "omeprazole",
    "pantoprazol": "pantoprazole",
    "stomach protector": "unidentified_ppi",
    "protector de estomago": "unidentified_ppi",
    "protector gástrico": "unidentified_ppi",
    # Anticoagulants
    "eliquis": "apixaban",
    "xarelto": "rivaroxaban",
    "pradaxa": "dabigatran",
    "sintrom": "acenocoumarol",
    # Cardiac
    "concor": "bisoprolol",
    "emconcor": "bisoprolol",
    "eucardic": "carvedilol",
    "lasix": "furosemide",
    "seguril": "furosemide",
    "furosemida": "furosemide",
    "norvasc": "amlodipine",
    "istin": "amlodipine",
    # RAAS
    "tritace": "ramipril",
    "zestril": "lisinopril",
    # Antidiabetics
    "glucophage": "metformin",
    "metformina": "metformin",
    # Supplements
    "calcium supplement": "calcium carbonate + vitamin d",
    "calcio": "calcium carbonate + vitamin d",
    "suplemento calcio": "calcium carbonate + vitamin d",
}


def normalize_medication_name(name: str) -> str:
    """Returns the generic name for a medication, or the input unchanged if not in the lookup."""
    clean = name.lower().strip()
    return _BRAND_TO_GENERIC.get(clean, clean)


def normalize_medication_list(meds_json: str) -> str:
    """
    Normalizes all medication names in a list to their generic equivalents.

    Args:
        meds_json: JSON array of medication dicts (output of extract_medications).

    Returns:
        JSON array with 'name' set to generic name and 'name_original' preserving the original.
    """
    meds = json.loads(meds_json)
    for med in meds:
        med["name_original"] = med["name"]
        med["name"] = normalize_medication_name(med["name"])
    return json.dumps(meds, ensure_ascii=False)
