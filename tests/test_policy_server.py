"""
Tests for PolicyServer and run_policy_check.

Verifies that:
- Clean text passes without violations
- All forbidden phrases (ES + EN) are detected
- Matching is case-insensitive
- HIGH-risk outputs require all three professional-review phrases
- is_high_risk=False does not enforce required phrases
- Multiple violations are all reported
- run_policy_check tool returns valid JSON with the expected structure
"""

import json
from pathlib import Path

import pytest

from policy.policy_server import PolicyServer, PolicyCheckResult
from tools.policy_check import run_policy_check

POLICY_DIR = Path(__file__).parent.parent / "policy"

_REQUIRED_ES = [
    "requiere revisión profesional",
    "no cambie la medicación sin consultar",
    "lleve esta información a su profesional sanitario",
]

_CLEAN_HIGH_RISK = (
    "Hemos detectado algunas diferencias en su medicación que requiere revisión profesional. "
    "Por favor, no cambie la medicación sin consultar a su médico o farmacéutico. "
    "Lleve esta información a su profesional sanitario en su próxima visita."
)

_CLEAN_LOW_RISK = (
    "Se han identificado algunas discrepancias menores en su medicación. "
    "Su equipo sanitario le informará en la próxima consulta."
)


@pytest.fixture
def server() -> PolicyServer:
    return PolicyServer(policy_dir=POLICY_DIR)


# ---------------------------------------------------------------------------
# Basic pass / fail
# ---------------------------------------------------------------------------

def test_clean_text_passes(server: PolicyServer) -> None:
    result = server.check_patient_output(_CLEAN_LOW_RISK)
    assert result.passed is True
    assert result.blocked_phrases == []
    assert result.missing_required == []


def test_clean_high_risk_passes(server: PolicyServer) -> None:
    result = server.check_patient_output(_CLEAN_HIGH_RISK, is_high_risk=True)
    assert result.passed is True
    assert result.blocked_phrases == []
    assert result.missing_required == []


# ---------------------------------------------------------------------------
# Forbidden phrases — Spanish
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "deje de tomar",
    "suspenda",
    "empiece a tomar",
    "cambie la dosis",
    "no necesita consultar",
    "puede tomarlo sin problema",
    "es seguro continuar",
    "es peligroso continuar",
    "tome este medicamento",
    "no tome este medicamento",
])
def test_forbidden_es_detected(server: PolicyServer, phrase: str) -> None:
    text = f"Estimado paciente, {phrase} el tratamiento de forma inmediata."
    result = server.check_patient_output(text)
    assert result.passed is False
    found = [b["phrase"] for b in result.blocked_phrases]
    assert phrase in found


# ---------------------------------------------------------------------------
# Forbidden phrases — English
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "stop taking",
    "discontinue",
    "start taking",
    "change your dose",
    "you do not need to consult",
    "it is safe to continue",
    "it is dangerous to continue",
    "take this medication",
    "do not take this medication",
])
def test_forbidden_en_detected(server: PolicyServer, phrase: str) -> None:
    text = f"Dear patient, please {phrase} immediately."
    result = server.check_patient_output(text)
    assert result.passed is False
    found = [b["phrase"] for b in result.blocked_phrases]
    assert phrase in found


# ---------------------------------------------------------------------------
# Case insensitivity
# ---------------------------------------------------------------------------

def test_forbidden_phrase_uppercase(server: PolicyServer) -> None:
    result = server.check_patient_output("DEJE DE TOMAR el medicamento.")
    assert result.passed is False
    assert any(b["phrase"] == "deje de tomar" for b in result.blocked_phrases)


def test_forbidden_phrase_mixed_case(server: PolicyServer) -> None:
    result = server.check_patient_output("Por favor Suspenda el tratamiento.")
    assert result.passed is False
    assert any(b["phrase"] == "suspenda" for b in result.blocked_phrases)


# ---------------------------------------------------------------------------
# HIGH-risk required phrases
# ---------------------------------------------------------------------------

def test_high_risk_missing_all_required_fails(server: PolicyServer) -> None:
    result = server.check_patient_output(_CLEAN_LOW_RISK, is_high_risk=True)
    assert result.passed is False
    for req in _REQUIRED_ES:
        assert req in result.missing_required


def test_high_risk_missing_one_required_fails(server: PolicyServer) -> None:
    text = (
        "Hay discrepancias que requiere revisión profesional. "
        "No cambie la medicación sin consultar."
        # missing: "lleve esta información a su profesional sanitario"
    )
    result = server.check_patient_output(text, is_high_risk=True)
    assert result.passed is False
    assert "lleve esta información a su profesional sanitario" in result.missing_required


def test_not_high_risk_ignores_missing_required(server: PolicyServer) -> None:
    result = server.check_patient_output(_CLEAN_LOW_RISK, is_high_risk=False)
    assert result.passed is True
    assert result.missing_required == []


# ---------------------------------------------------------------------------
# Multiple violations
# ---------------------------------------------------------------------------

def test_multiple_forbidden_phrases_all_reported(server: PolicyServer) -> None:
    text = "deje de tomar el medicamento y empiece a tomar otro."
    result = server.check_patient_output(text)
    assert result.passed is False
    found = [b["phrase"] for b in result.blocked_phrases]
    assert "deje de tomar" in found
    assert "empiece a tomar" in found


def test_forbidden_and_missing_required_both_reported(server: PolicyServer) -> None:
    text = "deje de tomar el medicamento."
    result = server.check_patient_output(text, is_high_risk=True)
    assert result.passed is False
    assert len(result.blocked_phrases) > 0
    assert len(result.missing_required) > 0


# ---------------------------------------------------------------------------
# Blocked phrase metadata
# ---------------------------------------------------------------------------

def test_blocked_phrase_has_severity_and_reason(server: PolicyServer) -> None:
    result = server.check_patient_output("deje de tomar la pastilla.")
    assert result.passed is False
    entry = result.blocked_phrases[0]
    assert "phrase" in entry
    assert "severity" in entry
    assert "reason" in entry
    assert entry["severity"] in ("critical", "high")


# ---------------------------------------------------------------------------
# PolicyCheckResult type
# ---------------------------------------------------------------------------

def test_result_is_dataclass_instance(server: PolicyServer) -> None:
    result = server.check_patient_output(_CLEAN_LOW_RISK)
    assert isinstance(result, PolicyCheckResult)


# ---------------------------------------------------------------------------
# run_policy_check tool (JSON interface)
# ---------------------------------------------------------------------------

def test_tool_clean_returns_passed_true() -> None:
    output = run_policy_check(_CLEAN_LOW_RISK, is_high_risk=False)
    data = json.loads(output)
    assert data["passed"] is True
    assert data["blocked_phrases"] == []
    assert data["missing_required"] == []


def test_tool_forbidden_phrase_returns_passed_false() -> None:
    text = "Por favor, deje de tomar el ibuprofeno."
    output = run_policy_check(text, is_high_risk=False)
    data = json.loads(output)
    assert data["passed"] is False
    assert len(data["blocked_phrases"]) > 0


def test_tool_high_risk_complete_passes() -> None:
    output = run_policy_check(_CLEAN_HIGH_RISK, is_high_risk=True)
    data = json.loads(output)
    assert data["passed"] is True


def test_tool_output_is_valid_json() -> None:
    output = run_policy_check("Texto cualquiera.", is_high_risk=False)
    data = json.loads(output)
    assert isinstance(data, dict)
    assert "passed" in data
    assert "blocked_phrases" in data
    assert "missing_required" in data
