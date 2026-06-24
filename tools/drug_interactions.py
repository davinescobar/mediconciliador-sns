"""
Drug interaction checker.

check_drug_interactions  — public API used by run_full_analysis.
                           Tries NLM RxNorm; falls back to static table on any failure.
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path

_STATIC_PATH = Path(__file__).parent.parent / "data" / "high_risk_medications.json"
_NLM_RXCUI_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json?name={}&search=1"
_NLM_INTERACTION_URL = "https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={}"
_TIMEOUT = 4


def _load_static() -> list[dict]:
    with open(_STATIC_PATH, encoding="utf-8") as f:
        return json.load(f)["categories"]


def get_rxcui(drug_name: str) -> str | None:
    """Returns the first RxCUI for drug_name, or None on failure."""
    url = _NLM_RXCUI_URL.format(urllib.parse.quote(drug_name))
    try:
        with urllib.request.urlopen(url, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read())
        ids = (
            data.get("idGroup", {}).get("rxnormId", [])
        )
        return ids[0] if ids else None
    except Exception:
        return None


def _fetch_nlm_interactions(rxcuis: list[str]) -> list[dict]:
    """Calls NLM interaction API for a list of RxCUIs. Returns interaction dicts."""
    if len(rxcuis) < 2:
        return []
    ids_str = "+".join(rxcuis)
    url = _NLM_INTERACTION_URL.format(ids_str)
    with urllib.request.urlopen(url, timeout=_TIMEOUT) as resp:
        data = json.loads(resp.read())

    results = []
    for group in data.get("fullInteractionTypeGroup", []):
        for itype in group.get("fullInteractionType", []):
            for pair in itype.get("interactionPair", []):
                concepts = pair.get("interactionConcept", [])
                if len(concepts) < 2:
                    continue
                results.append({
                    "drug1": concepts[0]["minConceptItem"]["name"],
                    "drug2": concepts[1]["minConceptItem"]["name"],
                    "severity": pair.get("severity", "unknown"),
                    "description": pair.get("description", ""),
                })
    return results


def _static_interactions(drug_names: list[str]) -> list[dict]:
    """
    Fallback: cross-checks drug_names against key_interactions in the static table.
    Returns interaction dicts with severity derived from the category risk_level.
    """
    categories = _load_static()

    drug_lower = [d.lower() for d in drug_names]

    # map each provided drug → its category entry (first match wins)
    drug_to_cat: dict[str, dict] = {}
    for cat in categories:
        for example in cat.get("examples", []):
            ex_l = example.lower()
            for name in drug_lower:
                if name in ex_l or ex_l in name:
                    if name not in drug_to_cat:
                        drug_to_cat[name] = cat

    _severity_map = {"HIGH": "high", "MEDIUM": "moderate", "LOW": "low"}

    results = []
    checked: set[tuple[str, str]] = set()

    for drug_a, cat_a in drug_to_cat.items():
        for drug_b, cat_b in drug_to_cat.items():
            if drug_a == drug_b:
                continue
            pair = tuple(sorted([drug_a, drug_b]))
            if pair in checked:
                continue
            checked.add(pair)

            # check if cat_b's category name or drug_b appears in cat_a's key_interactions
            interactions_a = [k.lower() for k in cat_a.get("key_interactions", [])]
            cat_b_name = cat_b["category"].lower()
            match = cat_b_name in interactions_a or any(
                drug_b in ki or ki in drug_b for ki in interactions_a
            )
            if not match:
                # also check reverse
                interactions_b = [k.lower() for k in cat_b.get("key_interactions", [])]
                cat_a_name = cat_a["category"].lower()
                match = cat_a_name in interactions_b or any(
                    drug_a in ki or ki in drug_a for ki in interactions_b
                )

            if match:
                severity = _severity_map.get(
                    cat_a["risk_level"] if cat_a["risk_level"] >= cat_b["risk_level"] else cat_b["risk_level"],
                    "moderate",
                )
                results.append({
                    "drug1": drug_a,
                    "drug2": drug_b,
                    "severity": severity,
                    "description": cat_a.get("reconciliation_note", ""),
                })

    return results


def check_drug_interactions(drug_names: list[str]) -> dict:
    """
    Returns interaction data for the given list of drug names.

    Tries NLM RxNorm first (4s timeout per request). Falls back to the
    static high_risk_medications.json table on any network or parse error.

    Returns:
        {
            "source": "nlm" | "static",
            "interactions": [
                {"drug1": str, "drug2": str, "severity": str, "description": str},
                ...
            ]
        }
    """
    if not drug_names or len(drug_names) < 2:
        return {"source": "static", "interactions": []}

    try:
        rxcuis = []
        for name in drug_names:
            cui = get_rxcui(name)
            if cui:
                rxcuis.append(cui)

        if len(rxcuis) >= 2:
            interactions = _fetch_nlm_interactions(rxcuis)
            return {"source": "nlm", "interactions": interactions}
    except Exception:
        pass

    return {"source": "static", "interactions": _static_interactions(drug_names)}
