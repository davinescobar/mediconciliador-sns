"""
MCP Server — MediConciliador SNS

Exposes synthetic medication data via MCP protocol. Read-only (SELECT only).
Backed by SQLite populated from data/synthetic_cases.json.

Tools:
- get_case_list()
- get_synthetic_case(case_id)
- get_discharge_summary(case_id)
- get_active_prescription(case_id)
- get_patient_interview(case_id)
- get_allergies(case_id)
- get_risk_factors(case_id)
- get_high_risk_medications()
- get_reconciliation_guidance()

Run:
    python mcp/db_init.py   # once
    python mcp/mcp_server.py
"""

import json
import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mediconciliador.db"


def _connect() -> sqlite3.Connection:
    """Opens the DB in read-only mode. Raises if DB does not exist."""
    uri = f"file:{DB_PATH}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _not_found(case_id: str) -> str:
    return json.dumps({"error": f"Case '{case_id}' not found"})


# — Private fetch functions (used by MCP tools and importable for tests) ——

def _fetch_case_list() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT case_id, title FROM cases ORDER BY case_id"
        ).fetchall()
    return [{"case_id": r[0], "title": r[1]} for r in rows]


def _fetch_synthetic_case(case_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            """SELECT case_id, title, patient_profile, discharge_summary,
                      active_prescription, patient_interview
               FROM cases WHERE case_id = ?""",
            (case_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "case_id": row[0],
        "title": row[1],
        "patient_profile": json.loads(row[2]),
        "discharge_summary": json.loads(row[3]),
        "active_prescription": json.loads(row[4]),
        "patient_interview": json.loads(row[5]),
    }


def _fetch_discharge_summary(case_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT discharge_summary FROM cases WHERE case_id = ?", (case_id,)
        ).fetchone()
    return json.loads(row[0]) if row else None


def _fetch_active_prescription(case_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT active_prescription FROM cases WHERE case_id = ?", (case_id,)
        ).fetchone()
    return json.loads(row[0]) if row else None


def _fetch_patient_interview(case_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT patient_interview FROM cases WHERE case_id = ?", (case_id,)
        ).fetchone()
    return json.loads(row[0]) if row else None


def _fetch_allergies(case_id: str) -> list[str] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT patient_profile FROM cases WHERE case_id = ?", (case_id,)
        ).fetchone()
    if row is None:
        return None
    return json.loads(row[0]).get("allergies", [])


def _fetch_risk_factors(case_id: str) -> list[str] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT patient_profile FROM cases WHERE case_id = ?", (case_id,)
        ).fetchone()
    if row is None:
        return None
    return json.loads(row[0]).get("risk_factors", [])


def _fetch_high_risk_medications() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT category, risk_level, examples, key_interactions, reconciliation_note "
            "FROM high_risk_medications"
        ).fetchall()
    return [
        {
            "category": r[0],
            "risk_level": r[1],
            "examples": json.loads(r[2]),
            "key_interactions": json.loads(r[3]),
            "reconciliation_note": r[4],
        }
        for r in rows
    ]


def _fetch_reconciliation_guidance() -> dict:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT key, content FROM reconciliation_guidance"
        ).fetchall()
    return {key: json.loads(content) for key, content in rows}


# — MCP tool definitions ————————————————————————————————————————————————

mcp = FastMCP("mediconciliador-mcp")


@mcp.tool()
def get_case_list() -> str:
    """Returns a list of all available synthetic cases (case_id and title)."""
    return json.dumps(_fetch_case_list(), ensure_ascii=False, indent=2)


@mcp.tool()
def get_synthetic_case(case_id: str) -> str:
    """Returns the full synthetic case record for a given case_id."""
    result = _fetch_synthetic_case(case_id)
    return _not_found(case_id) if result is None else json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_discharge_summary(case_id: str) -> str:
    """Returns the hospital discharge summary for a given case_id."""
    result = _fetch_discharge_summary(case_id)
    return _not_found(case_id) if result is None else json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_active_prescription(case_id: str) -> str:
    """Returns the active prescription list for a given case_id."""
    result = _fetch_active_prescription(case_id)
    return _not_found(case_id) if result is None else json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_patient_interview(case_id: str) -> str:
    """Returns the patient interview transcript for a given case_id."""
    result = _fetch_patient_interview(case_id)
    return _not_found(case_id) if result is None else json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_allergies(case_id: str) -> str:
    """Returns the documented allergies for a patient in a given case_id."""
    result = _fetch_allergies(case_id)
    if result is None:
        return _not_found(case_id)
    return json.dumps({"case_id": case_id, "allergies": result}, ensure_ascii=False, indent=2)


@mcp.tool()
def get_risk_factors(case_id: str) -> str:
    """Returns the clinical risk factors for a patient in a given case_id."""
    result = _fetch_risk_factors(case_id)
    if result is None:
        return _not_found(case_id)
    return json.dumps({"case_id": case_id, "risk_factors": result}, ensure_ascii=False, indent=2)


@mcp.tool()
def get_high_risk_medications() -> str:
    """Returns the reference list of high-risk medication categories with interaction notes."""
    return json.dumps(_fetch_high_risk_medications(), ensure_ascii=False, indent=2)


@mcp.tool()
def get_reconciliation_guidance() -> str:
    """Returns structured guidance: reconciliation principles, discrepancy types, risk scoring rules."""
    return json.dumps(_fetch_reconciliation_guidance(), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
