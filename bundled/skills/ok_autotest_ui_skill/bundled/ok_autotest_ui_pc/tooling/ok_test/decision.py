from __future__ import annotations

import argparse

from .common import REPORTS_DIR, load_json, save_json
from .coverage import compute_coverage


def evaluate_decision(run_payload: dict) -> dict:
    if run_payload.get("dry_run"):
        return {
            "risk_level": "中风险",
            "suggestion": "建议先实际执行后再判断",
            "reason": "当前 run_id 来自 dry-run，没有真实结果。",
        }

    if run_payload.get("run_status") == "blocked":
        return {
            "risk_level": "中风险",
            "suggestion": "先补前置再执行",
            "reason": run_payload.get("block_reason") or "已尝试自动补跑前置，但目标场景仍未真正执行。",
        }

    coverage_result = compute_coverage(run_payload)
    case_results = coverage_result["case_results"]
    baseline_failed = coverage_result["baseline_failed_cases"]
    missing_baseline = coverage_result["missing_baseline_cases"]
    execution_coverage = coverage_result["requirement_execution_coverage"]
    governance_coverage = coverage_result["governance_coverage"]
    ungoverned_cases = coverage_result["ungoverned_cases"]
    important_failures = [
        item for item in case_results
        if item["failed"] and item["priority"] in {"p0", "p1"} and not item["is_baseline"]
    ]

    if baseline_failed or governance_coverage < 0.9 or ungoverned_cases:
        return {
            "risk_level": "高风险",
            "suggestion": "建议暂停上线并处理问题",
            "reason": "存在基线失败、治理覆盖率不足或未完成治理映射的用例。",
            "details": baseline_failed or ungoverned_cases,
        }
    if missing_baseline:
        return {
            "risk_level": "中风险",
            "suggestion": "建议提测",
            "reason": "基线场景未跑齐。",
            "details": missing_baseline,
        }
    if execution_coverage < 0.8 or important_failures:
        return {
            "risk_level": "中风险",
            "suggestion": "建议提测",
            "reason": "推荐场景覆盖率不足 80% 或存在非基线 P0/P1 失败。",
        }
    if coverage_result["requirement_pass_rate"] < 1.0:
        return {
            "risk_level": "中风险",
            "suggestion": "建议人工判断或补跑",
            "reason": "推荐场景存在未全部通过的情况。",
        }
    return {
        "risk_level": "低风险",
        "suggestion": "建议可上线",
        "reason": "治理覆盖率达标，基线跑齐，推荐场景覆盖达到阈值且全部通过。",
    }


def handle_decide(args: argparse.Namespace) -> int:
    run_dir = REPORTS_DIR / args.run_id
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"run summary not found: {summary_path}")
    run_payload = load_json(summary_path)
    result = evaluate_decision(run_payload)
    save_json(run_dir / "decision_report.json", result)
    print(f"risk_level={result['risk_level']}")
    print(f"suggestion={result['suggestion']}")
    print(f"reason={result['reason']}")
    return 0
