"""
Tests for tools/drug_interactions.py.
All tests use the static fallback — no network calls.
"""

import pytest
from unittest.mock import patch

from tools.drug_interactions import (
    check_drug_interactions,
    _static_interactions,
)


def test_empty_list_returns_no_interactions():
    result = check_drug_interactions([])
    assert result["interactions"] == []


def test_single_drug_returns_no_interactions():
    result = check_drug_interactions(["warfarin"])
    assert result["interactions"] == []


def test_return_type_is_dict_with_expected_keys():
    result = check_drug_interactions(["warfarin", "ibuprofen"])
    assert isinstance(result, dict)
    assert "source" in result
    assert "interactions" in result
    assert isinstance(result["interactions"], list)


def test_static_fallback_detects_known_interaction():
    # warfarin (anticoagulant) + ibuprofen (NSAID) — known high-risk pair
    interactions = _static_interactions(["warfarin", "ibuprofen"])
    assert len(interactions) >= 1
    pairs = {(i["drug1"], i["drug2"]) for i in interactions} | {
        (i["drug2"], i["drug1"]) for i in interactions
    }
    assert ("warfarin", "ibuprofen") in pairs or ("ibuprofen", "warfarin") in pairs


def test_static_fallback_interaction_has_required_fields():
    interactions = _static_interactions(["warfarin", "ibuprofen"])
    for item in interactions:
        assert "drug1" in item
        assert "drug2" in item
        assert "severity" in item
        assert "description" in item


def test_check_falls_back_to_static_on_network_error():
    with patch("tools.drug_interactions.get_rxcui", side_effect=Exception("network down")):
        result = check_drug_interactions(["warfarin", "ibuprofen"])
    assert result["source"] == "static"
    assert isinstance(result["interactions"], list)


def test_no_duplicate_pairs_in_static():
    interactions = _static_interactions(["warfarin", "ibuprofen", "apixaban"])
    pairs = [tuple(sorted([i["drug1"], i["drug2"]])) for i in interactions]
    assert len(pairs) == len(set(pairs))


def test_nlm_source_when_rxcui_found():
    with (
        patch("tools.drug_interactions.get_rxcui", side_effect=["12345", "67890"]),
        patch("tools.drug_interactions._fetch_nlm_interactions", return_value=[
            {"drug1": "warfarin", "drug2": "ibuprofen", "severity": "high", "description": "Bleeding risk"}
        ]),
    ):
        result = check_drug_interactions(["warfarin", "ibuprofen"])
    assert result["source"] == "nlm"
    assert len(result["interactions"]) == 1
