"""
Initialize SQLite database for MediConciliador SNS.

Loads data/synthetic_cases.json and data/high_risk_medications.json into tables.
Run once (or whenever source JSON changes) before starting the MCP server.

Usage:
    python mcp/db_init.py
"""

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "mediconciliador.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS cases (
    case_id            TEXT PRIMARY KEY,
    title              TEXT NOT NULL,
    patient_profile    TEXT NOT NULL,
    discharge_summary  TEXT NOT NULL,
    active_prescription TEXT NOT NULL,
    patient_interview  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS high_risk_medications (
    category           TEXT PRIMARY KEY,
    risk_level         TEXT NOT NULL,
    examples           TEXT NOT NULL,
    key_interactions   TEXT NOT NULL,
    reconciliation_note TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reconciliation_guidance (
    key     TEXT PRIMARY KEY,
    content TEXT NOT NULL
);
"""

_RECONCILIATION_GUIDANCE = {
    "principles": (
        "Medication reconciliation compares patient medications across all sources to avoid "
        "errors such as omissions, duplications, dosing errors, or drug interactions. "
        "Sources: (1) hospital discharge summary, (2) active prescription list, "
        "(3) patient/caregiver interview. All discrepancies require professional review "
        "before any action is taken. The agent does not modify any medication list. "
        "Uncertainty must be explicitly stated when data is incomplete or ambiguous."
    ),
    "discrepancy_types": {
        "omission": "Present in one source, absent in another without documented justification.",
        "duplication": "Same medication under two different names (brand + generic) or two separate entries.",
        "discontinued_medication_still_taken": "Marked as stopped at discharge but patient reports still taking it.",
        "new_medication_not_in_prescription": "Patient reports a medication not documented in any clinical source.",
        "dose_mismatch": "Dose differs across sources without explanation.",
        "frequency_mismatch": "Frequency of administration differs across sources.",
        "route_mismatch": "Route of administration differs.",
        "patient_uncertainty": "Patient or caregiver is uncertain about a medication, dose, or whether still taking it.",
        "possible_allergy_issue": "A medication matches or potentially matches a documented patient allergy.",
        "high_risk_medication_issue": "A high-risk drug (anticoagulant, NSAID, etc.) has any discrepancy — classify MEDIUM or HIGH.",
        "self_medication_or_otc_issue": "Patient reports an OTC drug or supplement not documented anywhere.",
    },
    "risk_scoring_rules": {
        "HIGH": [
            "Anticoagulant involved in any discrepancy",
            "NSAID + anticoagulant combination present",
            "Allergy match detected",
            "Discontinued drug still being taken by patient",
            "Narrow therapeutic index drug with any discrepancy",
        ],
        "MEDIUM": [
            "Diuretic omission (escalate to HIGH if heart failure present)",
            "Dose mismatch for non-high-risk drug",
            "OTC medication undocumented",
            "Benzodiazepine or Z-drug discrepancy in elderly patient",
        ],
        "LOW": [
            "Brand/generic duplication for a low-risk drug",
            "Timing discrepancy only (morning vs. evening for stable drug)",
            "Patient uncertainty with no identified risk factor",
        ],
    },
}


def init_db(db_path: Path = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(_SCHEMA)
        _load_cases(conn)
        _load_high_risk_medications(conn)
        _load_reconciliation_guidance(conn)
        conn.commit()
        print(f"DB initialised at {db_path}")
    finally:
        conn.close()


def _load_cases(conn: sqlite3.Connection) -> None:
    cases = json.loads((DATA_DIR / "synthetic_cases.json").read_text(encoding="utf-8"))
    conn.executemany(
        """
        INSERT OR REPLACE INTO cases
            (case_id, title, patient_profile, discharge_summary, active_prescription, patient_interview)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                c["case_id"],
                c["title"],
                json.dumps(c["patient_profile"], ensure_ascii=False),
                json.dumps(c["discharge_summary"], ensure_ascii=False),
                json.dumps(c["active_prescription"], ensure_ascii=False),
                json.dumps(c["patient_interview"], ensure_ascii=False),
            )
            for c in cases
        ],
    )


def _load_high_risk_medications(conn: sqlite3.Connection) -> None:
    data = json.loads((DATA_DIR / "high_risk_medications.json").read_text(encoding="utf-8"))
    conn.executemany(
        """
        INSERT OR REPLACE INTO high_risk_medications
            (category, risk_level, examples, key_interactions, reconciliation_note)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                cat["category"],
                cat["risk_level"],
                json.dumps(cat["examples"], ensure_ascii=False),
                json.dumps(cat["key_interactions"], ensure_ascii=False),
                cat["reconciliation_note"],
            )
            for cat in data["categories"]
        ],
    )


def _load_reconciliation_guidance(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO reconciliation_guidance (key, content) VALUES (?, ?)",
        [(k, json.dumps(v, ensure_ascii=False)) for k, v in _RECONCILIATION_GUIDANCE.items()],
    )


if __name__ == "__main__":
    init_db()
