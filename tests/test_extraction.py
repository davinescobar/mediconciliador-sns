"""Tests for medication_extraction and medication_normalization tools."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from tools.medication_extraction import extract_medications, extract_discontinued
from tools.medication_normalization import normalize_medication_name, normalize_medication_list


# ── Fixtures ────────────────────────────────────────────────────────────────

DISCHARGE_001 = {
    "date": "2024-11-15",
    "medications_at_discharge": [
        {"name": "apixaban", "dose": "5 mg", "frequency": "twice daily", "route": "oral"},
        {"name": "bisoprolol", "dose": "2.5 mg", "frequency": "once daily", "route": "oral"},
        {"name": "omeprazole", "dose": "20 mg", "frequency": "once daily", "route": "oral"},
    ],
    "medications_discontinued_at_discharge": [
        {"name": "ibuprofen", "reason": "Contraindicated with anticoagulation."},
    ],
}

PRESCRIPTION_001 = {
    "medications": [
        {"name": "apixaban", "dose": "5 mg", "frequency": "twice daily", "route": "oral"},
        {"name": "bisoprolol", "dose": "2.5 mg", "frequency": "once daily", "route": "oral"},
        {"name": "omeprazole", "dose": "20 mg", "frequency": "once daily", "route": "oral"},
    ]
}

INTERVIEW_001 = {
    "reported_medications": [
        {"name": "apixaban", "dose": "5 mg", "frequency": "twice daily", "route": "oral", "patient_comment": "For my heart."},
        {"name": "bisoprolol", "dose": "2.5 mg", "frequency": "once daily", "route": "oral", "patient_comment": None},
        {"name": "omeprazole", "dose": "20 mg", "frequency": "once daily", "route": "oral", "patient_comment": "Stomach protector."},
        {"name": "ibuprofen", "dose": "600 mg", "frequency": "as needed", "route": "oral", "patient_comment": "For knee pain."},
    ]
}


# ── extract_medications ─────────────────────────────────────────────────────

class TestExtractMedications:
    def test_discharge_returns_correct_count(self):
        result = json.loads(extract_medications(json.dumps(DISCHARGE_001), "discharge"))
        assert len(result) == 3

    def test_discharge_names_are_lowercase(self):
        result = json.loads(extract_medications(json.dumps(DISCHARGE_001), "discharge"))
        names = {m["name"] for m in result}
        assert names == {"apixaban", "bisoprolol", "omeprazole"}

    def test_discharge_source_tag(self):
        result = json.loads(extract_medications(json.dumps(DISCHARGE_001), "discharge"))
        assert all(m["source"] == "discharge" for m in result)

    def test_prescription_extracts_medications_key(self):
        result = json.loads(extract_medications(json.dumps(PRESCRIPTION_001), "prescription"))
        assert len(result) == 3
        assert all(m["source"] == "prescription" for m in result)

    def test_interview_includes_patient_comment(self):
        result = json.loads(extract_medications(json.dumps(INTERVIEW_001), "interview"))
        ibup = next(m for m in result if m["name"] == "ibuprofen")
        assert ibup["patient_comment"] == "For knee pain."

    def test_interview_source_tag(self):
        result = json.loads(extract_medications(json.dumps(INTERVIEW_001), "interview"))
        assert all(m["source"] == "interview" for m in result)

    def test_unknown_source_type_returns_error(self):
        result = json.loads(extract_medications(json.dumps(DISCHARGE_001), "unknown"))
        assert "error" in result

    def test_empty_medications_list(self):
        data = {"medications_at_discharge": []}
        result = json.loads(extract_medications(json.dumps(data), "discharge"))
        assert result == []


class TestExtractDiscontinued:
    def test_extracts_discontinued_medication(self):
        result = json.loads(extract_discontinued(json.dumps(DISCHARGE_001)))
        assert len(result) == 1
        assert result[0]["name"] == "ibuprofen"

    def test_extracts_reason(self):
        result = json.loads(extract_discontinued(json.dumps(DISCHARGE_001)))
        assert "Contraindicated" in result[0]["reason"]

    def test_empty_discontinued_list(self):
        data = {"medications_at_discharge": [], "medications_discontinued_at_discharge": []}
        result = json.loads(extract_discontinued(json.dumps(data)))
        assert result == []


# ── normalize_medication_name ───────────────────────────────────────────────

class TestNormalizeMedicationName:
    @pytest.mark.parametrize("brand,generic", [
        ("nurofen", "ibuprofen"),
        ("Nurofen", "ibuprofen"),
        ("eliquis", "apixaban"),
        ("lasix", "furosemide"),
        ("stomach protector", "unidentified_ppi"),
        ("calcium supplement", "calcium carbonate + vitamin d"),
    ])
    def test_brand_to_generic(self, brand, generic):
        assert normalize_medication_name(brand) == generic

    def test_already_generic_passthrough(self):
        assert normalize_medication_name("ibuprofen") == "ibuprofen"
        assert normalize_medication_name("apixaban") == "apixaban"

    def test_unknown_name_passthrough(self):
        assert normalize_medication_name("unknown_drug_xyz") == "unknown_drug_xyz"

    def test_strips_whitespace(self):
        assert normalize_medication_name("  ibuprofen  ") == "ibuprofen"


class TestNormalizeMedicationList:
    def test_preserves_original_name(self):
        meds = [{"name": "nurofen", "source": "interview"}]
        result = json.loads(normalize_medication_list(json.dumps(meds)))
        assert result[0]["name_original"] == "nurofen"
        assert result[0]["name"] == "ibuprofen"

    def test_unknown_names_pass_through(self):
        meds = [{"name": "metformin", "source": "prescription"}]
        result = json.loads(normalize_medication_list(json.dumps(meds)))
        assert result[0]["name"] == "metformin"

    def test_empty_list(self):
        result = json.loads(normalize_medication_list("[]"))
        assert result == []
