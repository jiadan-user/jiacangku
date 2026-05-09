from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
KB_ROOT = ROOT / "bundled" / "knowledge_base" / "文本用例"
TOOLING_ROOT = ROOT / "bundled" / "skills" / "ok_autotest_ui_skill" / "bundled" / "ok_autotest_ui_pc"
DEFAULT_OUT_DIR = ROOT / ".qa_agent" / "coverage_accuracy"

sys.path.insert(0, str(TOOLING_ROOT))

from tooling.ok_test.text_coverage import build_text_case_dashboard, load_text_case_documents  # noqa: E402


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
SCENARIO_RE = re.compile(r"^#{2,6}\s*(TC[0-9A-Za-z_-]+)(?:\s*[:：]\s*|\s+)?(.+)$", re.MULTILINE)
PRIORITY_RE = re.compile(r"优先级\*?\*?\s*[:：]\s*(P[0-3])", re.IGNORECASE)
AUTOMATION_RE = re.compile(
    r"(?:^|[|｜])\s*(?:[-*]\s*)?\*{0,2}(?:UI\s*自动化|自动化可行性|是否自动化|自动化)\*{0,2}\s*[:：]\s*([^\n\r|]+)",
    re.IGNORECASE | re.MULTILINE,
)
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
TC_IN_TABLE_RE = re.compile(r"\bTC[0-9A-Za-z_-]+\b", re.IGNORECASE)
PRIORITIES = ("P0", "P1", "P2", "P3")
EXCLUDED_DOC_TOKENS = (
    "README",
    "归档记录",
    "更新记录",
    "问题原因",
    "修改方案",
    "调试报告",
    "运行与调试报告",
    "明确化",
    "CLARIFICATION_REPORT",
    "FINAL_DEBUG_GUIDE",
    "DEBUG_SUMMARY",
    "TEST_REPORT",
    "FINAL_REPORT",
    "ADD_FINAL",
    "RESUME_DEBUG",
)
MODULE_MAP = {
    "ai": "ai",
    "kyc": "kyc",
    "marketplace": "marketplace",
    "marketplace_order": "marketplace_order",
    "marketplace_post": "marketplace_post",
    "property_detail": "property_detail",
    "property_list": "property_list",
    "property_map": "property_map",
    "test_car": "car",
    "wallet": "wallet",
    "zhaopin": "zhaopin",
    "SEO": "seo",
    "vidflow": "vidflow",
    "Tiyan": "tiyan",
}


@dataclass
class LedgerRow:
    row_id: str
    parser: str
    document: str
    module_id: str
    group_name: str
    tc_id: str
    occurrence: int
    title: str
    priority: str
    automated: bool
    needs_normalization: bool
    missing_fields: str

    def comparable(self) -> tuple[Any, ...]:
        return (
            self.document,
            self.tc_id,
            self.occurrence,
            self.title,
            self.priority,
            self.automated,
            self.needs_normalization,
            self.missing_fields,
        )


def module_id_for(relative_path: Path) -> str:
    top = relative_path.parts[0] if relative_path.parts else ""
    path_text = relative_path.as_posix()
    if top == "test_car" and "探索列表" in path_text:
        return "car_list"
    if top == "Tiyan" and "Search/" in path_text:
        return "search_input"
    if top == "Property" and "Basic/List/" in path_text:
        return "property_list"
    if top == "Property" and "Basic/Map/" in path_text:
        return "property_map"
    return MODULE_MAP.get(top, top.lower() or "unknown")


def parse_automation(block: str) -> bool | None:
    match = AUTOMATION_RE.search(block)
    if not match:
        return None
    compact = re.sub(r"\s+", "", match.group(1))
    if any(token in compact for token in ("不可自动化", "未自动化", "不适合自动化")) or compact.startswith("❌"):
        return False
    if any(token in compact for token in ("可自动化", "已自动化")) or compact.startswith(("✅", "⚠")):
        return True
    return None


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    return bool(TABLE_SEPARATOR_RE.match(line.strip()))


def independent_table_rows(block: str, group_name: str, default_priority: str | None, default_automation: bool | None) -> list[dict[str, Any]]:
    lines = block.splitlines()
    rows_out: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        if not (lines[index].strip().startswith("|") and lines[index].strip().endswith("|")):
            index += 1
            continue
        table: list[str] = []
        while index < len(lines) and lines[index].strip().startswith("|") and lines[index].strip().endswith("|"):
            table.append(lines[index])
            index += 1
        if len(table) < 3:
            continue
        rows = [split_row(item) for item in table]
        header = [cell.replace("*", "").replace(" ", "").strip() for cell in rows[0]]
        data = rows[2:] if len(rows) > 1 and is_separator(table[1]) else rows[1:]
        tc_idx = next((i for i, cell in enumerate(header) if cell in {"编号", "TC", "用例编号", "TC编号"}), 0)
        if not any(tc_idx < len(row) and TC_IN_TABLE_RE.search(row[tc_idx]) for row in data):
            continue
        priority_idx = next((i for i, cell in enumerate(header) if "优先级" in cell), None)
        automation_idx = next(
            (
                i
                for i, cell in enumerate(header)
                if ("UI自动化" in cell or cell == "自动化" or "自动化可行性" in cell)
                and "不可自动化" not in cell
                and "未自动化" not in cell
                and "率" not in cell
            ),
            None,
        )
        for row in data:
            if tc_idx >= len(row):
                continue
            tc_match = TC_IN_TABLE_RE.search(row[tc_idx])
            if not tc_match:
                continue
            priority = default_priority
            if priority_idx is not None and priority_idx < len(row):
                priority_match = re.search(r"P[0-3]", row[priority_idx], re.IGNORECASE)
                if priority_match:
                    priority = priority_match.group(0).upper()
            automation = default_automation
            if automation_idx is not None and automation_idx < len(row):
                automation = parse_automation(f"UI自动化: {row[automation_idx]}")
            title = ""
            for cell_index, cell in enumerate(row):
                if cell_index in {tc_idx, priority_idx, automation_idx}:
                    continue
                if cell:
                    title = cell
                    break
            missing = []
            if not priority:
                missing.append("优先级")
            if automation is None:
                missing.append("UI自动化")
            rows_out.append(
                {
                    "group_name": group_name,
                    "tc_id": tc_match.group(0),
                    "title": title or tc_match.group(0),
                    "priority": priority or "未标注",
                    "automated": bool(automation),
                    "needs_normalization": bool(missing),
                    "missing_fields": ",".join(missing),
                }
            )
    return rows_out


def independent_doc_rows(root: Path, path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    headings = list(HEADING_RE.finditer(text))
    rows: list[dict[str, Any]] = []
    current_group = "未分组"
    for index, heading in enumerate(headings):
        level = len(heading.group(1))
        heading_text = heading.group(2).strip()
        scenario = SCENARIO_RE.match(heading.group(0))
        if level == 2 and not scenario:
            current_group = heading_text
            continue
        if level < 3 or not scenario:
            continue
        start = heading.end()
        end = len(text)
        for next_heading in headings[index + 1 :]:
            if len(next_heading.group(1)) <= 3:
                end = next_heading.start()
                break
        block = text[start:end]
        priority_match = PRIORITY_RE.search(block)
        priority = priority_match.group(1).upper() if priority_match else None
        automation = parse_automation(block)
        if "~" in heading_text or "～" in heading_text:
            table_rows = independent_table_rows(block, current_group, priority, automation)
            if table_rows:
                rows.extend(table_rows)
                continue
        missing = []
        if not priority:
            missing.append("优先级")
        if automation is None:
            missing.append("UI自动化")
        rows.append(
            {
                "group_name": current_group,
                "tc_id": scenario.group(1),
                "title": scenario.group(2).strip(),
                "priority": priority or "未标注",
                "automated": bool(automation),
                "needs_normalization": bool(missing),
                "missing_fields": ",".join(missing),
            }
        )
    return rows


def independent_ledger(root: Path) -> tuple[list[LedgerRow], dict[str, Any]]:
    rows: list[LedgerRow] = []
    markdown_files = 0
    excluded_files: list[dict[str, str]] = []
    for path in sorted(root.rglob("*.md")):
        markdown_files += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root)
        heading_count = len(SCENARIO_RE.findall(text))
        if path.suffix.lower() != ".md" or any(token in path.name for token in EXCLUDED_DOC_TOKENS) or not heading_count:
            excluded_files.append({"path": rel.as_posix(), "reason": "excluded_doc" if heading_count else "no_tc_heading"})
            continue
        module_id = module_id_for(rel)
        occurrences: Counter[str] = Counter()
        for item in independent_doc_rows(root, path):
            occurrences[item["tc_id"]] += 1
            occurrence = occurrences[item["tc_id"]]
            row_id = f"{rel.as_posix()}::{item['tc_id']}::{occurrence}"
            rows.append(
                LedgerRow(
                    row_id=row_id,
                    parser="independent",
                    document=rel.as_posix(),
                    module_id=module_id,
                    group_name=item["group_name"],
                    tc_id=item["tc_id"],
                    occurrence=occurrence,
                    title=item["title"],
                    priority=item["priority"],
                    automated=item["automated"],
                    needs_normalization=item["needs_normalization"],
                    missing_fields=item["missing_fields"],
                )
            )
    diagnostics = {
        "markdown_files": markdown_files,
        "files_with_cases": len({row.document for row in rows}),
        "parsed_scenarios": len(rows),
        "needs_normalization_cases": sum(1 for row in rows if row.needs_normalization),
        "excluded_files_count": len(excluded_files),
        "excluded_files": excluded_files,
    }
    return rows, diagnostics


def dashboard_ledger(root: Path) -> list[LedgerRow]:
    rows: list[LedgerRow] = []
    for document in load_text_case_documents(root):
        occurrences: Counter[str] = Counter()
        for scenario in document.scenarios:
            occurrences[scenario.tc_id] += 1
            occurrence = occurrences[scenario.tc_id]
            row_id = f"{document.relative_path}::{scenario.tc_id}::{occurrence}"
            rows.append(
                LedgerRow(
                    row_id=row_id,
                    parser="dashboard",
                    document=document.relative_path,
                    module_id=document.module_id,
                    group_name=scenario.group_name,
                    tc_id=scenario.tc_id,
                    occurrence=occurrence,
                    title=scenario.title,
                    priority=scenario.priority,
                    automated=scenario.automated,
                    needs_normalization=scenario.needs_normalization,
                    missing_fields=",".join(scenario.missing_fields),
                )
            )
    return rows


def summarize(rows: list[LedgerRow]) -> dict[str, Any]:
    priority_total: Counter[str] = Counter()
    priority_auto: Counter[str] = Counter()
    module_total: Counter[str] = Counter()
    module_auto: Counter[str] = Counter()
    for row in rows:
        priority_total[row.priority] += 1
        if row.automated:
            priority_auto[row.priority] += 1
        module_total[row.module_id] += 1
        if row.automated:
            module_auto[row.module_id] += 1
    return {
        "total_cases": len(rows),
        "automated_cases": sum(1 for row in rows if row.automated),
        "non_automated_cases": sum(1 for row in rows if not row.automated),
        "needs_normalization_cases": sum(1 for row in rows if row.needs_normalization),
        "priorities": [
            {
                "priority": priority,
                "total_cases": priority_total.get(priority, 0),
                "automated_cases": priority_auto.get(priority, 0),
                "non_automated_cases": priority_total.get(priority, 0) - priority_auto.get(priority, 0),
            }
            for priority in PRIORITIES
        ],
        "modules": [
            {
                "module": module,
                "total_cases": module_total[module],
                "automated_cases": module_auto[module],
                "non_automated_cases": module_total[module] - module_auto[module],
            }
            for module in sorted(module_total)
        ],
    }


def write_ledger(path: Path, rows: list[LedgerRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()) if rows else list(LedgerRow.__dataclass_fields__))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def fetch_dashboard(base_url: str, project_id: int) -> dict[str, Any]:
    url = base_url.rstrip("/") + f"/api/qa-agent/projects/{project_id}/coverage/latest"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def compare_dict(left: dict[str, Any], right: dict[str, Any], keys: list[str], *, float_keys: set[str] | None = None) -> list[dict[str, Any]]:
    float_keys = float_keys or set()
    diffs: list[dict[str, Any]] = []
    for key in keys:
        left_value = left.get(key)
        right_value = right.get(key)
        if key in float_keys:
            if not math.isclose(float(left_value or 0), float(right_value or 0), rel_tol=1e-12, abs_tol=1e-12):
                diffs.append({"key": key, "left": left_value, "right": right_value})
        elif left_value != right_value:
            diffs.append({"key": key, "left": left_value, "right": right_value})
    return diffs


def priority_map(payload: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {item["priority"]: {k: int(item.get(k) or 0) for k in ("total_cases", "automated_cases", "non_automated_cases")} for item in payload.get("priorities", [])}


def module_map(payload: dict[str, Any]) -> dict[str, dict[str, int]]:
    result = {}
    for item in payload.get("modules", []) or payload.get("module_breakdown", []):
        module = item.get("module")
        if not module:
            continue
        result[module] = {
            "total_cases": int(item.get("total_cases") or 0),
            "automated_cases": int(item.get("automated_cases") or 0),
            "non_automated_cases": int(item.get("non_automated_cases") or 0),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit coverage accuracy with ledger, independent parser, and dashboard readback.")
    parser.add_argument("--root", default=str(KB_ROOT))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--dashboard-url", default="http://10.192.35.53:8001")
    parser.add_argument("--project-id", type=int, default=1)
    parser.add_argument("--skip-dashboard", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dashboard_rows = dashboard_ledger(root)
    independent_rows, independent_diagnostics = independent_ledger(root)
    dashboard_summary = build_text_case_dashboard(root)
    dashboard_ledger_summary = summarize(dashboard_rows)
    independent_summary = summarize(independent_rows)

    write_ledger(out_dir / "coverage_ledger_dashboard.csv", dashboard_rows)
    write_ledger(out_dir / "coverage_ledger_independent.csv", independent_rows)
    (out_dir / "coverage_ledger_dashboard.json").write_text(
        json.dumps([asdict(row) for row in dashboard_rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "coverage_ledger_independent.json").write_text(
        json.dumps([asdict(row) for row in independent_rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    dashboard_rows_by_key = {row.row_id: row for row in dashboard_rows}
    independent_rows_by_key = {row.row_id: row for row in independent_rows}
    only_dashboard = sorted(set(dashboard_rows_by_key) - set(independent_rows_by_key))
    only_independent = sorted(set(independent_rows_by_key) - set(dashboard_rows_by_key))
    row_diffs = []
    for key in sorted(set(dashboard_rows_by_key) & set(independent_rows_by_key)):
        left = dashboard_rows_by_key[key]
        right = independent_rows_by_key[key]
        if left.comparable() != right.comparable():
            row_diffs.append({"row_id": key, "dashboard": asdict(left), "independent": asdict(right)})

    dashboard_summary_diffs = compare_dict(
        dashboard_summary,
        dashboard_ledger_summary,
        ["total_cases", "automated_cases", "non_automated_cases"],
    )
    dashboard_summary_diffs.extend(
        compare_dict(
            {"needs_normalization_cases": dashboard_summary.get("parse_diagnostics", {}).get("needs_normalization_cases")},
            {"needs_normalization_cases": dashboard_ledger_summary.get("needs_normalization_cases")},
            ["needs_normalization_cases"],
        )
    )
    independent_summary_diffs = compare_dict(
        dashboard_ledger_summary,
        independent_summary,
        ["total_cases", "automated_cases", "non_automated_cases", "needs_normalization_cases"],
    )
    priority_diffs = []
    if priority_map(dashboard_ledger_summary) != priority_map(independent_summary):
        priority_diffs.append({"dashboard": priority_map(dashboard_ledger_summary), "independent": priority_map(independent_summary)})
    module_diffs = []
    if module_map(dashboard_ledger_summary) != module_map(independent_summary):
        module_diffs.append({"dashboard": module_map(dashboard_ledger_summary), "independent": module_map(independent_summary)})

    remote_payload: dict[str, Any] | None = None
    remote_diffs: list[dict[str, Any]] = []
    remote_error: str | None = None
    if not args.skip_dashboard:
        try:
            remote_payload = fetch_dashboard(args.dashboard_url, args.project_id)
            remote_diffs.extend(
                compare_dict(
                    dashboard_summary,
                    remote_payload,
                    ["total_cases", "automated_cases", "non_automated_cases", "automation_rate", "total_p0_missing", "total_p1_missing"],
                    float_keys={"automation_rate"},
                )
            )
            remote_diag = remote_payload.get("parse_diagnostics") or {}
            remote_diffs.extend(
                compare_dict(
                    {"needs_normalization_cases": dashboard_summary.get("parse_diagnostics", {}).get("needs_normalization_cases")},
                    {"needs_normalization_cases": remote_diag.get("needs_normalization_cases")},
                    ["needs_normalization_cases"],
                )
            )
            if priority_map(dashboard_summary) != priority_map(remote_payload):
                remote_diffs.append({"key": "priorities", "local": priority_map(dashboard_summary), "remote": priority_map(remote_payload)})
            if module_map(dashboard_summary) != module_map(remote_payload):
                remote_diffs.append({"key": "modules", "local_count": len(module_map(dashboard_summary)), "remote_count": len(module_map(remote_payload))})
        except Exception as exc:
            remote_error = str(exc)

    failures = {
        "dashboard_summary_vs_ledger": dashboard_summary_diffs,
        "dashboard_ledger_only": only_dashboard[:50],
        "independent_ledger_only": only_independent[:50],
        "row_diffs": row_diffs[:50],
        "independent_summary_diffs": independent_summary_diffs,
        "priority_diffs": priority_diffs,
        "module_diffs": module_diffs,
        "remote_diffs": remote_diffs,
        "remote_error": remote_error,
    }
    passed = not any(value for value in failures.values() if value)
    report = {
        "status": "passed" if passed else "failed",
        "knowledge_base_path": str(root),
        "artifacts": {
            "dashboard_ledger_csv": str(out_dir / "coverage_ledger_dashboard.csv"),
            "independent_ledger_csv": str(out_dir / "coverage_ledger_independent.csv"),
            "dashboard_ledger_json": str(out_dir / "coverage_ledger_dashboard.json"),
            "independent_ledger_json": str(out_dir / "coverage_ledger_independent.json"),
        },
        "dashboard_summary": {
            "total_cases": dashboard_summary["total_cases"],
            "automated_cases": dashboard_summary["automated_cases"],
            "non_automated_cases": dashboard_summary["non_automated_cases"],
            "automation_rate": dashboard_summary["automation_rate"],
            "total_p0_missing": dashboard_summary["total_p0_missing"],
            "total_p1_missing": dashboard_summary["total_p1_missing"],
            "needs_normalization_cases": dashboard_summary["parse_diagnostics"]["needs_normalization_cases"],
            "priorities": dashboard_summary["priorities"],
        },
        "dashboard_ledger_summary": dashboard_ledger_summary,
        "independent_summary": independent_summary,
        "independent_diagnostics": independent_diagnostics,
        "remote_summary": (
            {
                "total_cases": remote_payload.get("total_cases"),
                "automated_cases": remote_payload.get("automated_cases"),
                "non_automated_cases": remote_payload.get("non_automated_cases"),
                "automation_rate": remote_payload.get("automation_rate"),
                "total_p0_missing": remote_payload.get("total_p0_missing"),
                "total_p1_missing": remote_payload.get("total_p1_missing"),
                "priorities": remote_payload.get("priorities"),
                "parse_diagnostics": remote_payload.get("parse_diagnostics"),
            }
            if remote_payload
            else None
        ),
        "failures": failures,
    }
    report_path = out_dir / "coverage_accuracy_audit.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(report_path), "summary": report["dashboard_summary"], "failures": failures}, ensure_ascii=False, indent=2))
    if args.strict and not passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
