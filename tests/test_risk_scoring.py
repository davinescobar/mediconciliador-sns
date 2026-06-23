"""Tests for risk_scoring tool — validates rules-based risk assignment."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from tools.risk_scoring import score_discrepancy_risk


def _score(discrepancies: list[dict], discharge_meds: list[dict] | None = None, context: dict | None = None) -> list[dict]:
    return json.loads(
        score_discrepancy_risk(
            json.dumps(discrepancies),
            discharge_meds_json=json.dumps(discharge_meds or []),
            context_json=json.dumps(context or {}),
        )
    )


class TestNsaidAnticoagulantInteraction:
    def test_nsaid_discontinued_with_anticoagulant_in_discharge_is_high(self):
        discrepancies = [{
            "medication": "ibuprofen",
            "type": "discontinued_medication_still_taken",
            "description": "ibuprofen discontinued but still taken",
        }]
        discharge_meds = [{"name": "apixaban"}, {"name": "omeprazole"}]
        scored = _score(discrepancies, discharge_meds)
        assert scored[0]["risk_level"] == "HIGH"

    def test_nsaid_discontinued_without_anticoagulant_is_medium(self):
        discrepancies = [{
            "medication": "ibuprofen",
            "type": "discontinued_medication_still_taken",
            "description": "ibuprofen discontinued but still taken",
        }]
        discharge_meds = [{"name": "ramipril"}, {"name": "metformin"}]
        scored = _score(discrepancies, discharge_meds)
        assert scored[0]["risk_level"] == "MEDIUM"

    def test_anticoagulant_discontinued_still_taken_is_high(self):
        discrepancies = [{
            "medication": "warfarin",
            "type": "discontinued_medication_still_taken",
            "description": "warfarin still taken",
        }]
        scored = _score(discrepancies)
        assert scored[0]["risk_level"] == "HIGH"


class TestDiureticOmission:
    def test_furosemide_omission_in_heart_failure_is_high(self):
        discrepancies = [{
            "medication": "furosemide",
            "type": "omission_in_prescription",
            "description": "furosemide missing from prescription",
        }]
        context = {"risk_factors": ["heart_failure", "hypertension"]}
        scored = _score(discrepancies, context=context)
        assert scored[0]["risk_level"] == "HIGH"

    def test_furosemide_omission_without_heart_failure_is_medium(self):
        discrepancies = [{
            "medication": "furosemide",
            "type": "omission_in_prescription",
            "description": "furosemide missing from prescription",
        }]
        context = {"risk_factors": ["hypertension"]}
        scored = _score(discrepancies, context=context)
        assert scored[0]["risk_level"] == "MEDIUM"


class TestPossibleDuplication:
    def test_possible_duplication_is_low(self):
        discrepancies = [{
            "medication": "unidentified_ppi / omeprazole",
            "type": "possible_duplication",
            "description": "possible PPI duplication",
            "uncertainty": "high",
        }]
        scored = _score(discrepancies)
        assert scored[0]["risk_level"] == "LOW"


class TestUndocumentedMedication:
    def test_undocumented_medication_is_medium(self):
        discrepancies = [{
            "medication": "herbal_supplement",
            "type": "undocumented_patient_medication",
            "description": "not in any official record",
        }]
        scored = _score(discrepancies)
        assert scored[0]["risk_level"] == "MEDIUM"


class TestRationalePresent:
    @pytest.mark.parametrize("disc_type", [
        "discontinued_medication_still_taken",
        "omission_in_prescription",
        "possible_duplication",
        "undocumented_patient_medication",
    ])
    def test_rationale_always_set(self, disc_type):
        discrepancies = [{
            "medication": "ibuprofen",
            "type": disc_type,
            "description": "test",
        }]
        scored = _score(discrepancies)
        assert "rationale" in scored[0]
        assert scored[0]["rationale"] != ""
