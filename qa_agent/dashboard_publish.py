from __future__ import annotations

import json
import os
import socket
import sys
import base64
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from qa_agent.io import read_json, read_text, write_json

COMPLETED_STATUSES = {"completed", "COMPLETED", "已完成"}
DEFAULT_DASHBOARD_URL = "http://10.192.35.53:8001"


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
    reports_root = (
        Path(__file__).resolve().parents[1]
        / "bundled"
        / "skills"
        / "ok_autotest_ui_skill"
        / "bundled"
        / "ok_autotest_ui_pc"
        / "reports"
        / "ok_test_runs"
    )
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
