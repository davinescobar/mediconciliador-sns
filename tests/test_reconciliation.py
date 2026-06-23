"""
Tests for discrepancy detection — validates case_001 expected output
against the gold standard in data/gold_standard_discrepancies.json.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.medication_extraction import extract_medications, extract_discontinued
from tools.medication_normalization import normalize_medication_list
from tools.discrepancy_detection import detect_discrepancies
from tools.report_generation import run_full_analysis


# ── Helpers ─────────────────────────────────────────────────────────────────

def _load_case(case_id: str) -> dict:
    path = Path(__file__).parent.parent / "data" / "synthetic_cases.json"
    cases = json.loads(path.read_text())
    return next(c for c in cases if c["case_id"] == case_id)


def _normalized_meds(source_json: str, source_type: str) -> str:
    raw = extract_medications(source_json, source_type)
    return normalize_medication_list(raw)


# ── detect_discrepancies — case_001 ─────────────────────────────────────────

class TestDetectDiscrepanciesCase001:
    def setup_method(self):
        case = _load_case("case_001")
        discharge_json = json.dumps(case["discharge_summary"])
        prescription_json = json.dumps(case["active_prescription"])
        interview_json = json.dumps(case["patient_interview"])
        discontinued_json = extract_discontinued(discharge_json)

        discharge_norm = _normalized_meds(discharge_json, "discharge")
        prescription_norm = _normalized_meds(prescription_json, "prescription")
        interview_norm = _normalized_meds(interview_json, "interview")

        self.discrepancies = json.loads(
            detect_discrepancies(
                discharge_norm,
                prescription_norm,
                interview_norm,
                discontinued_json,
            )
        )

    def test_detects_at_least_one_discrepancy(self):
        assert len(self.discrepancies) >= 1

    def test_detects_ibuprofen_discontinued_still_taken(self):
        types = {d["type"] for d in self.discrepancies}
        assert "discontinued_medication_still_taken" in types

    def test_ibuprofen_flagged_as_discontinued(self):
        disc = next(
            d for d in self.discrepancies
            if d["type"] == "discontinued_medication_still_taken"
        )
        assert "ibuprofen" in disc["medication"]

    def test_no_false_positives_for_prescribed_meds(self):
        # apixaban, bisoprolol, omeprazole all match across sources — no omission
        omissions = [d for d in self.discrepancies if d["type"] == "omission_in_prescription"]
        for o in omissions:
            assert o["medication"] not in {"apixaban", "bisoprolol", "omeprazole"}


# ── detect_discrepancies — case_002 ─────────────────────────────────────────

class TestDetectDiscrepanciesCase002:
    def setup_method(self):
        case = _load_case("case_002")
        discharge_json = json.dumps(case["discharge_summary"])
        prescription_json = json.dumps(case["active_prescription"])
        interview_json = json.dumps(case["patient_interview"])
        discontinued_json = extract_discontinued(discharge_json)

        discharge_norm = _normalized_meds(discharge_json, "discharge")
        prescription_norm = _normalized_meds(prescription_json, "prescription")
        interview_norm = _normalized_meds(interview_json, "interview")

        self.discrepancies = json.loads(
            detect_discrepancies(
                discharge_norm,
                prescription_norm,
                interview_norm,
                discontinued_json,
            )
        )

    def test_detects_furosemide_omission(self):
        types = {d["type"] for d in self.discrepancies}
        assert "omission_in_prescription" in types

    def test_furosemide_is_the_omitted_drug(self):
        omissions = [d for d in self.discrepancies if d["type"] == "omission_in_prescription"]
        meds = {d["medication"] for d in omissions}
        assert "furosemide" in meds


# ── detect_discrepancies — case_003 ─────────────────────────────────────────

class TestDetectDiscrepanciesCase003:
    def setup_method(self):
        case = _load_case("case_003")
        discharge_json = json.dumps(case["discharge_summary"])
        prescription_json = json.dumps(case["active_prescription"])
        interview_json = json.dumps(case["patient_interview"])
        discontinued_json = extract_discontinued(discharge_json)

        discharge_norm = _normalized_meds(discharge_json, "discharge")
        prescription_norm = _normalized_meds(prescription_json, "prescription")
        interview_norm = _normalized_meds(interview_json, "interview")

        self.discrepancies = json.loads(
            detect_discrepancies(
                discharge_norm,
                prescription_norm,
                interview_norm,
                discontinued_json,
            )
        )

    def test_detects_possible_ppi_duplication(self):
        types = {d["type"] for d in self.discrepancies}
        assert "possible_duplication" in types

    def test_duplication_involves_omeprazole(self):
        dups = [d for d in self.discrepancies if d["type"] == "possible_duplication"]
        assert any("omeprazole" in d["medication"] for d in dups)


# ── run_full_analysis pipeline ───────────────────────────────────────────────

class TestRunFullAnalysis:
    def test_case_001_returns_high_risk(self):
        case = _load_case("case_001")
        case_data = {
            "case_id": "case_001",
            "discharge_summary": case["discharge_summary"],
            "active_prescription": case["active_prescription"],
            "patient_interview": case["patient_interview"],
            "risk_factors": case["patient_profile"]["risk_factors"],
        }
        report = json.loads(run_full_analysis(json.dumps(case_data)))

        assert report["case_id"] == "case_001"
        assert report["summary"]["high_risk"] >= 1
        assert report["requires_professional_review"] is True

    def test_case_001_ibuprofen_flagged_high(self):
        case = _load_case("case_001")
        case_data = {
            "case_id": "case_001",
            "discharge_summary": case["discharge_summary"],
            "active_prescription": case["active_prescription"],
            "patient_interview": case["patient_interview"],
            "risk_factors": case["patient_profile"]["risk_factors"],
        }
        report = json.loads(run_full_analysis(json.dumps(case_data)))
        high_meds = [
            d["medication"]
            for d in report["discrepancies"]
            if d["risk_level"] == "HIGH"
        ]
        assert any("ibuprofen" in m for m in high_meds)

    def test_report_includes_trace(self):
        case = _load_case("case_001")
        case_data = {
            "case_id": "case_001",
            "discharge_summary": case["discharge_summary"],
            "active_prescription": case["active_prescription"],
            "patient_interview": case["patient_interview"],
            "risk_factors": [],
        }
        report = json.loads(run_full_analysis(json.dumps(case_data)))
        assert len(report["trace"]) > 0

    def test_case_002_furosemide_flagged_high(self):
        case = _load_case("case_002")
        case_data = {
            "case_id": "case_002",
            "discharge_summary": case["discharge_summary"],
            "active_prescription": case["active_prescription"],
            "patient_interview": case["patient_interview"],
            "risk_factors": case["patient_profile"]["risk_factors"],
        }
        report = json.loads(run_full_analysis(json.dumps(case_data)))
        high_meds = [
            d["medication"]
            for d in report["discrepancies"]
            if d["risk_level"] == "HIGH"
        ]
        assert any("furosemide" in m for m in high_meds)

    def test_case_003_duplication_low_risk(self):
        case = _load_case("case_003")
        case_data = {
            "case_id": "case_003",
            "discharge_summary": case["discharge_summary"],
            "active_prescription": case["active_prescription"],
            "patient_interview": case["patient_interview"],
            "risk_factors": case["patient_profile"]["risk_factors"],
        }
        report = json.loads(run_full_analysis(json.dumps(case_data)))
        dups = [d for d in report["discrepancies"] if d["type"] == "possible_duplication"]
        assert len(dups) >= 1
        assert all(d["risk_level"] == "LOW" for d in dups)

    def test_report_includes_reconciliation_table(self):
        case = _load_case("case_001")
        case_data = {
            "case_id": "case_001",
            "discharge_summary": case["discharge_summary"],
            "active_prescription": case["active_prescription"],
            "patient_interview": case["patient_interview"],
            "risk_factors": case["patient_profile"]["risk_factors"],
        }
        report = json.loads(run_full_analysis(json.dumps(case_data)))
        table = report.get("reconciliation_table", [])
        assert isinstance(table, list)
        assert len(table) > 0
        row_keys = {"medication", "discharge_summary", "active_prescription", "patient_interview"}
        assert all(row_keys.issubset(r.keys()) for r in table)

    def test_reconciliation_table_ibuprofen_marked_suspended(self):
        case = _load_case("case_001")
        case_data = {
            "case_id": "case_001",
            "discharge_summary": case["discharge_summary"],
            "active_prescription": case["active_prescription"],
            "patient_interview": case["patient_interview"],
            "risk_factors": case["patient_profile"]["risk_factors"],
        }
        report = json.loads(run_full_analysis(json.dumps(case_data)))
        table = report["reconciliation_table"]
        ibuprofen_rows = [r for r in table if r["medication"] == "ibuprofen"]
        assert len(ibuprofen_rows) == 1
        assert ibuprofen_rows[0]["discharge_summary"] == "SUSPENDIDO"

    def test_reconciliation_table_high_risk_sorted_first(self):
        case = _load_case("case_001")
        case_data = {
            "case_id": "case_001",
            "discharge_summary": case["discharge_summary"],
            "active_prescription": case["active_prescription"],
            "patient_interview": case["patient_interview"],
            "risk_factors": case["patient_profile"]["risk_factors"],
        }
        report = json.loads(run_full_analysis(json.dumps(case_data)))
        table = report["reconciliation_table"]
        high_risk_indices = [i for i, r in enumerate(table) if r.get("risk_level") == "HIGH"]
        non_high_indices = [i for i, r in enumerate(table) if r.get("risk_level") != "HIGH"]
        if high_risk_indices and non_high_indices:
            assert max(high_risk_indices) < min(non_high_indices)
