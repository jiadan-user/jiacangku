from __future__ import annotations

import json
import os
import socket
import sys
import base64
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qa_agent.io import read_json, read_text, write_json

COMPLETED_STATUSES = {"completed", "COMPLETED", "已完成"}
DEFAULT_DASHBOARD_URL = "http://10.192.35.53:8001"


def _ok_ui_project_root(project_root: Path) -> Path:
    return (
        project_root
        / "bundled"
        / "skills"
        / "ok_autotest_ui_skill"
        / "bundled"
        / "ok_autotest_ui_pc"
    )


def _ok_ui_reports_root(project_root: Path) -> Path:
    return _ok_ui_project_root(project_root) / "reports" / "ok_test_runs"


def _dashboard_url(value: str | None = None) -> str:
    return value or os.getenv("QA_AGENT_DASHBOARD_URL", "") or DEFAULT_DASHBOARD_URL


def _read_json_path(path: str | Path | None) -> dict[str, Any]:
    if not path:
        return {}
    return read_json(str(path), default={}) or {}


def _read_text_path(path: str | Path | None) -> str:
    if not path:
        return ""
    return read_text(str(path))


def _artifact_path(state: dict[str, Any], *names: str) -> str:
    artifacts = state.get("artifacts", {}) or {}
    for name in names:
        value = artifacts.get(name)
        if value:
            return value
    return ""


def _find_ok_ui_artifacts(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    candidates: list[Path] = []
    for key in ("ok_ui_execution_report", "ok_ui_report", "release_recommendation"):
        value = _artifact_path(state, key)
        if value:
            path = Path(value)
            candidates.append(path if path.is_dir() else path.parent)
    for value in (state.get("artifacts", {}) or {}).values():
        if isinstance(value, str) and value:
            path = Path(value)
            if path.name in {"summary.json", "coverage_report.json", "decision_report.json"}:
                candidates.append(path.parent)

    for directory in candidates:
        summary = _read_json_path(directory / "summary.json")
        coverage = _read_json_path(directory / "coverage_report.json")
        decision = _read_json_path(directory / "decision_report.json")
        if summary or coverage or decision:
            return summary, coverage, decision
    reports_root = _ok_ui_reports_root(Path(__file__).resolve().parents[1])
    if reports_root.exists():
        summaries = sorted(reports_root.glob("*/summary.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        for summary_path in summaries[:3]:
            directory = summary_path.parent
            summary = _read_json_path(summary_path)
            coverage = _read_json_path(directory / "coverage_report.json")
            decision = _read_json_path(directory / "decision_report.json")
            if summary or coverage or decision:
                return summary, coverage, decision
    return {}, {}, {}


def _build_coverage_dashboard(project_root: Path) -> dict[str, Any]:
    tooling_root = (
        project_root
        / "bundled"
        / "skills"
        / "ok_autotest_ui_skill"
        / "bundled"
        / "ok_autotest_ui_pc"
    )
    if not tooling_root.exists():
        return {"source": "qa_agent_publish", "error": f"OK UI project not found: {tooling_root}"}
    sys.path.insert(0, str(tooling_root))
    try:
        from tooling.ok_test.text_coverage import build_text_case_dashboard

        return build_text_case_dashboard()
    except Exception as exc:
        return {"source": "qa_agent_publish", "error": str(exc)}
    finally:
        try:
            sys.path.remove(str(tooling_root))
        except ValueError:
            pass


def _allure_report_dir(summary: dict[str, Any]) -> Path | None:
    value = summary.get("allure_report") if isinstance(summary, dict) else ""
    if value:
        path = Path(str(value))
        if path.exists() and path.is_dir():
            return path
    return None


def _package_allure_report(report_dir: Path | None) -> dict[str, Any]:
    if not report_dir:
        return {}
    files: list[dict[str, str]] = []
    for path in sorted(report_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(report_dir).as_posix()
        if rel.startswith("history/"):
            continue
        data = path.read_bytes()
        files.append({"path": rel, "encoding": "base64", "content": base64.b64encode(data).decode("ascii")})
    return {"index_path": "index.html", "files": files}


def _latest_ok_ui_run_id(project_root: Path) -> str:
    latest_path = _ok_ui_project_root(project_root) / "reports" / "ok_test_latest_run.txt"
    if not latest_path.exists():
        raise FileNotFoundError(f"OK UI latest run marker not found: {latest_path}")
    run_id = latest_path.read_text(encoding="utf-8").strip()
    if not run_id:
        raise FileNotFoundError(f"OK UI latest run marker is empty: {latest_path}")
    return run_id


def _ok_ui_run_dir(project_root: Path, ok_ui_run_id: str) -> Path:
    run_dir = _ok_ui_reports_root(project_root) / ok_ui_run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"OK UI run not found: {run_dir}")
    return run_dir


def _ok_ui_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


def _ok_ui_status(summary: dict[str, Any]) -> str:
    if summary.get("dry_run"):
        return "DRY_RUN"
    return "COMPLETED"


def _ok_ui_modules(summary: dict[str, Any], module: str | None = None) -> list[str]:
    if module:
        return _normalize_list_for_publish(module)
    modules = summary.get("selected_modules")
    if isinstance(modules, list) and modules:
        return [str(item) for item in modules if str(item)]
    selection = summary.get("selection") or {}
    if isinstance(selection, dict):
        return _normalize_list_for_publish(selection.get("module"))
    return []


def _ok_ui_sites(summary: dict[str, Any], site: str | None = None) -> list[str]:
    if site:
        return _normalize_list_for_publish(site)
    selection = summary.get("selection") or {}
    if isinstance(selection, dict):
        return _normalize_list_for_publish(selection.get("site"))
    return []


def _normalize_list_for_publish(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str):
        return [item.strip() for item in value.replace("，", ",").replace("；", ";").replace("\n", ",").replace(";", ",").split(",") if item.strip()]
    return [str(value)]


def _sample_list_for_publish(value: Any, limit: int = 50) -> dict[str, Any]:
    if not isinstance(value, list):
        return {"total": 0, "items": []}
    return {"total": len(value), "items": value[:limit]}


def _compact_phase_report_for_publish(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    keep_keys = {
        "phase",
        "name",
        "pytest_exit_code",
        "junit_path",
        "output_path",
        "empty_marker_path",
        "pytest_target_count",
        "result_source",
        "result_warnings",
    }
    compact = {key: value[key] for key in keep_keys if key in value}
    case_results = value.get("case_results")
    if isinstance(case_results, list):
        compact["case_results_total"] = len(case_results)
    return compact


def _compact_ok_ui_summary_for_publish(summary: dict[str, Any]) -> dict[str, Any]:
    keep_keys = {
        "run_id",
        "dry_run",
        "selection",
        "selected_count",
        "selected_modules",
        "selected_features",
        "requested_workers",
        "resolved_workers",
        "parallel_enabled",
        "parallel_reason",
        "parallel_granularity",
        "pytest_command",
        "artifact_retention",
        "run_status",
        "block_reason",
        "pytest_exit_code",
        "execution_target_mode",
        "pytest_target_count",
        "prerequisite_attempted",
        "prerequisite_selected_count",
        "prerequisite_passed_count",
        "executed_cases",
        "passed_cases",
        "failed_cases",
        "skipped_cases",
        "allure_report",
        "allure_url",
        "lean_cleanup",
    }
    compact = {key: summary[key] for key in keep_keys if key in summary}
    for key in (
        "selected_nodeids",
        "selected_case_ids",
        "scope_case_nodeids",
        "recommended_case_nodeids",
        "baseline_case_nodeids",
        "prerequisite_selector_texts",
    ):
        if key in summary:
            compact[f"{key}_sample"] = _sample_list_for_publish(summary.get(key))
    case_results = summary.get("case_results")
    if isinstance(case_results, list):
        compact["case_results_total"] = len(case_results)
        compact["failed_case_results_sample"] = [
            item for item in case_results if isinstance(item, dict) and item.get("outcome") == "failed"
        ][:50]
        compact["skipped_case_results_sample"] = [
            item for item in case_results if isinstance(item, dict) and item.get("outcome") == "skipped"
        ][:20]
    phase_reports = summary.get("phase_reports")
    if isinstance(phase_reports, list):
        compact["phase_reports"] = [_compact_phase_report_for_publish(item) for item in phase_reports]
    return compact


def _standalone_ok_ui_report(ok_ui_run_id: str, summary: dict[str, Any], coverage: dict[str, Any], decision: dict[str, Any]) -> str:
    run_status = summary.get("run_status") or ("dry_run" if summary.get("dry_run") else "unknown")
    lines = [
        f"# OK UI 独立回归报告",
        "",
        f"- OK UI run_id：`{ok_ui_run_id}`",
        f"- 执行结果：{run_status}",
        f"- 选中用例：{summary.get('selected_count', 0)}",
        f"- 实际执行：{summary.get('executed_cases', 0)}",
        f"- 通过：{summary.get('passed_cases', 0)}",
        f"- 失败：{summary.get('failed_cases', 0)}",
        f"- 跳过：{summary.get('skipped_cases', 0)}",
        f"- 线程数：{summary.get('resolved_workers') or 1}",
    ]
    if coverage:
        lines.extend(
            [
                "",
                "## 覆盖摘要",
                f"- 推荐范围执行率：{coverage.get('requirement_execution_coverage', '')}",
                f"- 本次通过率：{coverage.get('requirement_pass_rate', '')}",
            ]
        )
    if decision:
        lines.extend(
            [
                "",
                "## 发布建议",
                f"- 风险等级：{decision.get('risk_level', '')}",
                f"- 建议：{decision.get('suggestion', '')}",
                f"- 原因：{decision.get('reason', '')}",
            ]
        )
    return "\n".join(lines) + "\n"


def _ok_ui_allure_report_dir(project_root: Path, ok_ui_run_id: str, summary: dict[str, Any]) -> Path | None:
    try:
        if _latest_ok_ui_run_id(project_root) != ok_ui_run_id:
            return None
    except FileNotFoundError:
        return None
    return _allure_report_dir(summary)


def build_ok_ui_publish_payload(
    project_root: Path,
    ok_ui_run_id: str,
    *,
    project_key: str | None = None,
    module: str | None = None,
    site: str | None = None,
    change_mode: str | None = None,
) -> dict[str, Any]:
    run_dir = _ok_ui_run_dir(project_root, ok_ui_run_id)
    summary_path = run_dir / "summary.json"
    summary = _read_json_path(summary_path)
    if not summary:
        raise FileNotFoundError(f"OK UI summary not found: {summary_path}")
    coverage = _read_json_path(run_dir / "coverage_report.json")
    decision = _read_json_path(run_dir / "decision_report.json")
    coverage_dashboard = _build_coverage_dashboard(project_root)
    timestamp = _ok_ui_timestamp(summary_path)
    run_state = {
        "run_id": ok_ui_run_id,
        "status": _ok_ui_status(summary),
        "change_mode": change_mode or "OK UI 独立回归",
        "current_phase": "ok_autotest_ui_skill",
        "created_at": timestamp,
        "updated_at": timestamp,
        "artifacts": {
            "ok_ui_execution_report": str(summary_path),
            "release_recommendation": str(run_dir / "decision_report.json"),
        },
        "phase_statuses": {"ok_autotest_ui_skill": "COMPLETED"},
        "phase_timings": {},
    }
    modules = _ok_ui_modules(summary, module)
    sites = _ok_ui_sites(summary, site)
    return {
        "run_id": ok_ui_run_id,
        "status": run_state["status"],
        "operator": os.getenv("QA_AGENT_OPERATOR") or os.getenv("USER") or "匿名用户",
        "host": socket.gethostname(),
        "project_root": str(project_root),
        "project_key": project_key or os.getenv("QA_AGENT_DASHBOARD_PROJECT_KEY", "OK"),
        "product": os.getenv("QA_AGENT_PRODUCT", ""),
        "change_mode": run_state["change_mode"],
        "module": modules,
        "site": sites,
        "trigger_source": "ok_ui_skill_cli",
        "branch": os.getenv("GIT_BRANCH", ""),
        "commit_sha": os.getenv("GIT_COMMIT", ""),
        "pipeline_id": os.getenv("CI_PIPELINE_ID", ""),
        "build_url": os.getenv("CI_BUILD_URL", ""),
        "started_at": timestamp,
        "finished_at": timestamp,
        "artifacts": {
            "run_state": run_state,
            "final_report": _standalone_ok_ui_report(ok_ui_run_id, summary, coverage, decision),
            "summary": _compact_ok_ui_summary_for_publish(summary),
            "coverage": coverage,
            "coverage_dashboard": coverage_dashboard,
            "decision": decision,
            "phase3_gate": {},
            "allure_report": _package_allure_report(_ok_ui_allure_report_dir(project_root, ok_ui_run_id, summary)),
        },
    }


def build_publish_payload(project_root: Path, run_id: str) -> dict[str, Any]:
    run_dir = project_root / ".qa_agent" / "runs" / run_id
    state_path = run_dir / "run_state.json"
    state = _read_json_path(state_path)
    if not state:
        raise FileNotFoundError(f"run_state.json not found: {state_path}")
    requirement = _read_json_path(_artifact_path(state, "requirement_packet"))
    final_report = _read_text_path(_artifact_path(state, "final_report"))
    summary, coverage, decision = _find_ok_ui_artifacts(state)
    coverage_dashboard = _build_coverage_dashboard(project_root)
    allure_report = _package_allure_report(_allure_report_dir(summary))

    modules = requirement.get("requested_modules") or requirement.get("candidate_modules") or requirement.get("module") or []
    sites = requirement.get("requested_sites") or requirement.get("site") or []
    return {
        "run_id": run_id,
        "status": state.get("status") or "completed",
        "operator": os.getenv("QA_AGENT_OPERATOR") or os.getenv("USER") or "匿名用户",
        "host": socket.gethostname(),
        "project_root": str(project_root),
        "project_key": os.getenv("QA_AGENT_DASHBOARD_PROJECT_KEY", "OK"),
        "product": os.getenv("QA_AGENT_PRODUCT", ""),
        "change_mode": state.get("change_mode") or requirement.get("change_mode") or "",
        "module": modules,
        "site": sites,
        "trigger_source": os.getenv("QA_AGENT_TRIGGER_SOURCE", "local_cli"),
        "branch": os.getenv("GIT_BRANCH", ""),
        "commit_sha": os.getenv("GIT_COMMIT", ""),
        "pipeline_id": os.getenv("CI_PIPELINE_ID", ""),
        "build_url": os.getenv("CI_BUILD_URL", ""),
        "started_at": state.get("created_at"),
        "finished_at": state.get("updated_at"),
        "artifacts": {
            "run_state": state,
            "final_report": final_report,
            "summary": summary,
            "coverage": coverage,
            "coverage_dashboard": coverage_dashboard,
            "decision": decision,
            "phase3_gate": _read_json_path(_artifact_path(state, "phase3_gate_result")),
            "allure_report": allure_report,
        },
    }


def publish_payload(base_url: str, payload: dict[str, Any], api_key: str = "", timeout: int = 30) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/api/qa-agent/runs/publish"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {"success": True}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"success": False, "status_code": exc.code, "error": detail}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def publish_coverage(project_root: Path, *, base_url: str | None = None, api_key: str | None = None, project_key: str | None = None) -> dict[str, Any]:
    base_url = _dashboard_url(base_url)
    if not base_url:
        return {"success": False, "skipped": True, "reason": "dashboard url unavailable"}
    payload = {
        "project_key": project_key or os.getenv("QA_AGENT_DASHBOARD_PROJECT_KEY", "OK"),
        "product": os.getenv("QA_AGENT_PRODUCT", ""),
        "operator": os.getenv("QA_AGENT_OPERATOR") or os.getenv("USER") or "匿名用户",
        "host": socket.gethostname(),
        "project_root": str(project_root),
        "coverage": _build_coverage_dashboard(project_root),
    }
    url = base_url.rstrip("/") + "/api/qa-agent/coverage/publish"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    key = api_key or os.getenv("QA_AGENT_DASHBOARD_API_KEY", "")
    if key:
        headers["X-API-Key"] = key
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {"success": True}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"success": False, "status_code": exc.code, "error": detail}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def publish_run(
    project_root: Path,
    run_id: str,
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    allow_incomplete: bool = False,
) -> dict[str, Any]:
    base_url = _dashboard_url(base_url)
    run_dir = project_root / ".qa_agent" / "runs" / run_id
    result_path = run_dir / "dashboard_publish_result.json"
    if not base_url:
        result = {"success": False, "skipped": True, "reason": "dashboard url unavailable"}
        write_json(result_path, result)
        return result
    payload = build_publish_payload(project_root, run_id)
    status = str(payload.get("status") or "")
    if not allow_incomplete and status not in COMPLETED_STATUSES:
        result = {
            "success": False,
            "skipped": True,
            "reason": f"run is not completed: {status or 'unknown'}",
        }
        write_json(result_path, result)
        return result
    result = publish_payload(base_url, payload, api_key or os.getenv("QA_AGENT_DASHBOARD_API_KEY", ""))
    write_json(result_path, result)
    return result


def publish_ok_ui_run(
    project_root: Path,
    ok_ui_run_id: str | None = None,
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    project_key: str | None = None,
    module: str | None = None,
    site: str | None = None,
    change_mode: str | None = None,
) -> dict[str, Any]:
    base_url = _dashboard_url(base_url)
    run_id = ok_ui_run_id or _latest_ok_ui_run_id(project_root)
    run_dir = _ok_ui_run_dir(project_root, run_id)
    result_path = run_dir / "dashboard_publish_result.json"
    if not base_url:
        result = {"success": False, "skipped": True, "reason": "dashboard url unavailable"}
        write_json(result_path, result)
        return result
    payload = build_ok_ui_publish_payload(
        project_root,
        run_id,
        project_key=project_key,
        module=module,
        site=site,
        change_mode=change_mode,
    )
    result = publish_payload(base_url, payload, api_key or os.getenv("QA_AGENT_DASHBOARD_API_KEY", ""))
    write_json(result_path, result)
    return result
