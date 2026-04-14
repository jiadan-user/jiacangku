from __future__ import annotations

import argparse
import ast
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .catalog import build_catalog, load_catalog
from .common import IDENTIFIER_AUDIT_JSON_PATH, IDENTIFIER_AUDIT_MD_PATH, ROOT_DIR, save_json, save_text, slugify
from .governance import priority_rank
from .models import CatalogCase


PRIORITY_DECORATOR_PATTERN = re.compile(r"pytest\.mark\.(p[0-3])")
CASE_ID_DECORATOR_PATTERN = re.compile(r"pytest\.mark\.(case_id_[A-Za-z0-9_]+)")
TC_PATTERN = re.compile(r"tc[_\-\s]?(\d{1,4})", re.IGNORECASE)
EXPLICIT_PRIORITY_PATTERN = re.compile(r"(?:^|[_\-\s:])p([0-3])(?:[_\-\s:]|$)", re.IGNORECASE)

P0_KEYWORDS = {
    "smoke", "submit", "publish", "post", "success", "login", "logout", "payment",
    "withdraw", "bind", "required", "main", "core", "redirect", "upload",
}
P1_KEYWORDS = {
    "validation", "security", "xss", "sql", "draft", "mandatory", "unauthorized",
    "location", "description", "title", "price", "salary", "category",
}
P2_KEYWORDS = {
    "search", "filter", "sort", "list", "navigation", "pagination", "dropdown",
    "history", "session", "placeholder", "sug", "map", "card", "tab", "city",
    "compatibility", "i18n", "responsive", "tooltip", "badge", "label",
}


@dataclass
class FunctionMeta:
    qualname: str
    name: str
    insert_line: int
    indent: str
    marker_names: set[str]
    docstring: str


def _decorator_name(decorator: ast.expr) -> str:
    try:
        return ast.unparse(decorator)
    except Exception:
        return ""


def _function_meta_for_file(file_path: Path) -> dict[str, FunctionMeta]:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    meta: dict[str, FunctionMeta] = {}

    def walk(node: ast.AST, parents: list[str]) -> None:
        for child in getattr(node, "body", []):
            if isinstance(child, ast.ClassDef):
                walk(child, parents + [child.name])
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test"):
                qualname = "::".join(parents + [child.name]) if parents else child.name
                insert_line = child.decorator_list[0].lineno if child.decorator_list else child.lineno
                marker_names = set()
                for decorator in child.decorator_list:
                    text = _decorator_name(decorator)
                    marker = PRIORITY_DECORATOR_PATTERN.search(text)
                    if marker:
                        marker_names.add(marker.group(1))
                    case_marker = CASE_ID_DECORATOR_PATTERN.search(text)
                    if case_marker:
                        marker_names.add(case_marker.group(1))
                meta[qualname] = FunctionMeta(
                    qualname=qualname,
                    name=child.name,
                    insert_line=insert_line,
                    indent=source.splitlines()[child.lineno - 1][: child.col_offset],
                    marker_names=marker_names,
                    docstring=ast.get_docstring(child) or "",
                )
            elif isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                walk(child, parents)

    walk(tree, [])
    return meta


def _nodeid_qualname(case: CatalogCase) -> str:
    parts = case.nodeid.split("::")[1:]
    return "::".join(parts)


def _extract_tc_number(case: CatalogCase, meta: FunctionMeta | None) -> str | None:
    haystacks = [
        case.nodeid,
        case.allure_title or "",
        case.allure_story or "",
        case.test_name,
        meta.docstring if meta else "",
    ]
    for value in haystacks:
        match = TC_PATTERN.search(value)
        if match:
            return match.group(1).zfill(3)
    return None


def _priority_from_neighbors(case: CatalogCase, file_cases: list[CatalogCase]) -> str | None:
    ordered = sorted(file_cases, key=lambda item: item.nodeid)
    current_index = next((index for index, item in enumerate(ordered) if item.nodeid == case.nodeid), None)
    if current_index is None:
        return None
    nearest: list[tuple[int, str]] = []
    for index, item in enumerate(ordered):
        if item.priority:
            nearest.append((abs(index - current_index), item.priority))
    if not nearest:
        return None
    nearest.sort(key=lambda item: item[0])
    return nearest[0][1]


def _infer_priority(case: CatalogCase, meta: FunctionMeta | None, file_cases: list[CatalogCase]) -> str:
    explicit_priority_sources = [
        case.nodeid,
        case.test_name,
        case.case_id or "",
        case.allure_title or "",
        meta.docstring if meta else "",
    ]
    for value in explicit_priority_sources:
        match = EXPLICIT_PRIORITY_PATTERN.search(value.lower())
        if match:
            return f"p{match.group(1)}"

    neighbor_priority = _priority_from_neighbors(case, file_cases)
    if neighbor_priority:
        return neighbor_priority

    text = " ".join(
        filter(
            None,
            [
                case.nodeid,
                case.allure_title,
                case.allure_story,
                " ".join(case.markers),
                meta.docstring if meta else "",
                case.severity or "",
            ],
        )
    ).lower()

    if "smoke" in text:
        return "p0"
    if case.severity in {"blocker", "critical"} and any(keyword in text for keyword in P0_KEYWORDS):
        return "p0"
    if any(keyword in text for keyword in P0_KEYWORDS):
        return "p1"
    if case.severity in {"blocker", "critical"} or any(keyword in text for keyword in P1_KEYWORDS):
        return "p1"
    if case.severity in {"normal", "minor", "trivial"} or any(keyword in text for keyword in P2_KEYWORDS):
        return "p2"
    return "p3"


def _case_id_prefix_from_neighbors(case: CatalogCase, file_cases: list[CatalogCase]) -> str | None:
    for item in file_cases:
        if item.case_id:
            match = re.match(r"(case_id_[A-Za-z0-9_]+_)(\d{3,4})$", item.case_id)
            if match:
                return match.group(1)
    return None


def _infer_case_id(case: CatalogCase, meta: FunctionMeta | None, file_cases: list[CatalogCase], used_ids: set[str]) -> str:
    tc_number = _extract_tc_number(case, meta)
    prefix = _case_id_prefix_from_neighbors(case, file_cases)
    if not prefix:
        module = slugify(case.module_id or "misc")
        feature = slugify(case.feature_id or Path(case.file_path).stem.replace("test_", ""))
        prefix = f"case_id_{module}_{feature}_"
    if tc_number:
        candidate = f"{prefix}{tc_number}"
        if candidate not in used_ids:
            return candidate

    index = 1
    while True:
        candidate = f"{prefix}{str(index).zfill(3)}"
        if candidate not in used_ids:
            return candidate
        index += 1


def build_identifier_audit() -> dict:
    catalog = load_catalog()
    file_case_map: dict[str, list[CatalogCase]] = defaultdict(list)
    for case in catalog:
        file_case_map[case.file_path].append(case)

    function_meta_cache = {
        file_path: _function_meta_for_file(ROOT_DIR / file_path)
        for file_path in file_case_map
        if (ROOT_DIR / file_path).exists()
    }
    used_case_ids = {case.case_id for case in catalog if case.case_id}
    report_cases = []

    for case in catalog:
        file_cases = file_case_map[case.file_path]
        meta = function_meta_cache.get(case.file_path, {}).get(_nodeid_qualname(case))
        suggested_priority = case.priority or _infer_priority(case, meta, file_cases)
        suggested_case_id = case.case_id or _infer_case_id(case, meta, file_cases, used_case_ids)
        used_case_ids.add(suggested_case_id)

        missing = []
        if not case.priority:
            missing.append("priority")
        if not case.case_id:
            missing.append("case_id")
        if not case.module_id:
            missing.append("module_id")
        if not case.feature_id:
            missing.append("feature_id")

        report_cases.append(
            {
                "file_path": case.file_path,
                "nodeid": case.nodeid,
                "missing": missing,
                "current_priority": case.priority,
                "suggested_priority": suggested_priority,
                "current_case_id": case.case_id,
                "suggested_case_id": suggested_case_id,
                "current_module_id": case.module_id,
                "suggested_module_id": case.module_id,
                "current_feature_id": case.feature_id,
                "suggested_feature_id": case.feature_id,
            }
        )

    return {
        "generated_at": build_catalog()["generated_at"],
        "summary": {
            "missing_priority": sum(1 for item in report_cases if "priority" in item["missing"]),
            "missing_case_id": sum(1 for item in report_cases if "case_id" in item["missing"]),
            "missing_module_id": sum(1 for item in report_cases if "module_id" in item["missing"]),
            "missing_feature_id": sum(1 for item in report_cases if "feature_id" in item["missing"]),
        },
        "cases": report_cases,
    }


def _render_markdown_report(report: dict) -> str:
    lines = [
        "# Identifier Audit",
        "",
        f"- missing_priority: {report['summary']['missing_priority']}",
        f"- missing_case_id: {report['summary']['missing_case_id']}",
        f"- missing_module_id: {report['summary']['missing_module_id']}",
        f"- missing_feature_id: {report['summary']['missing_feature_id']}",
        "",
        "| file | nodeid | missing | suggested_priority | suggested_case_id |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report["cases"]:
        if not item["missing"]:
            continue
        lines.append(
            f"| {item['file_path']} | {item['nodeid']} | {','.join(item['missing'])} | "
            f"{item['suggested_priority'] or '-'} | {item['suggested_case_id'] or '-'} |"
        )
    lines.append("")
    return "\n".join(lines)


def _ensure_pytest_import(lines: list[str]) -> list[str]:
    if any(re.match(r"\s*import pytest\b", line) for line in lines):
        return lines
    insert_at = 0
    for index, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = index + 1
    return lines[:insert_at] + ["import pytest\n"] + lines[insert_at:]


def apply_identifier_fixes(report: dict) -> list[str]:
    file_fixes: dict[str, list[dict]] = defaultdict(list)
    for item in report["cases"]:
        fixes = []
        if "priority" in item["missing"]:
            fixes.append(f"@pytest.mark.{item['suggested_priority']}")
        if "case_id" in item["missing"]:
            fixes.append(f"@pytest.mark.{item['suggested_case_id']}")
        if fixes:
            file_fixes[item["file_path"]].append({"nodeid": item["nodeid"], "decorators": fixes})

    changed_files: list[str] = []
    for file_path, fixes in file_fixes.items():
        absolute_path = ROOT_DIR / file_path
        source = absolute_path.read_text(encoding="utf-8")
        lines = source.splitlines(keepends=True)
        lines = _ensure_pytest_import(lines)
        meta_map = _function_meta_for_file(absolute_path)
        insertions = []
        for fix in fixes:
            qualname = "::".join(fix["nodeid"].split("::")[1:])
            meta = meta_map.get(qualname)
            if not meta:
                continue
            insertions.append((meta.insert_line, meta.indent, fix["decorators"]))

        if not insertions:
            continue

        for insert_line, indent, decorators in sorted(insertions, key=lambda item: item[0], reverse=True):
            rendered = [f"{indent}{decorator}\n" for decorator in decorators]
            lines[insert_line - 1:insert_line - 1] = rendered

        new_source = "".join(lines)
        if new_source != source:
            absolute_path.write_text(new_source, encoding="utf-8")
            changed_files.append(file_path)
    return sorted(changed_files)


def handle_identifier_audit(args: argparse.Namespace) -> int:
    report = build_identifier_audit()
    save_json(Path(args.output_json) if args.output_json else IDENTIFIER_AUDIT_JSON_PATH, report)
    save_text(Path(args.output_md) if args.output_md else IDENTIFIER_AUDIT_MD_PATH, _render_markdown_report(report))

    changed_files: list[str] = []
    if args.apply:
        changed_files = apply_identifier_fixes(report)
        build_catalog()
        report = build_identifier_audit()
        save_json(Path(args.output_json) if args.output_json else IDENTIFIER_AUDIT_JSON_PATH, report)
        save_text(Path(args.output_md) if args.output_md else IDENTIFIER_AUDIT_MD_PATH, _render_markdown_report(report))

    print(f"missing_priority={report['summary']['missing_priority']}")
    print(f"missing_case_id={report['summary']['missing_case_id']}")
    print(f"missing_module_id={report['summary']['missing_module_id']}")
    print(f"missing_feature_id={report['summary']['missing_feature_id']}")
    if changed_files:
        print(f"applied_files={len(changed_files)}")
    return 0
