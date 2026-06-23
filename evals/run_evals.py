"""
Evaluation runner for MediConciliador SNS.

Metrics reported:
  Pipeline (deterministic, no LLM required):
    - Discrepancy detection recall & precision vs gold_standard_discrepancies.json
    - Risk classification accuracy
    - Tool trajectory coverage

  Safety policy (PolicyServer unit tests):
    - Forbidden phrase detection rate
    - Required phrase check for HIGH-risk outputs
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.report_generation import run_full_analysis  # noqa: E402
from policy.policy_server import PolicyServer  # noqa: E402


# ── data loaders ──────────────────────────────────────────────────────────────

def _load(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _prep_case(case: dict) -> str:
    """Reformat synthetic_cases.json entry for run_full_analysis."""
    return json.dumps({
        "case_id": case["case_id"],
        "discharge_summary": case["discharge_summary"],
        "active_prescription": case["active_prescription"],
        "patient_interview": case["patient_interview"],
        "risk_factors": case.get("patient_profile", {}).get("risk_factors", []),
    }, ensure_ascii=False)


# ── discrepancy matching ──────────────────────────────────────────────────────

def _type_matches(gold_type: str, detected_type: str) -> bool:
    """Gold 'omission' matches detected 'omission_in_prescription', etc."""
    return gold_type in detected_type


def _med_matches(gold_med: str, detected_med: str) -> bool:
    """Primary medication name substring match (case-insensitive)."""
    primary = gold_med.lower().split(" / ")[0].split(" vs ")[0].strip()
    return primary in detected_med.lower()


def _find_match(gold_disc: dict, detected: list[dict]) -> dict | None:
    for d in detected:
        if _type_matches(gold_disc["type"], d["type"]) and _med_matches(gold_disc["medication"], d["medication"]):
            return d
    return None


# ── pipeline evaluation ───────────────────────────────────────────────────────

_REQUIRED_TRACE_TOOLS = {
    "extract_medications",
    "normalize_medication_list",
    "detect_discrepancies",
    "score_discrepancy_risk",
    "format_reconciliation_report",
}


def eval_pipeline(cases: list, gold: list) -> list[dict]:
    gold_by_id = {g["case_id"]: g for g in gold}
    results = []

    for case in cases:
        case_id = case["case_id"]
        gold_case = gold_by_id.get(case_id)
        if not gold_case:
            continue

        report = json.loads(run_full_analysis(_prep_case(case)))
        detected = report["discrepancies"]
        trace_tools = {entry["tool"] for entry in report.get("trace", [])}

        disc_results = []
        for gd in gold_case["expected_discrepancies"]:
            match = _find_match(gd, detected)
            matched = match is not None
            disc_results.append({
                "gold_medication": gd["medication"],
                "gold_type": gd["type"],
                "gold_risk": gd["risk_level"],
                "matched": matched,
                "detected_risk": match["risk_level"] if matched else None,
                "risk_correct": matched and match["risk_level"] == gd["risk_level"],
            })

        gold_matched = sum(1 for r in disc_results if r["matched"])
        false_positives = max(0, len(detected) - gold_matched)

        results.append({
            "case_id": case_id,
            "discrepancies": disc_results,
            "false_positives": false_positives,
            "trajectory_ok": _REQUIRED_TRACE_TOOLS.issubset(trace_tools),
        })

    return results


# ── safety policy evaluation ──────────────────────────────────────────────────

def eval_safety(eval_cases: list, policy: PolicyServer) -> list[dict]:
    results = []
    for tc in eval_cases:
        result = policy.check_patient_output(tc["text"], is_high_risk=tc["is_high_risk"])
        results.append({
            "test_id": tc["test_id"],
            "description": tc["description"],
            "expected_passed": tc["expected_passed"],
            "actual_passed": result.passed,
            "ok": tc["expected_passed"] == result.passed,
            "blocked_phrases": result.blocked_phrases,
            "missing_required": result.missing_required,
        })
    return results


# ── report printing ───────────────────────────────────────────────────────────

def _pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "N/A"


def print_report(pipeline: list[dict], safety: list[dict]) -> int:
    W = 62
    print()
    print("=" * W)
    print("  MediConciliador SNS — Evaluation Report")
    print("=" * W)

    # ── pipeline ──────────────────────────────────────────────────────────────
    print(f"\nPIPELINE EVALUATION ({len(pipeline)} cases, deterministic)")
    print("-" * W)

    total_gold = total_tp = total_fp = total_risk_ok = total_traj_ok = 0

    for r in pipeline:
        tps = sum(1 for d in r["discrepancies"] if d["matched"])
        gn = len(r["discrepancies"])
        risk_n = sum(1 for d in r["discrepancies"] if d["risk_correct"])
        traj = "✓" if r["trajectory_ok"] else "✗"

        total_gold += gn
        total_tp += tps
        total_fp += r["false_positives"]
        total_risk_ok += risk_n
        total_traj_ok += r["trajectory_ok"]

        print(f"\n  {r['case_id']}")
        for d in r["discrepancies"]:
            m = "✓" if d["matched"] else "✗"
            risk_str = (
                f"  risk {d['detected_risk']} {'✓' if d['risk_correct'] else '✗'}"
                if d["matched"] else ""
            )
            med = d["gold_medication"][:32]
            print(f"    {m} {med:<32s} [{d['gold_type']}]{risk_str}")
        if r["false_positives"]:
            print(f"    false positives: {r['false_positives']}")
        print(f"    trajectory: {traj}")

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 1.0

    print(f"\n  Discrepancy recall:      {total_tp}/{total_gold} ({_pct(total_tp, total_gold)})")
    print(f"  Discrepancy precision:   {_pct(round(precision * 100), 100)}  (FP={total_fp})")
    print(f"  Risk classification:     {total_risk_ok}/{total_tp} ({_pct(total_risk_ok, total_tp)})")
    print(f"  Trajectory coverage:     {total_traj_ok}/{len(pipeline)} ({_pct(total_traj_ok, len(pipeline))})")

    # ── safety ────────────────────────────────────────────────────────────────
    print(f"\nSAFETY POLICY EVALUATION ({len(safety)} tests)")
    print("-" * W)

    total_safety_ok = 0
    for r in safety:
        s = "✓" if r["ok"] else "✗"
        exp = "PASS" if r["expected_passed"] else "FAIL"
        act = "PASS" if r["actual_passed"] else "FAIL"
        print(f"  {s} {r['test_id'][:42]:<42s}  exp={exp}  act={act}")
        if not r["ok"]:
            if r["blocked_phrases"]:
                phrases = [p["phrase"] for p in r["blocked_phrases"]]
                print(f"      blocked: {phrases}")
            if r["missing_required"]:
                print(f"      missing required: {r['missing_required']}")
        total_safety_ok += r["ok"]

    print(f"\n  Safety tests passed:     {total_safety_ok}/{len(safety)} ({_pct(total_safety_ok, len(safety))})")

    # ── summary ───────────────────────────────────────────────────────────────
    all_pass = (
        total_tp == total_gold
        and total_fp == 0
        and total_risk_ok == total_tp
        and total_traj_ok == len(pipeline)
        and total_safety_ok == len(safety)
    )

    total_checks = total_gold + total_tp + len(pipeline) + len(safety)
    total_ok = total_tp + total_risk_ok + total_traj_ok + total_safety_ok

    print()
    print("=" * W)
    verdict = "PASS" if all_pass else "FAIL"
    print(f"  RESULT: {verdict} — {total_ok}/{total_checks} evaluations")
    print("=" * W)
    print()

    return 0 if all_pass else 1


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    data_dir = ROOT / "data"
    evals_dir = ROOT / "evals"
    policy_dir = ROOT / "policy"

    cases = _load(data_dir / "synthetic_cases.json")
    gold = _load(data_dir / "gold_standard_discrepancies.json")
    eval_cases = _load(evals_dir / "eval_cases.json")
    policy = PolicyServer(policy_dir)

    pipeline_results = eval_pipeline(cases, gold)
    safety_results = eval_safety(eval_cases, policy)

    return print_report(pipeline_results, safety_results)


if __name__ == "__main__":
    sys.exit(main())
