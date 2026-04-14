from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .catalog import load_catalog
from .common import REPORTS_DIR, load_json, save_json
from .governance import case_is_governed, feature_breakdown_template, is_baseline_case, scope_cases
from .models import GovernanceCaseResult, SelectionCriteria
from .text_coverage import DEFAULT_KNOWLEDGE_BASE, write_text_case_dashboard


def _case_outcome_map(run_payload: dict[str, Any]) -> dict[str, str]:
    outcome_map: dict[str, str] = {}
    for item in run_payload.get("case_results", []):
        outcome_map[item["nodeid"]] = item.get("outcome", "selected")
    return outcome_map


def compute_coverage(run_payload: dict[str, Any], module_filter: str | None = None) -> dict[str, Any]:
    catalog = load_catalog()
    dry_run = bool(run_payload.get("dry_run"))
    selection = SelectionCriteria(**run_payload.get("selection", {}))
    selected_nodeids = set(run_payload.get("selected_nodeids", []))
    scoped_cases = scope_cases(catalog, selection, module_filter=module_filter, selected_nodeids=selected_nodeids)
    recommended_ids = set(run_payload.get("recommended_case_nodeids", []))
    baseline_ids = set(run_payload.get("baseline_case_nodeids", []))
    outcome_map = _case_outcome_map(run_payload)
    case_results: list[GovernanceCaseResult] = []
    feature_breakdown = feature_breakdown_template()

    for case in scoped_cases:
        outcome = outcome_map.get(case.nodeid, "not_run")
        executed = not dry_run and outcome in {"passed", "failed", "error", "xfailed", "xpassed"}
        failed = outcome_map.get(case.nodeid) in {"failed", "error"}
        passed = executed and not failed and outcome in {"passed", "xpassed"}
        recommended = case.nodeid in recommended_ids
        baseline = case.nodeid in baseline_ids or is_baseline_case(case)
        result = GovernanceCaseResult(
            nodeid=case.nodeid,
            module_id=case.module_id or "unmapped",
            feature_id=case.feature_id or "unmapped",
            case_id=case.case_id,
            name=case.allure_title or case.test_name,
            priority=case.priority,
            governed=case_is_governed(case),
            is_baseline=baseline,
            executed=executed,
            passed=passed,
            failed=failed,
            recommended=recommended,
        )
        case_results.append(result)
        bucket = feature_breakdown[result.feature_id]
        bucket["total"] += 1
        bucket["governed"] += int(result.governed)
        bucket["baseline"] += int(result.is_baseline)
        bucket["recommended"] += int(result.recommended)
        bucket["executed"] += int(result.executed)
        bucket["passed"] += int(result.passed)

    total = len(case_results)
    governed = sum(1 for item in case_results if item.governed)
    baseline_total = sum(1 for item in case_results if item.is_baseline)
    baseline_executed = sum(1 for item in case_results if item.is_baseline and item.executed)
    recommended = [item for item in case_results if item.recommended]
    executed = [item for item in recommended if item.executed]
    passed = [item for item in executed if item.passed]
    missing_baseline = [item.to_dict() for item in case_results if item.is_baseline and not item.executed]
    baseline_failed = [item.to_dict() for item in case_results if item.is_baseline and item.failed]
    ungoverned_cases = [item.to_dict() for item in case_results if not item.governed]

    return {
        "run_id": run_payload.get("run_id"),
        "run_status": run_payload.get("run_status"),
        "block_reason": run_payload.get("block_reason"),
        "module_filter": module_filter,
        "governance_coverage": governed / total if total else 0.0,
        "baseline_execution_coverage": baseline_executed / baseline_total if baseline_total else 0.0,
        "requirement_execution_coverage": len(executed) / len(recommended) if recommended else 0.0,
        "requirement_pass_rate": len(passed) / len(executed) if executed else 0.0,
        "executed_cases": len(executed),
        "passed_cases": len(passed),
        "failed_cases": sum(1 for item in case_results if item.failed),
        "skipped_cases": sum(1 for item in case_results if not item.executed and outcome_map.get(item.nodeid) == "skipped"),
        "feature_breakdown": feature_breakdown,
        "missing_baseline_cases": missing_baseline,
        "baseline_failed_cases": baseline_failed,
        "ungoverned_cases": ungoverned_cases,
        "case_results": [item.to_dict() for item in case_results],
    }


def _resolve_run_payload(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    run_dir = REPORTS_DIR / args.run_id
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"run summary not found: {summary_path}")
    return run_dir, load_json(summary_path)


def handle_coverage(args: argparse.Namespace) -> int:
    handled = False

    if args.run_id:
        run_dir, run_payload = _resolve_run_payload(args)
        result = compute_coverage(run_payload, module_filter=args.module)
        save_json(run_dir / "coverage_report.json", result)
        print(f"run_id={result['run_id']}")
        print(f"当前范围内已纳入治理的自动化脚本占比={result['governance_coverage']:.2%}")
        print(f"基线用例执行率={result['baseline_execution_coverage']:.2%}")
        print(f"推荐用例执行率={result['requirement_execution_coverage']:.2%}")
        print(f"本次通过率={result['requirement_pass_rate']:.2%}")
        if result["missing_baseline_cases"]:
            print("未执行的基线用例:")
            for case in result["missing_baseline_cases"]:
                print(f"- {case['nodeid']} | {case['name']}")
        handled = True

    if args.dashboard:
        knowledge_base = Path(args.knowledge_base_path) if args.knowledge_base_path else DEFAULT_KNOWLEDGE_BASE
        dashboard_output = Path(args.dashboard_output) if args.dashboard_output else None
        dashboard = write_text_case_dashboard(dashboard_output, knowledge_base)
        print(f"文本用例总数={dashboard['total_cases']}")
        print(f"已自动化={dashboard['automated_cases']}")
        print(f"未自动化={dashboard['non_automated_cases']}")
        print(f"自动化率={dashboard['automation_rate']:.2%}")
        print(f"dashboard_output={dashboard['dashboard_output']}")
        handled = True

    if not handled:
        raise ValueError("coverage 命令至少需要提供 --run-id 或 --dashboard")
    return 0
