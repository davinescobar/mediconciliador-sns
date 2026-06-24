"""
Tests for MCP server read-only enforcement and data integrity.

Criterion: pytest passes green → Session 2 complete.

Test strategy:
- init_db fixture populates the SQLite DB via db_init.py
- Data integrity tests query the DB via the private _fetch_* functions
  (imported with importlib to avoid name collision with the `mcp` pip package)
- Read-only tests verify that the connection mode blocks writes
"""

import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mediconciliador.db"


# — Fixtures ——————————————————————————————————————————————————————————————

@pytest.fixture(scope="session", autouse=True)
def init_db():
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "mcp" / "db_init.py")],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "initialised" in result.stdout


def _ro_conn() -> sqlite3.Connection:
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def _load_server():
    """Import mcp_server.py as '_mcp_server' to avoid collision with the mcp package."""
    spec = importlib.util.spec_from_file_location(
        "_mcp_server", PROJECT_ROOT / "mcp" / "mcp_server.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def server():
    return _load_server()


# — Server structure ——————————————————————————————————————————————————————

class TestServerStructure:
    def test_has_mcp_instance(self, server):
        assert hasattr(server, "mcp")

    def test_all_9_tools_defined(self, server):
        expected = {
            "get_case_list", "get_synthetic_case", "get_discharge_summary",
            "get_active_prescription", "get_patient_interview", "get_allergies",
            "get_risk_factors", "get_high_risk_medications", "get_reconciliation_guidance",
        }
        for name in expected:
            assert hasattr(server, name), f"Missing tool function: {name}"


# — Case list —————————————————————————————————————————————————————————————

class TestCaseList:
    def test_returns_ten_cases(self, server):
        cases = server._fetch_case_list()
        assert len(cases) == 10

    def test_case_ids(self, server):
        ids = {c["case_id"] for c in server._fetch_case_list()}
        assert ids == {
            "case_001", "case_002", "case_003", "case_004", "case_005",
            "case_006", "case_007", "case_008", "case_009", "case_010",
        }

    def test_tool_returns_valid_json(self, server):
        result = server.get_case_list()
        parsed = json.loads(result)
        assert isinstance(parsed, list)


# — Synthetic case ————————————————————————————————————————————————————————

class TestSyntheticCase:
    def test_case_001_exists(self, server):
        case = server._fetch_synthetic_case("case_001")
        assert case is not None
        assert case["case_id"] == "case_001"

    def test_full_structure(self, server):
        case = server._fetch_synthetic_case("case_001")
        assert "patient_profile" in case
        assert "discharge_summary" in case
        assert "active_prescription" in case
        assert "patient_interview" in case

    def test_unknown_returns_none(self, server):
        assert server._fetch_synthetic_case("case_999") is None

    def test_tool_not_found_returns_error_json(self, server):
        result = json.loads(server.get_synthetic_case("case_999"))
        assert "error" in result


# — Discharge summary ————————————————————————————————————————————————————

class TestDischargeSummary:
    def test_case_001_has_apixaban(self, server):
        ds = server._fetch_discharge_summary("case_001")
        names = [m["name"] for m in ds["medications_at_discharge"]]
        assert "apixaban" in names

    def test_case_001_ibuprofen_discontinued(self, server):
        ds = server._fetch_discharge_summary("case_001")
        stopped = [m["name"] for m in ds["medications_discontinued_at_discharge"]]
        assert "ibuprofen" in stopped

    def test_case_002_furosemide_at_discharge(self, server):
        ds = server._fetch_discharge_summary("case_002")
        names = [m["name"] for m in ds["medications_at_discharge"]]
        assert "furosemide" in names


# — Active prescription ——————————————————————————————————————————————————

class TestActivePrescription:
    def test_case_002_furosemide_missing(self, server):
        """Core discrepancy for case_002: furosemide in discharge but absent from prescription."""
        ap = server._fetch_active_prescription("case_002")
        names = [m["name"] for m in ap["medications"]]
        assert "furosemide" not in names

    def test_case_001_apixaban_present(self, server):
        ap = server._fetch_active_prescription("case_001")
        names = [m["name"] for m in ap["medications"]]
        assert "apixaban" in names


# — Patient interview ————————————————————————————————————————————————————

class TestPatientInterview:
    def test_case_001_patient_takes_ibuprofen(self, server):
        """Core discrepancy for case_001: ibuprofen discontinued but patient still takes it."""
        pi = server._fetch_patient_interview("case_001")
        names = [m["name"] for m in pi["reported_medications"]]
        assert "ibuprofen" in names

    def test_case_002_caregiver_not_present(self, server):
        pi = server._fetch_patient_interview("case_002")
        assert pi["caregiver_present"] is False

    def test_case_003_patient_reports_stomach_protector(self, server):
        """Core discrepancy for case_003: possible brand/generic duplication."""
        pi = server._fetch_patient_interview("case_003")
        names = [m["name"] for m in pi["reported_medications"]]
        assert "stomach protector" in names


# — Allergies ————————————————————————————————————————————————————————————

class TestAllergies:
    def test_case_001_penicillin(self, server):
        allergies = server._fetch_allergies("case_001")
        assert "penicillin" in allergies

    def test_case_002_no_allergies(self, server):
        assert server._fetch_allergies("case_002") == []

    def test_unknown_returns_none(self, server):
        assert server._fetch_allergies("case_999") is None


# — Risk factors ————————————————————————————————————————————————————————

class TestRiskFactors:
    def test_case_001_has_afib(self, server):
        rf = server._fetch_risk_factors("case_001")
        assert "atrial_fibrillation" in rf

    def test_case_001_has_ckd(self, server):
        rf = server._fetch_risk_factors("case_001")
        assert "chronic_kidney_disease" in rf

    def test_case_003_has_cognitive_impairment(self, server):
        rf = server._fetch_risk_factors("case_003")
        assert "cognitive_mild_impairment" in rf


# — High-risk medications ————————————————————————————————————————————————

class TestHighRiskMedications:
    def test_returns_all_categories(self, server):
        cats = server._fetch_high_risk_medications()
        assert len(cats) >= 20

    def test_anticoagulants_high_risk(self, server):
        cats = {c["category"]: c for c in server._fetch_high_risk_medications()}
        assert cats["anticoagulants"]["risk_level"] == "HIGH"

    def test_apixaban_in_anticoagulants(self, server):
        cats = {c["category"]: c for c in server._fetch_high_risk_medications()}
        assert "apixaban" in cats["anticoagulants"]["examples"]

    def test_ibuprofen_in_nsaids(self, server):
        cats = {c["category"]: c for c in server._fetch_high_risk_medications()}
        assert "ibuprofen" in cats["nsaids"]["examples"]

    def test_furosemide_in_diuretics(self, server):
        cats = {c["category"]: c for c in server._fetch_high_risk_medications()}
        assert "furosemide" in cats["diuretics"]["examples"]


# — Reconciliation guidance ——————————————————————————————————————————————

class TestReconciliationGuidance:
    def test_has_principles(self, server):
        g = server._fetch_reconciliation_guidance()
        assert "principles" in g

    def test_has_discrepancy_types(self, server):
        g = server._fetch_reconciliation_guidance()
        assert "discrepancy_types" in g
        assert "omission" in g["discrepancy_types"]

    def test_has_risk_scoring_rules(self, server):
        g = server._fetch_reconciliation_guidance()
        assert "risk_scoring_rules" in g
        assert "HIGH" in g["risk_scoring_rules"]


# — Read-only enforcement ————————————————————————————————————————————————

class TestReadOnly:
    def test_insert_blocked(self):
        conn = _ro_conn()
        with pytest.raises(sqlite3.OperationalError):
            conn.execute(
                "INSERT INTO cases VALUES ('x','x','{}','{}','{}','{}')"
            )
        conn.close()

    def test_update_blocked(self):
        conn = _ro_conn()
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("UPDATE cases SET title = 'hacked' WHERE case_id = 'case_001'")
        conn.close()

    def test_delete_blocked(self):
        conn = _ro_conn()
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("DELETE FROM cases WHERE case_id = 'case_001'")
        conn.close()

    def test_drop_table_blocked(self):
        conn = _ro_conn()
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("DROP TABLE cases")
        conn.close()
