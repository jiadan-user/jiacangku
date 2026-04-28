from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .common import (
    ROOT_DIR,
    default_coverage_dashboard_path,
    default_dashboard_modules_dir,
    save_text,
    slugify,
    utcnow_iso,
)


def _default_knowledge_base() -> Path:
    for base in [ROOT_DIR, *ROOT_DIR.parents]:
        bundled_candidate = base / "bundled" / "knowledge_base" / "文本用例"
        if bundled_candidate.exists():
            return bundled_candidate
        sibling_candidate = base / "knowledge_base" / "文本用例"
        if sibling_candidate.exists():
            return sibling_candidate
    return ROOT_DIR / "test_data" / "knowledge_base" / "文本用例"


DEFAULT_KNOWLEDGE_BASE = _default_knowledge_base()
SUMMARY_TOTAL_RE = re.compile(r"总用例数[^0-9]*(\d+)\s*条")
SUMMARY_AUTOMATED_RE = re.compile(r"可自动化[^0-9]*(\d+)\s*条")
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
SCENARIO_HEADING_RE = re.compile(r"^###\s*(TC[0-9A-Za-z_-]+)(?:\s*[:：]\s*|\s+)?(.+)$", re.MULTILINE)
PRIORITY_RE = re.compile(r"优先级\*?\*?\s*[:：]\s*(P[0-3])", re.IGNORECASE)
UI_AUTOMATION_RE = re.compile(r"UI自动化\*?\*?\s*[:：]\s*([^\n\r]+)")
UNSPECIFIED_PRIORITY = "未标注"
PRIORITY_ORDER = ("P0", "P1", "P2", "P3")
PRIORITY_DESCRIPTIONS = {
    "P0": "主链路、必须优先保障",
    "P1": "核心功能，影响较大",
    "P2": "重要但不是主链路",
    "P3": "低风险长尾或体验类",
}
TEXT_CASE_MODULE_MAP = {
    "ai": "ai",
    "kyc": "kyc",
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
STATUS_ORDER = {"未开始": 0, "部分覆盖": 1, "已完成": 2}
FOCUSED_MODULES = ("car", "wallet", "zhaopin")


@dataclass
class TextCaseScenario:
    tc_id: str
    title: str
    priority: str
    automated: bool
    group_name: str
    needs_normalization: bool = False
    missing_fields: list[str] = field(default_factory=list)


@dataclass
class TextCaseDocument:
    module: str
    module_id: str
    relative_path: str
    feature_name: str
    feature_display_name: str
    scenarios: list[TextCaseScenario]

    @property
    def total_cases(self) -> int:
        return len(self.scenarios)

    @property
    def automated_cases(self) -> int:
        return sum(1 for item in self.scenarios if item.automated)

    @property
    def non_automated_cases(self) -> int:
        return max(self.total_cases - self.automated_cases, 0)

    @property
    def automation_rate(self) -> float:
        return self.automated_cases / self.total_cases if self.total_cases else 0.0

    @property
    def needs_normalization_cases(self) -> int:
        return sum(1 for item in self.scenarios if item.needs_normalization)


def _is_candidate_doc(path: Path, text: str) -> bool:
    if path.suffix.lower() != ".md":
        return False
    return bool(SCENARIO_HEADING_RE.search(text))


def _display_module(relative_path: Path) -> str:
    if not relative_path.parts:
        return "未分组"
    top = relative_path.parts[0]
    aliases = {
        "test_car": "test_car",
        "SEO": "SEO",
        "Tiyan": "Tiyan",
        "Property": "Property",
    }
    return aliases.get(top, top)


def _feature_name(path: Path, text: str) -> str:
    title = TITLE_RE.search(text)
    if title:
        return title.group(1).strip()
    return path.stem


def _feature_display_name(feature_name: str, path: Path) -> str:
    cleaned = feature_name.strip()
    cleaned = cleaned.replace("测试用例文档", "").replace("测试用例", "").strip(" -_")
    cleaned = re.sub(r"[-_ ]?20\d{6,8}$", "", cleaned).strip(" -_")
    if " - " in cleaned:
        parts = [part.strip() for part in cleaned.split(" - ") if part.strip()]
        if len(parts) >= 2:
            return parts[-1]
    if "_" in cleaned:
        return cleaned.replace("_", " ").strip()
    return cleaned or path.stem


def _document_module_id(relative_path: Path, display_module: str) -> str:
    top = relative_path.parts[0] if relative_path.parts else ""
    if top == "test_car" and "探索列表" in relative_path.as_posix():
        return "car_list"
    if top == "Tiyan" and "Search/" in relative_path.as_posix():
        return "search_input"
    if top == "Property" and "Basic/List/" in relative_path.as_posix():
        return "property_list"
    if top == "Property" and "Basic/Map/" in relative_path.as_posix():
        return "property_map"
    return TEXT_CASE_MODULE_MAP.get(top, slugify(display_module) or display_module.lower())


def _parse_automation(block: str) -> bool | None:
    automation_match = UI_AUTOMATION_RE.search(block)
    if not automation_match:
        return None
    value = automation_match.group(1).strip()
    if "不可自动化" in value or value.startswith("❌"):
        return False
    if "可自动化" in value or value.startswith("✅") or value.startswith("⚠"):
        return True
    return None


def _parse_scenarios(text: str) -> list[TextCaseScenario]:
    headings = list(HEADING_RE.finditer(text))
    scenarios: list[TextCaseScenario] = []
    current_group = "未分组"

    for index, heading in enumerate(headings):
        level = len(heading.group(1))
        heading_text = heading.group(2).strip()
        if level == 2:
            current_group = heading_text
            continue
        if level != 3:
            continue

        scenario_heading = SCENARIO_HEADING_RE.match(heading.group(0))
        if not scenario_heading:
            continue

        start = heading.end()
        end = len(text)
        for next_heading in headings[index + 1 :]:
            if len(next_heading.group(1)) <= 3:
                end = next_heading.start()
                break
        block = text[start:end]
        priority_match = PRIORITY_RE.search(block)
        automation = _parse_automation(block)
        missing_fields: list[str] = []
        if not priority_match:
            missing_fields.append("优先级")
        if automation is None:
            missing_fields.append("UI自动化")
        scenarios.append(
            TextCaseScenario(
                tc_id=scenario_heading.group(1).strip(),
                title=scenario_heading.group(2).strip(),
                priority=priority_match.group(1).upper() if priority_match else UNSPECIFIED_PRIORITY,
                automated=bool(automation),
                group_name=current_group or "未分组",
                needs_normalization=bool(missing_fields),
                missing_fields=missing_fields,
            )
        )
    return scenarios


def _parse_document(root: Path, path: Path) -> TextCaseDocument | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not _is_candidate_doc(path, text):
        return None

    scenarios = _parse_scenarios(text)
    if not scenarios:
        return None

    relative_path = path.relative_to(root)
    display_module = _display_module(relative_path)
    feature_name = _feature_name(path, text)
    module_id = _document_module_id(relative_path, display_module)
    return TextCaseDocument(
        module=display_module,
        module_id=module_id,
        relative_path=relative_path.as_posix(),
        feature_name=feature_name,
        feature_display_name=_feature_display_name(feature_name, path),
        scenarios=scenarios,
    )


def load_text_case_documents(root: Path = DEFAULT_KNOWLEDGE_BASE) -> list[TextCaseDocument]:
    documents, _diagnostics = _scan_text_case_documents(root)
    return documents


def _scan_text_case_documents(root: Path = DEFAULT_KNOWLEDGE_BASE) -> tuple[list[TextCaseDocument], dict[str, Any]]:
    documents: list[TextCaseDocument] = []
    markdown_files = 0
    files_with_tc_headings = 0
    tc_headings_total = 0
    needs_normalization_files: list[dict[str, Any]] = []
    excluded_files: list[dict[str, Any]] = []
    if not root.exists():
        return documents, {
            "markdown_files": 0,
            "files_with_tc_headings": 0,
            "tc_headings_total": 0,
            "parsed_scenarios": 0,
            "fully_structured_cases": 0,
            "needs_normalization_cases": 0,
            "needs_normalization_files": [],
            "excluded_files": [],
            "excluded_files_count": 0,
        }
    for path in sorted(root.rglob("*.md")):
        markdown_files += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative_path = path.relative_to(root).as_posix()
        heading_count = len(SCENARIO_HEADING_RE.findall(text))
        if not heading_count:
            excluded_files.append({"path": relative_path, "reason": "no_tc_heading"})
            continue
        files_with_tc_headings += 1
        tc_headings_total += heading_count
        document = _parse_document(root, path)
        if document is not None:
            documents.append(document)
            if document.needs_normalization_cases:
                documents_missing_fields = sorted(
                    {
                        missing
                        for scenario in document.scenarios
                        for missing in scenario.missing_fields
                    }
                )
                needs_normalization_files.append(
                    {
                        "path": document.relative_path,
                        "cases": document.needs_normalization_cases,
                        "missing_fields": documents_missing_fields,
                    }
                )
    parsed_scenarios = sum(document.total_cases for document in documents)
    needs_normalization_cases = sum(document.needs_normalization_cases for document in documents)
    diagnostics = {
        "markdown_files": markdown_files,
        "files_with_tc_headings": files_with_tc_headings,
        "tc_headings_total": tc_headings_total,
        "parsed_scenarios": parsed_scenarios,
        "fully_structured_cases": max(parsed_scenarios - needs_normalization_cases, 0),
        "needs_normalization_cases": needs_normalization_cases,
        "needs_normalization_files": needs_normalization_files,
        "excluded_files": excluded_files,
        "excluded_files_count": len(excluded_files),
    }
    return documents, diagnostics


def _priority_missing(scenarios: list[TextCaseScenario], priority: str) -> int:
    return sum(1 for item in scenarios if item.priority == priority and not item.automated)


def _rate(value: float) -> str:
    return f"{value:.1%}"


def _status(total: int, automated: int) -> str:
    if automated <= 0:
        return "未开始"
    if automated >= total:
        return "已完成"
    return "部分覆盖"


def _remark(status: str, p0_missing: int, p1_missing: int) -> str:
    if p0_missing > 0:
        return "存在 P0 未自动化场景，优先补齐"
    if p1_missing > 0:
        return "存在 P1 未自动化场景，建议尽快补齐"
    if status == "已完成":
        return "当前场景已全部自动化"
    if status == "部分覆盖":
        return "剩余主要为非 P0/P1 场景"
    return "尚未开始自动化"


def _scenario_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    match = re.search(r"(\d+)", item["tc_id"])
    return (int(match.group(1)) if match else 0, item["tc_id"])


def _group_function_rows(document: TextCaseDocument) -> list[dict[str, Any]]:
    groups: dict[str, list[TextCaseScenario]] = defaultdict(list)
    for scenario in document.scenarios:
        groups[scenario.group_name].append(scenario)

    rows: list[dict[str, Any]] = []
    for group_name, scenarios in groups.items():
        total = len(scenarios)
        automated = sum(1 for item in scenarios if item.automated)
        p0_missing = _priority_missing(scenarios, "P0")
        p1_missing = _priority_missing(scenarios, "P1")
        row_status = _status(total, automated)
        covered = sorted(
            [
                {
                    "tc_id": item.tc_id,
                    "title": item.title,
                    "priority": item.priority,
                    "status": "已自动化",
                    "needs_normalization": item.needs_normalization,
                    "missing_fields": item.missing_fields,
                }
                for item in scenarios
                if item.automated
            ],
            key=_scenario_sort_key,
        )
        uncovered = sorted(
            [
                {
                    "tc_id": item.tc_id,
                    "title": item.title,
                    "priority": item.priority,
                    "status": "未自动化",
                    "needs_normalization": item.needs_normalization,
                    "missing_fields": item.missing_fields,
                }
                for item in scenarios
                if not item.automated
            ],
            key=_scenario_sort_key,
        )
        rows.append(
            {
                "module": document.module_id,
                "feature_name": document.feature_name,
                "feature_display_name": document.feature_display_name,
                "relative_path": document.relative_path,
                "group_name": group_name,
                "status": row_status,
                "total_cases": total,
                "automated_cases": automated,
                "non_automated_cases": max(total - automated, 0),
                "automation_rate": automated / total if total else 0.0,
                "p0_missing": p0_missing,
                "p1_missing": p1_missing,
                "needs_normalization_cases": sum(1 for item in scenarios if item.needs_normalization),
                "remark": _remark(row_status, p0_missing, p1_missing),
                "covered_scenarios": covered,
                "uncovered_scenarios": uncovered,
            }
        )
    rows.sort(
        key=lambda item: (
            STATUS_ORDER[item["status"]],
            -item["p0_missing"],
            -item["p1_missing"],
            item["group_name"],
        )
    )
    return rows


def _scenario_priority_counts(documents: list[TextCaseDocument]) -> tuple[Counter[str], Counter[str]]:
    priority_total: Counter[str] = Counter()
    priority_automated: Counter[str] = Counter()
    for document in documents:
        for scenario in document.scenarios:
            priority_total[scenario.priority] += 1
            if scenario.automated:
                priority_automated[scenario.priority] += 1
    return priority_total, priority_automated


def build_text_case_dashboard(root: Path = DEFAULT_KNOWLEDGE_BASE) -> dict[str, Any]:
    documents, diagnostics = _scan_text_case_documents(root)
    priority_total, priority_automated = _scenario_priority_counts(documents)

    module_rollup: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "feature_pages": 0,
            "function_count": 0,
            "completed_functions": 0,
            "partial_functions": 0,
            "not_started_functions": 0,
            "total_cases": 0,
            "automated_cases": 0,
            "non_automated_cases": 0,
            "p0_missing": 0,
            "p1_missing": 0,
            "needs_normalization_cases": 0,
        }
    )
    function_rows: list[dict[str, Any]] = []
    module_details: dict[str, dict[str, Any]] = defaultdict(lambda: {"feature_pages": []})

    for document in documents:
        group_rows = _group_function_rows(document)
        module_rollup[document.module_id]["feature_pages"] += 1
        module_details[document.module_id]["feature_pages"].append(
            {
                "feature_name": document.feature_name,
                "feature_display_name": document.feature_display_name,
                "relative_path": document.relative_path,
                "total_cases": document.total_cases,
                "automated_cases": document.automated_cases,
                "non_automated_cases": document.non_automated_cases,
                "automation_rate": document.automation_rate,
                "needs_normalization_cases": document.needs_normalization_cases,
                "groups": group_rows,
            }
        )

        for row in group_rows:
            function_rows.append(row)
            module_rollup[row["module"]]["function_count"] += 1
            module_rollup[row["module"]]["completed_functions"] += int(row["status"] == "已完成")
            module_rollup[row["module"]]["partial_functions"] += int(row["status"] == "部分覆盖")
            module_rollup[row["module"]]["not_started_functions"] += int(row["status"] == "未开始")
            module_rollup[row["module"]]["total_cases"] += row["total_cases"]
            module_rollup[row["module"]]["automated_cases"] += row["automated_cases"]
            module_rollup[row["module"]]["non_automated_cases"] += row["non_automated_cases"]
            module_rollup[row["module"]]["p0_missing"] += row["p0_missing"]
            module_rollup[row["module"]]["p1_missing"] += row["p1_missing"]
            module_rollup[row["module"]]["needs_normalization_cases"] += row["needs_normalization_cases"]

    modules: list[dict[str, Any]] = []
    for module_name, stats in module_rollup.items():
        modules.append(
            {
                "module": module_name,
                "feature_pages": stats["feature_pages"],
                "function_count": stats["function_count"],
                "completed_functions": stats["completed_functions"],
                "partial_functions": stats["partial_functions"],
                "not_started_functions": stats["not_started_functions"],
                "total_cases": stats["total_cases"],
                "automated_cases": stats["automated_cases"],
                "non_automated_cases": stats["non_automated_cases"],
                "automation_rate": stats["automated_cases"] / stats["total_cases"] if stats["total_cases"] else 0.0,
                "p0_missing": stats["p0_missing"],
                "p1_missing": stats["p1_missing"],
                "needs_normalization_cases": stats["needs_normalization_cases"],
            }
        )
    modules.sort(key=lambda item: (-item["p0_missing"], -item["p1_missing"], -item["non_automated_cases"], item["module"]))
    function_rows.sort(
        key=lambda item: (
            STATUS_ORDER[item["status"]],
            -item["p0_missing"],
            -item["p1_missing"],
            item["module"],
            item["feature_display_name"],
            item["group_name"],
        )
    )

    total_cases = sum(item.total_cases for item in documents)
    automated_cases = sum(item.automated_cases for item in documents)
    priorities = []
    for priority in PRIORITY_ORDER:
        total = priority_total.get(priority, 0)
        automated = priority_automated.get(priority, 0)
        priorities.append(
            {
                "priority": priority,
                "description": PRIORITY_DESCRIPTIONS[priority],
                "total_cases": total,
                "automated_cases": automated,
                "non_automated_cases": max(total - automated, 0),
                "automation_rate": automated / total if total else 0.0,
            }
        )

    completed_modules = [item["module"] for item in modules if item["partial_functions"] == 0 and item["not_started_functions"] == 0]
    top_gap_modules = [item["module"] for item in modules if item["p0_missing"] > 0 or item["p1_missing"] > 0 or item["non_automated_cases"] > 0][:3]
    focus_rows = [item for item in function_rows if item["non_automated_cases"] > 0][:10]

    for module_name, detail in module_details.items():
        detail["feature_pages"].sort(key=lambda item: (-item["non_automated_cases"], item["feature_display_name"]))
        module_summary = next((item for item in modules if item["module"] == module_name), None)
        detail["summary"] = module_summary

    return {
        "generated_at": utcnow_iso(),
        "knowledge_base_path": str(root),
        "module_count": len(modules),
        "feature_page_count": len(documents),
        "function_count": len(function_rows),
        "total_cases": total_cases,
        "automated_cases": automated_cases,
        "non_automated_cases": max(total_cases - automated_cases, 0),
        "automation_rate": automated_cases / total_cases if total_cases else 0.0,
        "total_p0_missing": sum(item["p0_missing"] for item in function_rows),
        "total_p1_missing": sum(item["p1_missing"] for item in function_rows),
        "completed_modules": completed_modules,
        "top_gap_modules": top_gap_modules,
        "modules": modules,
        "functions": function_rows,
        "focus_rows": focus_rows,
        "priorities": priorities,
        "module_details": module_details,
        "parse_diagnostics": diagnostics,
    }


def _render_main_dashboard(payload: dict[str, Any]) -> str:
    lines = [
        "# 自动化覆盖汇报页",
        "",
        f"- 生成时间：{payload['generated_at']}",
        f"- 文本用例路径：`{payload['knowledge_base_path']}`",
        "",
        "## 一页结论",
        "",
        "| 指标 | 数值 |",
        "| --- | --- |",
        f"| 总模块数 | {payload['module_count']} |",
        f"| 功能页数 | {payload['feature_page_count']} |",
        f"| 功能点数 | {payload['function_count']} |",
        f"| 文本用例总数 | {payload['total_cases']} |",
        f"| 已自动化用例数 | {payload['automated_cases']} |",
        f"| 未自动化用例数 | {payload['non_automated_cases']} |",
        f"| 自动化率 | {_rate(payload['automation_rate'])} |",
        f"| P0 未自动化总数 | {payload['total_p0_missing']} |",
        f"| P1 未自动化总数 | {payload['total_p1_missing']} |",
        "",
        f"- 已完成模块：{'、'.join(payload['completed_modules']) if payload['completed_modules'] else '暂无'}",
        f"- 当前重点关注模块：{'、'.join(payload['top_gap_modules']) if payload['top_gap_modules'] else '暂无'}",
        "",
        "## 模块汇总",
        "",
        "| 模块 | 功能页数 | 功能点数 | 已完成功能点 | 部分覆盖功能点 | 未开始功能点 | 已自动化/总场景 | 自动化率 | P0未自动化 | P1未自动化 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in payload["modules"]:
        lines.append(
            f"| {item['module']} | {item['feature_pages']} | {item['function_count']} | {item['completed_functions']} | "
            f"{item['partial_functions']} | {item['not_started_functions']} | {item['automated_cases']}/{item['total_cases']} | "
            f"{_rate(item['automation_rate'])} | {item['p0_missing']} | {item['p1_missing']} |"
        )

    lines.extend(
        [
            "",
            "## 功能汇总",
            "",
            "| 模块 | 功能页 | 功能点 | 状态 | 已自动化/总场景 | 自动化率 | P0未自动化 | P1未自动化 | 备注 |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for item in payload["functions"]:
        lines.append(
            f"| {item['module']} | {item['feature_display_name']} | {item['group_name']} | {item['status']} | "
            f"{item['automated_cases']}/{item['total_cases']} | {_rate(item['automation_rate'])} | "
            f"{item['p0_missing']} | {item['p1_missing']} | {item['remark']} |"
        )

    lines.extend(
        [
            "",
            "## 重点缺口",
            "",
            "| 模块 | 功能页 | 功能点 | 状态 | 已自动化/总场景 | 自动化率 | P0未自动化 | P1未自动化 |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    if payload["focus_rows"]:
        for item in payload["focus_rows"]:
            lines.append(
                f"| {item['module']} | {item['feature_display_name']} | {item['group_name']} | {item['status']} | "
                f"{item['automated_cases']}/{item['total_cases']} | {_rate(item['automation_rate'])} | "
                f"{item['p0_missing']} | {item['p1_missing']} |"
            )
    else:
        lines.append("| 暂无 | 暂无 | 暂无 | 暂无 | 0/0 | 0.0% | 0 | 0 |")

    lines.extend(
        [
            "",
            "## 重点模块展开",
            "",
        ]
    )
    for module_name in FOCUSED_MODULES:
        detail = payload["module_details"].get(module_name)
        if not detail or not detail.get("feature_pages"):
            continue
        lines.extend(
            [
                f"### {module_name}",
                "",
                f"- 明细文档：`references/dashboard-modules/{module_name}.md`",
                "",
                "| 功能页 | 功能点 | 状态 | 已自动化/总场景 | 自动化率 | P0未自动化 | P1未自动化 |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for feature in detail["feature_pages"]:
            for group in feature["groups"]:
                lines.append(
                    f"| {feature['feature_display_name']} | {group['group_name']} | {group['status']} | "
                    f"{group['automated_cases']}/{group['total_cases']} | {_rate(group['automation_rate'])} | "
                    f"{group['p0_missing']} | {group['p1_missing']} |"
                )
        lines.append("")

    lines.extend(
        [
            "## 优先级汇总",
            "",
            "| 优先级 | 含义 | 总场景数 | 已自动化数 | 未自动化数 | 自动化率 |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in payload["priorities"]:
        lines.append(
            f"| {item['priority']} | {item['description']} | {item['total_cases']} | "
            f"{item['automated_cases']} | {item['non_automated_cases']} | {_rate(item['automation_rate'])} |"
        )
    return "\n".join(lines) + "\n"


def _render_module_detail(module_name: str, payload: dict[str, Any]) -> str:
    detail = payload["module_details"][module_name]
    summary = detail.get("summary") or {
        "feature_pages": len(detail["feature_pages"]),
        "function_count": sum(len(item["groups"]) for item in detail["feature_pages"]),
        "completed_functions": 0,
        "partial_functions": 0,
        "not_started_functions": 0,
        "total_cases": sum(item["total_cases"] for item in detail["feature_pages"]),
        "automated_cases": sum(item["automated_cases"] for item in detail["feature_pages"]),
        "automation_rate": 0.0,
        "p0_missing": 0,
        "p1_missing": 0,
    }
    lines = [
        f"# {module_name} 模块自动化细报",
        "",
        f"- 生成时间：{payload['generated_at']}",
        f"- 文本用例路径：`{payload['knowledge_base_path']}`",
        "",
        "## 模块结论",
        "",
        "| 指标 | 数值 |",
        "| --- | --- |",
        f"| 功能页数 | {summary['feature_pages']} |",
        f"| 功能点数 | {summary['function_count']} |",
        f"| 已完成功能点 | {summary['completed_functions']} |",
        f"| 部分覆盖功能点 | {summary['partial_functions']} |",
        f"| 未开始功能点 | {summary['not_started_functions']} |",
        f"| 已自动化/总场景 | {summary['automated_cases']}/{summary['total_cases']} |",
        f"| 自动化率 | {_rate(summary['automation_rate'])} |",
        f"| P0 未自动化 | {summary['p0_missing']} |",
        f"| P1 未自动化 | {summary['p1_missing']} |",
        "",
    ]

    for feature in detail["feature_pages"]:
        lines.extend(
            [
                f"## {feature['feature_display_name']}",
                "",
                f"- 来源文档：`{feature['relative_path']}`",
                "",
                "| 功能点 | 状态 | 已自动化/总场景 | 自动化率 | P0未自动化 | P1未自动化 | 备注 |",
                "| --- | --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for group in feature["groups"]:
            lines.append(
                f"| {group['group_name']} | {group['status']} | {group['automated_cases']}/{group['total_cases']} | "
                f"{_rate(group['automation_rate'])} | {group['p0_missing']} | {group['p1_missing']} | {group['remark']} |"
            )
        lines.append("")

        for group in feature["groups"]:
            lines.extend(
                [
                    f"### {group['group_name']}",
                    "",
                    f"- 状态：{group['status']}",
                    f"- 已自动化/总场景：{group['automated_cases']}/{group['total_cases']}",
                    f"- 自动化率：{_rate(group['automation_rate'])}",
                    f"- P0 未自动化：{group['p0_missing']}",
                    f"- P1 未自动化：{group['p1_missing']}",
                    "",
                    "#### 已自动化场景",
                    "",
                    "| TC | 场景 | 优先级 |",
                    "| --- | --- | --- |",
                ]
            )
            if group["covered_scenarios"]:
                for item in group["covered_scenarios"]:
                    lines.append(f"| {item['tc_id']} | {item['title']} | {item['priority']} |")
            else:
                lines.append("| 暂无 | 暂无 | 暂无 |")

            lines.extend(
                [
                    "",
                    "#### 未自动化场景",
                    "",
                    "| TC | 场景 | 优先级 |",
                    "| --- | --- | --- |",
                ]
            )
            if group["uncovered_scenarios"]:
                for item in group["uncovered_scenarios"]:
                    lines.append(f"| {item['tc_id']} | {item['title']} | {item['priority']} |")
            else:
                lines.append("| 暂无 | 暂无 | 暂无 |")
            lines.append("")

    return "\n".join(lines) + "\n"


def write_text_case_dashboard(output_path: Path | None = None, root: Path = DEFAULT_KNOWLEDGE_BASE) -> dict[str, Any]:
    payload = build_text_case_dashboard(root)
    output_path = output_path or default_coverage_dashboard_path()
    modules_dir = default_dashboard_modules_dir()
    save_text(output_path, _render_main_dashboard(payload))
    for module_name in payload["module_details"]:
        save_text(modules_dir / f"{module_name}.md", _render_module_detail(module_name, payload))
    payload["dashboard_output"] = str(output_path)
    payload["dashboard_modules_dir"] = str(modules_dir)
    return payload


def handle_dashboard(args: argparse.Namespace) -> int:
    knowledge_base = Path(args.knowledge_base_path) if getattr(args, "knowledge_base_path", None) else DEFAULT_KNOWLEDGE_BASE
    output = Path(args.output) if getattr(args, "output", None) else None
    payload = write_text_case_dashboard(output, knowledge_base)
    print(f"模块数={payload['module_count']}")
    print(f"功能页数={payload['feature_page_count']}")
    print(f"功能点数={payload['function_count']}")
    print(f"文本用例总数={payload['total_cases']}")
    print(f"已自动化={payload['automated_cases']}")
    print(f"未自动化={payload['non_automated_cases']}")
    print(f"自动化率={payload['automation_rate']:.2%}")
    print(f"P0未自动化={payload['total_p0_missing']}")
    print(f"P1未自动化={payload['total_p1_missing']}")
    print(f"dashboard_output={payload['dashboard_output']}")
    print(f"dashboard_modules_dir={payload['dashboard_modules_dir']}")
    return 0
