from __future__ import annotations

import argparse
import io
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

import pytest

from .common import (
    ALLURE_SERVER_INFO_PATH,
    PREREQUISITES_PATH,
    REPORTS_DIR,
    ROOT_DIR,
    ROOT_REPORTS_DIR,
    create_run_id,
    ensure_dir,
    load_json,
    load_yaml,
    resolve_pytest_command,
    save_json,
    shell_join,
)
from .catalog import load_catalog
from .coverage import compute_coverage
from .decision import evaluate_decision
from .governance import matches_case, recommend_cases
from .models import CatalogCase, SelectionCriteria
from .selector import build_criteria, select_cases

EXECUTED_OUTCOMES = {"passed", "failed", "error", "xfailed", "xpassed"}
PASSED_OUTCOMES = {"passed", "xpassed"}
FAILED_OUTCOMES = {"failed", "error"}
ALLURE_REPORT_DIR = ROOT_REPORTS_DIR / "allure-report"
ALLURE_RESULTS_DIR = ROOT_REPORTS_DIR / "allure-results"
ALLURE_HOST = "127.0.0.1"


def _report_reason(report: pytest.TestReport) -> str | None:
    text = (getattr(report, "longreprtext", "") or "").strip()
    if not text:
        return None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else text


class _RunPlugin:
    def __init__(self) -> None:
        self.case_results: dict[str, dict[str, Any]] = {}

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when != "call":
            if report.skipped and report.nodeid not in self.case_results:
                self.case_results[report.nodeid] = {
                    "nodeid": report.nodeid,
                    "outcome": "skipped",
                    "duration": report.duration,
                    "reason": _report_reason(report),
                }
            if report.failed and report.nodeid not in self.case_results:
                self.case_results[report.nodeid] = {
                    "nodeid": report.nodeid,
                    "outcome": report.outcome,
                    "duration": report.duration,
                    "reason": _report_reason(report),
                }
            return
        self.case_results[report.nodeid] = {
            "nodeid": report.nodeid,
            "outcome": report.outcome,
            "duration": report.duration,
            "reason": _report_reason(report),
        }


def _default_case_result(nodeid: str) -> dict[str, Any]:
    return {
        "nodeid": nodeid,
        "outcome": "not_run",
        "duration": 0.0,
        "reason": None,
    }


def _build_summary(run_id: str, args: argparse.Namespace, selected_cases: list[CatalogCase], case_results: list[dict[str, Any]], dry_run: bool) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "dry_run": dry_run,
        "selection": build_criteria(args).to_dict(),
        "selected_count": len(selected_cases),
        "selected_nodeids": [case.nodeid for case in selected_cases],
        "selected_case_ids": [case.case_id for case in selected_cases if case.case_id],
        "selected_modules": sorted({case.module_id for case in selected_cases if case.module_id}),
        "selected_features": sorted({case.feature_id for case in selected_cases if case.feature_id}),
        "requested_workers": _requested_workers(args),
        "resolved_workers": 1,
        "parallel_enabled": False,
        "parallel_reason": "not resolved yet",
        "pytest_command": "",
        "artifact_retention": _artifact_retention(args),
        "lean_cleanup": {"enabled": False, "deleted": [], "reason": ""},
        "case_results": case_results,
        "recommended_case_nodeids": [],
        "baseline_case_nodeids": [],
        "run_status": "dry_run" if dry_run else "pending",
        "block_reason": None,
        "prerequisite_attempted": False,
        "prerequisite_selected_count": 0,
        "prerequisite_passed_count": 0,
        "executed_cases": 0,
        "passed_cases": 0,
        "failed_cases": 0,
        "skipped_cases": 0,
        "phase_reports": [],
        "prerequisite_selector_texts": [],
    }


def _sync_latest_report_assets(run_id: str, junit_path: Path, allure_dir: Path) -> None:
    latest_allure_dir = ALLURE_RESULTS_DIR
    latest_junit_path = ROOT_REPORTS_DIR / "junit.xml"
    ensure_dir(ROOT_REPORTS_DIR)
    if latest_allure_dir.exists():
        shutil.rmtree(latest_allure_dir)
    shutil.copytree(allure_dir, latest_allure_dir)
    shutil.copy2(junit_path, latest_junit_path)
    (ROOT_REPORTS_DIR / "ok_test_latest_run.txt").write_text(run_id + "\n", encoding="utf-8")


def _ensure_allure_cli() -> tuple[str | None, str]:
    allure_bin = shutil.which("allure")
    if allure_bin:
        return allure_bin, "Allure CLI 已就绪。"

    if sys.platform == "darwin":
        brew_bin = shutil.which("brew")
        if brew_bin:
            result = subprocess.run([brew_bin, "install", "allure"], capture_output=True, text=True)
            allure_bin = shutil.which("allure")
            if result.returncode == 0 and allure_bin:
                return allure_bin, "未检测到 Allure CLI，已自动安装并完成静态报告生成。"
            tail = (result.stderr or result.stdout).strip().splitlines()
            reason = tail[-1] if tail else "brew install allure 执行失败"
            return None, f"未检测到 Allure CLI，已尝试自动安装但失败：{reason}"

    return None, "未检测到 Allure CLI，当前环境无法自动安装，请先安装后再查看静态报告。"


def _load_allure_server_info() -> dict[str, Any]:
    if not ALLURE_SERVER_INFO_PATH.exists():
        return {}
    try:
        return load_json(ALLURE_SERVER_INFO_PATH)
    except Exception:
        return {}


def _save_allure_server_info(payload: dict[str, Any]) -> None:
    ensure_dir(ALLURE_SERVER_INFO_PATH.parent)
    save_json(ALLURE_SERVER_INFO_PATH, payload)


def _process_is_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _stop_allure_server(info: dict[str, Any]) -> None:
    pid = info.get("pid")
    if not isinstance(pid, int):
        return
    if not _process_is_alive(pid):
        return
    try:
        os.kill(pid, 15)
    except OSError:
        return
    for _ in range(20):
        if not _process_is_alive(pid):
            return
        time.sleep(0.1)
    try:
        os.kill(pid, 9)
    except OSError:
        return


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ALLURE_HOST, 0))
        return int(sock.getsockname()[1])


def _url_available(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1.0) as response:
            return 200 <= response.status < 400
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def _start_allure_server(report_dir: Path) -> dict[str, Any]:
    index_path = report_dir / "index.html"
    if not index_path.exists():
        return {
            "started": False,
            "url": None,
            "message": "未找到 Allure 静态报告首页，无法启动本地报告服务。",
        }

    existing = _load_allure_server_info()
    existing_report_dir = existing.get("report_dir")
    existing_url = existing.get("url")
    if (
        existing_report_dir == str(report_dir)
        and _process_is_alive(existing.get("pid"))
        and isinstance(existing_url, str)
        and _url_available(existing_url)
    ):
        return {
            "started": True,
            "url": existing_url,
            "message": "复用现有 Allure 报告服务。",
        }

    if existing:
        _stop_allure_server(existing)

    port = _find_free_port()
    command = [sys.executable, "-m", "http.server", str(port), "--bind", ALLURE_HOST]
    process = subprocess.Popen(
        command,
        cwd=report_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    url = f"http://{ALLURE_HOST}:{port}/index.html"
    for _ in range(20):
        if _url_available(url):
            break
        time.sleep(0.1)

    payload = {
        "pid": process.pid,
        "port": port,
        "url": url,
        "report_dir": str(report_dir),
    }
    _save_allure_server_info(payload)
    return {
        "started": _url_available(url),
        "url": url,
        "message": "Allure 本地报告服务已启动。" if _url_available(url) else "Allure 本地报告服务已启动，但暂未确认链接可访问。",
    }


def _generate_allure_report() -> dict[str, Any]:
    allure_bin, ensure_message = _ensure_allure_cli()
    if not allure_bin:
        return {
            "available": False,
            "generated": False,
            "message": ensure_message,
            "report_dir": str(ALLURE_REPORT_DIR),
            "url": None,
        }

    command = [allure_bin, "generate", str(ALLURE_RESULTS_DIR), "-o", str(ALLURE_REPORT_DIR), "--clean"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        tail = (result.stderr or result.stdout).strip().splitlines()
        reason = tail[-1] if tail else "Allure generate 执行失败"
        return {
            "available": True,
            "generated": False,
            "message": f"{ensure_message} Allure CLI 已找到，但静态报告生成失败：{reason}",
            "report_dir": str(ALLURE_REPORT_DIR),
            "url": None,
        }

    server_result = _start_allure_server(ALLURE_REPORT_DIR)
    return {
        "available": True,
        "generated": True,
        "message": f"{ensure_message} {server_result['message']}".strip(),
        "report_dir": str(ALLURE_REPORT_DIR),
        "url": server_result.get("url"),
    }


def _print_selected_cases(selected_cases: list[CatalogCase]) -> None:
    for case in selected_cases:
        title = case.allure_title or case.test_name
        print(f"- {case.nodeid} | {case.case_id or '-'} | {title}")


def _phase_junit_path(run_dir: Path, phase_name: str) -> Path:
    return run_dir / f"junit_{phase_name}.xml"


def _phase_output_path(run_dir: Path, phase_name: str) -> Path:
    return run_dir / f"pytest_output_{phase_name}.txt"


def _build_pytest_args(nodeids: list[str], junit_path: Path, allure_dir: Path, workers: int = 1) -> list[str]:
    args = nodeids + [
        "-p",
        "no:rerunfailures",
        "-o",
        "addopts=",
        "--junitxml",
        str(junit_path),
        "--alluredir",
        str(allure_dir),
    ]
    if workers > 1:
        args.extend(["-n", str(workers), "--dist", "loadscope"])
    return args


def _cgroup_cpu_limit() -> int | None:
    cpu_max = Path("/sys/fs/cgroup/cpu.max")
    try:
        if cpu_max.exists():
            quota_text, period_text = cpu_max.read_text(encoding="utf-8").strip().split()[:2]
            if quota_text != "max":
                quota = int(quota_text)
                period = int(period_text)
                if quota > 0 and period > 0:
                    return max(1, quota // period)
    except (OSError, ValueError):
        pass

    quota_path = Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    period_path = Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
    try:
        if quota_path.exists() and period_path.exists():
            quota = int(quota_path.read_text(encoding="utf-8").strip())
            period = int(period_path.read_text(encoding="utf-8").strip())
            if quota > 0 and period > 0:
                return max(1, quota // period)
    except (OSError, ValueError):
        pass
    return None


def _requested_workers(args: argparse.Namespace) -> str:
    return str(getattr(args, "workers", None) or os.getenv("OK_TEST_WORKERS") or "1").strip().lower()


def _max_workers(args: argparse.Namespace) -> int:
    raw = getattr(args, "max_workers", None) or os.getenv("OK_TEST_MAX_WORKERS") or "4"
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = 4
    return max(1, value)


def _artifact_retention(args: argparse.Namespace) -> str:
    value = str(getattr(args, "artifact_retention", None) or os.getenv("OK_TEST_ARTIFACT_RETENTION") or "lean")
    return "full" if value.strip().lower() == "full" else "lean"


def _resolve_workers(args: argparse.Namespace, selected_count: int, has_prerequisites: bool) -> dict[str, Any]:
    requested = _requested_workers(args)
    max_workers = _max_workers(args)
    if has_prerequisites:
        return {
            "requested_workers": requested,
            "resolved_workers": 1,
            "parallel_enabled": False,
            "parallel_reason": "selected cases have prerequisite mapping; forced serial to preserve login/data state",
            "max_workers": max_workers,
        }
    if requested in {"", "1", "none", "false", "off"}:
        return {
            "requested_workers": requested or "1",
            "resolved_workers": 1,
            "parallel_enabled": False,
            "parallel_reason": "serial execution requested",
            "max_workers": max_workers,
        }
    if selected_count <= 1:
        return {
            "requested_workers": requested,
            "resolved_workers": 1,
            "parallel_enabled": False,
            "parallel_reason": "only one selected case",
            "max_workers": max_workers,
        }
    if requested == "auto":
        cpu_count = os.cpu_count() or 1
        cgroup_limit = _cgroup_cpu_limit()
        if cgroup_limit:
            cpu_count = min(cpu_count, cgroup_limit)
        workers = max(1, min(cpu_count, selected_count, max_workers))
        return {
            "requested_workers": requested,
            "resolved_workers": workers,
            "parallel_enabled": workers > 1,
            "parallel_reason": f"auto resolved with cpu={cpu_count}, selected={selected_count}, max={max_workers}",
            "max_workers": max_workers,
        }
    try:
        requested_count = int(requested)
    except ValueError as exc:
        raise ValueError("--workers 只支持 1、正整数或 auto") from exc
    if requested_count < 1:
        raise ValueError("--workers 必须大于等于 1")
    workers = max(1, min(requested_count, selected_count, max_workers))
    return {
        "requested_workers": requested,
        "resolved_workers": workers,
        "parallel_enabled": workers > 1,
        "parallel_reason": (
            f"explicit workers={requested_count}; capped by selected={selected_count}, max={max_workers}"
            if workers != requested_count
            else f"explicit workers={workers}"
        ),
        "max_workers": max_workers,
    }


def _collect_phase_results(cases: list[CatalogCase], plugin: _RunPlugin) -> list[dict[str, Any]]:
    return [plugin.case_results.get(case.nodeid, _default_case_result(case.nodeid)) for case in cases]


def _junit_reason(testcase: ET.Element) -> str | None:
    for tag in ("failure", "error", "skipped"):
        child = testcase.find(tag)
        if child is not None:
            message = (child.attrib.get("message") or child.text or "").strip()
            return message or tag
    return None


def _junit_outcome(testcase: ET.Element) -> str:
    if testcase.find("error") is not None:
        return "error"
    if testcase.find("failure") is not None:
        return "failed"
    if testcase.find("skipped") is not None:
        return "skipped"
    return "passed"


def _junit_duration(testcase: ET.Element) -> float:
    try:
        return float(testcase.attrib.get("time", "0") or 0)
    except ValueError:
        return 0.0


def _nodeid_suffix(nodeid: str) -> str:
    parts = nodeid.split("::")
    return "::".join(parts[1:]) if len(parts) > 1 else nodeid


def _junit_candidate_nodeids(testcase: ET.Element) -> list[str]:
    classname = testcase.attrib.get("classname", "")
    name = testcase.attrib.get("name", "")
    file_attr = testcase.attrib.get("file", "")
    candidates: list[str] = []
    if testcase.attrib.get("nodeid"):
        candidates.append(testcase.attrib["nodeid"])
    if file_attr:
        candidates.append(f"{file_attr}::{name}")
    if classname and name:
        class_parts = [part for part in classname.split(".") if part]
        if class_parts:
            maybe_class = class_parts[-1]
            module_parts = class_parts[:-1] if not maybe_class.startswith("test_") else class_parts
            module_path = "/".join(module_parts) + ".py" if module_parts else ""
            if maybe_class.startswith("test_"):
                candidates.append(f"{'/'.join(class_parts)}.py::{name}")
            elif module_path:
                candidates.append(f"{module_path}::{maybe_class}::{name}")
                candidates.append(f"{module_path}::{name}")
    return [item for item in dict.fromkeys(candidates) if item]


def _match_junit_nodeid(testcase: ET.Element, selected_nodeids: list[str]) -> str:
    candidates = _junit_candidate_nodeids(testcase)
    selected = set(selected_nodeids)
    for candidate in candidates:
        if candidate in selected:
            return candidate
    name = testcase.attrib.get("name", "")
    classname = testcase.attrib.get("classname", "")
    matching_by_suffix = [
        nodeid
        for nodeid in selected_nodeids
        if _nodeid_suffix(nodeid).endswith(name) or nodeid.endswith(f"::{name}")
    ]
    if len(matching_by_suffix) == 1:
        return matching_by_suffix[0]
    matching_by_class = [
        nodeid
        for nodeid in matching_by_suffix
        if Path(nodeid.split("::", 1)[0]).stem in classname.replace(".", "/")
    ]
    if len(matching_by_class) == 1:
        return matching_by_class[0]
    return candidates[0] if candidates else name


def _parse_junit_results(junit_path: Path, selected_nodeids: list[str]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if not junit_path.exists():
        return {}, [f"JUnit XML not found: {junit_path}"]
    try:
        root = ET.parse(junit_path).getroot()
    except ET.ParseError as exc:
        return {}, [f"JUnit XML parse failed: {exc}"]
    results: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    for testcase in root.findall(".//testcase"):
        nodeid = _match_junit_nodeid(testcase, selected_nodeids)
        if nodeid in results:
            warnings.append(f"duplicate JUnit testcase mapped to {nodeid}")
        results[nodeid] = {
            "nodeid": nodeid,
            "outcome": _junit_outcome(testcase),
            "duration": _junit_duration(testcase),
            "reason": _junit_reason(testcase),
        }
    if not results and selected_nodeids:
        warnings.append("JUnit XML contained no testcase records")
    return results, warnings


def _merge_phase_results(
    cases: list[CatalogCase],
    plugin_results: dict[str, dict[str, Any]],
    junit_results: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str], str]:
    warnings: list[str] = []
    source = "junit" if junit_results else "plugin"
    results: list[dict[str, Any]] = []
    for case in cases:
        junit_result = junit_results.get(case.nodeid)
        plugin_result = plugin_results.get(case.nodeid)
        if junit_result and plugin_result and junit_result.get("outcome") != plugin_result.get("outcome"):
            warnings.append(
                f"result mismatch for {case.nodeid}: plugin={plugin_result.get('outcome')} junit={junit_result.get('outcome')}"
            )
        results.append(junit_result or plugin_result or _default_case_result(case.nodeid))
    return results, warnings, source


def _result_counts(case_results: list[dict[str, Any]]) -> dict[str, int]:
    outcomes = [item.get("outcome", "not_run") for item in case_results]
    return {
        "executed": sum(1 for outcome in outcomes if outcome in EXECUTED_OUTCOMES),
        "passed": sum(1 for outcome in outcomes if outcome in PASSED_OUTCOMES),
        "failed": sum(1 for outcome in outcomes if outcome in FAILED_OUTCOMES),
        "skipped": sum(1 for outcome in outcomes if outcome == "skipped"),
        "not_run": sum(1 for outcome in outcomes if outcome == "not_run"),
    }


def _selector_text(selector: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("module", "feature", "story", "priority", "site", "case_id", "path", "nodeid"):
        value = selector.get(key)
        if value:
            parts.append(f"--{key.replace('_', '-')} {value}")
    return " ".join(parts)


def _normalize_selector_payloads(value: Any) -> list[dict[str, Any]]:
    if not value:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _load_prerequisite_config() -> dict[str, Any]:
    payload = load_yaml(PREREQUISITES_PATH)
    payload.setdefault("features", {})
    payload.setdefault("cases", {})
    payload.setdefault("nodeids", {})
    return payload


def _resolve_prerequisite_selectors(selected_cases: list[CatalogCase], config: dict[str, Any]) -> list[dict[str, Any]]:
    selectors: dict[str, dict[str, Any]] = {}
    for case in selected_cases:
        values = []
        if case.case_id:
            values.extend(_normalize_selector_payloads(config.get("cases", {}).get(case.case_id)))
        values.extend(_normalize_selector_payloads(config.get("nodeids", {}).get(case.nodeid)))
        if case.feature_id:
            values.extend(_normalize_selector_payloads(config.get("features", {}).get(case.feature_id)))
        for selector in values:
            text = _selector_text(selector)
            if text:
                selectors[text] = selector
    return list(selectors.values())


def _resolve_prerequisite_cases(selected_cases: list[CatalogCase], catalog: list[CatalogCase], config: dict[str, Any]) -> tuple[list[CatalogCase], list[dict[str, Any]]]:
    selector_payloads = _resolve_prerequisite_selectors(selected_cases, config)
    selected_nodeids = {case.nodeid for case in selected_cases}
    prerequisite_map: dict[str, CatalogCase] = {}

    for selector in selector_payloads:
        criteria = SelectionCriteria(
            module=selector.get("module"),
            feature=selector.get("feature"),
            story=selector.get("story"),
            priority=selector.get("priority"),
            site=selector.get("site"),
            case_id=selector.get("case_id"),
            path=selector.get("path"),
            nodeid=selector.get("nodeid"),
        )
        for case in catalog:
            if case.skill_excluded or case.nodeid in selected_nodeids:
                continue
            if matches_case(case, criteria):
                prerequisite_map[case.nodeid] = case

    return sorted(prerequisite_map.values(), key=lambda item: item.nodeid), selector_payloads


def _run_phase(
    phase_name: str,
    cases: list[CatalogCase],
    run_dir: Path,
    allure_dir: Path,
    pytest_cmd: list[str],
    workers: int = 1,
) -> dict[str, Any]:
    junit_path = _phase_junit_path(run_dir, phase_name)
    nodeids = [case.nodeid for case in cases]
    if not nodeids:
        empty_marker = junit_path.with_suffix(".empty.json")
        save_json(empty_marker, {"phase": phase_name, "selected": 0})
        return {
            "phase": phase_name,
            "pytest_exit_code": 0,
            "junit_path": str(junit_path),
            "case_results": [],
            "selected_count": 0,
            "resolved_workers": workers,
            "parallel_enabled": False,
            "result_source": "empty",
            "result_warnings": [],
            "empty_marker_path": str(empty_marker),
        }

    plugin = _RunPlugin()
    pytest_args = _build_pytest_args(nodeids, junit_path, allure_dir, workers=workers)
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    output_path = _phase_output_path(run_dir, phase_name)
    if workers > 1:
        command = pytest_cmd + pytest_args
        result = subprocess.run(command, cwd=ROOT_DIR, capture_output=True, text=True)
        exit_code = result.returncode
        output_path.write_text((result.stdout or "") + "\n" + (result.stderr or ""), encoding="utf-8")
        plugin_results: dict[str, dict[str, Any]] = {}
    else:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exit_code = pytest.main(pytest_args, plugins=[plugin])
        output_path.write_text(stdout_buffer.getvalue() + "\n" + stderr_buffer.getvalue(), encoding="utf-8")
        plugin_results = plugin.case_results
    junit_results, junit_warnings = _parse_junit_results(junit_path, nodeids)
    case_results, merge_warnings, result_source = _merge_phase_results(cases, plugin_results, junit_results)
    return {
        "phase": phase_name,
        "pytest_exit_code": exit_code,
        "junit_path": str(junit_path),
        "output_path": str(output_path),
        "case_results": case_results,
        "selected_count": len(cases),
        "resolved_workers": workers,
        "parallel_enabled": workers > 1,
        "result_source": result_source,
        "result_warnings": junit_warnings + merge_warnings,
    }


def _determine_run_status(final_counts: dict[str, int], block_reason: str | None) -> str:
    if block_reason:
        return "blocked"
    if final_counts["failed"] > 0:
        return "failed"
    if final_counts["executed"] > 0:
        return "passed"
    return "blocked"


def _delete_file(path: Path, deleted: list[str]) -> None:
    try:
        if path.exists() and path.is_file():
            path.unlink()
            deleted.append(str(path))
    except OSError:
        return


def _lean_cleanup(run_dir: Path, summary: dict[str, Any]) -> dict[str, Any]:
    if summary.get("dry_run"):
        return {"enabled": False, "deleted": [], "reason": "dry-run keeps preview artifacts"}
    if summary.get("run_status") != "passed":
        return {"enabled": False, "deleted": [], "reason": f"run_status={summary.get('run_status')} keeps debug artifacts"}
    if summary.get("artifact_retention") != "lean":
        return {"enabled": False, "deleted": [], "reason": "artifact_retention=full"}

    deleted: list[str] = []
    for name in ("coverage_input.json", "decision_input.json", "selection.json", "pytest_command.txt"):
        _delete_file(run_dir / name, deleted)
    for phase in summary.get("phase_reports", []) or []:
        if not isinstance(phase, dict):
            continue
        counts = _result_counts(phase.get("case_results", []) or [])
        if phase.get("pytest_exit_code") == 0 and counts["failed"] == 0:
            output_path = phase.get("output_path")
            if output_path:
                _delete_file(Path(output_path), deleted)
        empty_marker = phase.get("empty_marker_path")
        if empty_marker:
            _delete_file(Path(empty_marker), deleted)
    return {"enabled": True, "deleted": deleted, "reason": "passed run with lean retention"}


def handle_run(args: argparse.Namespace) -> int:
    criteria = build_criteria(args)
    selected_cases = select_cases(criteria)
    if not selected_cases:
        print("matched_cases=0")
        return 1

    run_id = create_run_id([case.nodeid for case in selected_cases])
    run_dir = ensure_dir(REPORTS_DIR / run_id)
    pytest_cmd, pytest_display = resolve_pytest_command()
    allure_dir = ensure_dir(run_dir / "allure-results")

    save_json(run_dir / "selection.json", {"cases": [case.to_dict() for case in selected_cases]})
    nodeids = [case.nodeid for case in selected_cases]
    catalog = load_catalog()
    scoped_cases, recommended_cases, baseline_cases = recommend_cases(catalog, criteria, selected_cases)
    prerequisite_config = _load_prerequisite_config()
    prerequisite_cases, prerequisite_selectors = _resolve_prerequisite_cases(selected_cases, catalog, prerequisite_config)
    worker_resolution = _resolve_workers(args, len(selected_cases), bool(prerequisite_cases))
    resolved_workers = int(worker_resolution["resolved_workers"])
    command_hint = pytest_cmd + _build_pytest_args(
        nodeids,
        _phase_junit_path(run_dir, "target_initial"),
        allure_dir,
        workers=resolved_workers,
    )
    (run_dir / "pytest_command.txt").write_text(shell_join(command_hint), encoding="utf-8")

    if args.dry_run:
        case_results = [{"nodeid": case.nodeid, "outcome": "selected", "duration": 0.0, "reason": None} for case in selected_cases]
        summary = _build_summary(run_id, args, selected_cases, case_results, dry_run=True)
        summary.update(worker_resolution)
        summary["pytest_command"] = shell_join(command_hint)
        summary["scope_case_nodeids"] = [case.nodeid for case in scoped_cases]
        summary["recommended_case_nodeids"] = [case.nodeid for case in recommended_cases]
        summary["baseline_case_nodeids"] = [case.nodeid for case in baseline_cases]
        summary["prerequisite_selected_count"] = len(prerequisite_cases)
        summary["prerequisite_selector_texts"] = [_selector_text(item) for item in prerequisite_selectors]
        save_json(run_dir / "coverage_input.json", summary)
        save_json(run_dir / "decision_input.json", summary)
        save_json(run_dir / "summary.json", summary)
        print(f"run_id={run_id}")
        print("mode=dry-run")
        print(f"matched_cases={len(selected_cases)}")
        print(f"recommended_cases={len(recommended_cases)}")
        print(f"baseline_cases={len(baseline_cases)}")
        print(f"requested_workers={summary['requested_workers']}")
        print(f"resolved_workers={summary['resolved_workers']}")
        print(f"parallel_enabled={str(summary['parallel_enabled']).lower()}")
        print(f"parallel_reason={summary['parallel_reason']}")
        print(f"pytest={pytest_display}")
        _print_selected_cases(selected_cases)
        return 0

    initial_phase = _run_phase("target_initial", selected_cases, run_dir, allure_dir, pytest_cmd, workers=resolved_workers)
    initial_results = initial_phase["case_results"]
    initial_counts = _result_counts(initial_results)

    prerequisite_attempted = bool(prerequisite_cases) and any(
        item["outcome"] in {"skipped", "not_run"} for item in initial_results
    )
    prerequisite_phase: dict[str, Any] | None = None
    final_phase = initial_phase
    block_reason: str | None = None

    if prerequisite_attempted:
        prerequisite_phase = _run_phase("prerequisite", prerequisite_cases, run_dir, allure_dir, pytest_cmd, workers=1)
        prerequisite_counts = _result_counts(prerequisite_phase["case_results"])
        if prerequisite_counts["failed"] > 0:
            block_reason = "已自动补跑前置，但前置用例存在失败，请先处理前置问题后再重跑目标场景。"
        elif prerequisite_counts["executed"] == 0:
            block_reason = "已尝试自动补跑前置，但前置用例未真正执行，请先检查环境、账号或前置数据。"
        else:
            final_phase = _run_phase("target_after_prerequisite", selected_cases, run_dir, allure_dir, pytest_cmd, workers=resolved_workers)
    else:
        prerequisite_counts = _result_counts([])

    final_results = final_phase["case_results"]
    final_counts = _result_counts(final_results)
    if block_reason is None and final_counts["executed"] == 0:
        if prerequisite_attempted:
            block_reason = "已自动补跑前置，但目标用例仍未真正执行，请检查前置映射或环境数据。"
        else:
            block_reason = "目标用例未真正执行，请检查环境、账号或补充前置映射。"

    summary = _build_summary(run_id, args, selected_cases, final_results, dry_run=False)
    summary.update(worker_resolution)
    summary["pytest_command"] = shell_join(command_hint)
    summary["pytest_exit_code"] = final_phase["pytest_exit_code"]
    summary["scope_case_nodeids"] = [case.nodeid for case in scoped_cases]
    summary["recommended_case_nodeids"] = [case.nodeid for case in recommended_cases]
    summary["baseline_case_nodeids"] = [case.nodeid for case in baseline_cases]
    summary["prerequisite_attempted"] = prerequisite_attempted
    summary["prerequisite_selected_count"] = len(prerequisite_cases)
    summary["prerequisite_passed_count"] = prerequisite_counts["passed"]
    summary["prerequisite_selector_texts"] = [_selector_text(item) for item in prerequisite_selectors]
    summary["executed_cases"] = final_counts["executed"]
    summary["passed_cases"] = final_counts["passed"]
    summary["failed_cases"] = final_counts["failed"]
    summary["skipped_cases"] = final_counts["skipped"]
    summary["block_reason"] = block_reason
    summary["run_status"] = _determine_run_status(final_counts, block_reason)
    summary["phase_reports"] = [initial_phase] + ([prerequisite_phase] if prerequisite_phase else []) + ([final_phase] if final_phase is not initial_phase else [])

    save_json(run_dir / "coverage_input.json", summary)
    save_json(run_dir / "decision_input.json", summary)
    save_json(run_dir / "summary.json", summary)

    latest_junit_path = Path(final_phase["junit_path"])
    _sync_latest_report_assets(run_id, latest_junit_path, allure_dir)
    coverage_result = compute_coverage(summary)
    decision_result = evaluate_decision(summary)
    save_json(run_dir / "coverage_report.json", coverage_result)
    save_json(run_dir / "decision_report.json", decision_result)
    allure_result = _generate_allure_report()
    summary["allure_report"] = allure_result["report_dir"]
    summary["allure_url"] = allure_result.get("url")
    summary["lean_cleanup"] = _lean_cleanup(run_dir, summary)
    save_json(run_dir / "summary.json", summary)

    print(f"run_id={run_id}")
    print(f"run_status={summary['run_status']}")
    print(f"pytest_exit_code={summary['pytest_exit_code']}")
    print(f"matched_cases={len(selected_cases)}")
    print(f"executed_cases={summary['executed_cases']}")
    print(f"passed_cases={summary['passed_cases']}")
    print(f"failed_cases={summary['failed_cases']}")
    print(f"skipped_cases={summary['skipped_cases']}")
    print(f"requested_workers={summary['requested_workers']}")
    print(f"resolved_workers={summary['resolved_workers']}")
    print(f"parallel_enabled={str(summary['parallel_enabled']).lower()}")
    print(f"parallel_reason={summary['parallel_reason']}")
    print(f"artifact_retention={summary['artifact_retention']}")
    if summary.get("lean_cleanup", {}).get("enabled"):
        print(f"lean_cleanup_deleted={len(summary['lean_cleanup'].get('deleted', []))}")
    print(f"prerequisite_attempted={str(prerequisite_attempted).lower()}")
    print(f"prerequisite_selected_count={summary['prerequisite_selected_count']}")
    print(f"prerequisite_passed_count={summary['prerequisite_passed_count']}")
    if prerequisite_attempted and summary["prerequisite_selector_texts"]:
        print("prerequisite_selectors=")
        for item in summary["prerequisite_selector_texts"]:
            print(f"- {item}")
    if summary["run_status"] == "blocked":
        print(f"block_reason={summary['block_reason']}")
    else:
        print(f"推荐范围执行率={coverage_result['requirement_execution_coverage']:.2%}")
        print(f"本次通过率={coverage_result['requirement_pass_rate']:.2%}")
    print(f"risk_level={decision_result['risk_level']}")
    print(f"suggestion={decision_result['suggestion']}")
    print(f"reason={decision_result['reason']}")
    print(f"allure_results={ALLURE_RESULTS_DIR}")
    print(f"allure_report={allure_result['report_dir']}")
    print(f"allure_url={allure_result.get('url') or 'unavailable'}")
    print(f"junit_path={ROOT_REPORTS_DIR / 'junit.xml'}")
    print(f"screenshots_path={ROOT_REPORTS_DIR / 'screenshots'}")
    print(f"allure_status={allure_result['message']}")
    return 0 if summary["run_status"] != "blocked" else 2
