from __future__ import annotations

import argparse
import ast
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
KB_ROOT = ROOT / "bundled" / "knowledge_base" / "文本用例"
TEST_CASES_ROOT = (
    ROOT
    / "bundled"
    / "skills"
    / "ok_autotest_ui_skill"
    / "bundled"
    / "ok_autotest_ui_pc"
    / "test_cases"
)
REPORT_DIR = ROOT / ".qa_agent"

HEADING_RE = re.compile(r"^(?P<hash>#{2,6})\s+(?P<title>.+)$")
TC_TOKEN_RE = re.compile(r"\bTC[-_A-Za-z]*\d+[A-Za-z0-9_-]*\b", re.IGNORECASE)
TEST_TC_RE = re.compile(r"\btest_tc(?P<num>\d+[A-Za-z0-9_]*)\b", re.IGNORECASE)
PRIORITY_MARK_RE = re.compile(r"pytest\.mark\.([pP][0-3])\b")
SKIP_RE = re.compile(r"pytest\.mark\.skip\((?P<body>.*?)\)", re.DOTALL)
DOC_RE = re.compile(r"录制文档\s*[:：]\s*(?P<doc>[^\n\r]+\.md)")

FIELD_PRIORITY_RE = re.compile(r"(?P<prefix>\*\*)优先级(?P<suffix>\*\*\s*[:：]\s*)(?P<value>P[0-3])", re.IGNORECASE)
FIELD_UI_RE = re.compile(
    r"(?P<prefix>\*\*)(?P<label>UI\s*自动化|自动化可行性|是否自动化|自动化)(?P<suffix>\*\*\s*[:：]\s*)(?P<value>[^\n\r|]+)",
    re.IGNORECASE,
)


@dataclass
class Evidence:
    doc_rel: str
    tc_key: str
    priority: str | None
    automatable: bool | None
    script_path: str
    test_name: str
    raw_tc: str


@dataclass
class OrderedEvidence:
    priority: str | None
    automatable: bool | None
    script_path: str
    test_name: str


SCRIPT_DOC_OVERRIDES = {
    "property_list/test_au58_property_list_card_property_type_buy.py": "property_list/au58-Property-列表卡片房产类型功能测试用例-买房.md",
    "property_list/test_au58_property_list_card_property_type_commercial_buy.py": "property_list/au58-Property-列表卡片房产类型功能测试用例-商业买房.md",
    "property_list/test_au58_property_list_card_property_type_commercial_rent.py": "property_list/au58-Property-列表卡片房产类型功能测试用例-商业租房.md",
    "property_list/test_au58_property_list_card_property_type_student.py": "property_list/au58-Property-列表卡片房产类型功能测试用例-学生公寓.md",
    "property_list/test_au58_property_list_sort_pagination_commercial_rent.py": "property_list/au58-Property-列表卡片排列翻页功能测试用例-商业租房.md",
    "property_list/test_au58_property_map_card_count.py": "property_list/au58-Property-地图模式卡片数量功能测试用例.md",
    "property_list/test_au58_property_map_pin_count.py": "property_list/au58-Property-地图模式房源点数量功能测试用例.md",
    "property_list/test_au58_property_map_geolocation_permission.py": "property_list/au58-Property-地图授权定位功能测试用例.md",
}


@dataclass
class TcBlock:
    tc_id: str
    start: int
    end: int
    heading_line: int
    text: str


@dataclass
class Report:
    updated_files: dict[str, dict[str, int]] = field(default_factory=dict)
    matched_evidence: int = 0
    unmatched_evidence: list[dict[str, str]] = field(default_factory=list)
    conflicts: list[dict[str, str]] = field(default_factory=list)
    ambiguous: list[dict[str, str]] = field(default_factory=list)

    def add_update(self, path: str, key: str, count: int = 1) -> None:
        self.updated_files.setdefault(path, defaultdict(int))[key] += count

    def to_jsonable(self) -> dict[str, object]:
        return {
            "updated_files": {path: dict(stats) for path, stats in sorted(self.updated_files.items())},
            "matched_evidence": self.matched_evidence,
            "unmatched_evidence": self.unmatched_evidence,
            "conflicts": self.conflicts,
            "ambiguous": self.ambiguous,
        }


def tc_key(value: str) -> str:
    compact = re.sub(r"[^A-Za-z0-9]", "", value).upper()
    if compact.startswith("TC"):
        compact = compact[2:]
    return compact


def tc_number_key(value: str) -> str | None:
    matches = re.findall(r"\d+", value)
    if not matches:
        return None
    return matches[-1].zfill(3)


def infer_automatable(decorator_text: str) -> bool | None:
    skip = SKIP_RE.search(decorator_text)
    if skip:
        reason = skip.group("body")
        if any(token in reason for token in ("不需要自动化", "不自动化", "不可自动化", "手动", "manual", "跳过自动化", "预期不一致", "免登录态")):
            return False
        return None
    return True


def extract_tc_tokens(text: str) -> set[str]:
    tokens = {m.group(0) for m in TC_TOKEN_RE.finditer(text)}
    for match in TEST_TC_RE.finditer(text):
        tokens.add(f"TC{match.group('num')}")
    return tokens


def unique_by_basename(paths: Iterable[Path]) -> dict[str, str]:
    bucket: dict[str, list[Path]] = defaultdict(list)
    for path in paths:
        bucket[path.name].append(path)
    result: dict[str, str] = {}
    for name, items in bucket.items():
        if len(items) == 1:
            result[name] = items[0].relative_to(KB_ROOT).as_posix()
    return result


def target_docs_for_script(script_rel: str, module_doc: str | None, basename_map: dict[str, str]) -> list[str]:
    targets: set[str] = set()
    if script_rel in SCRIPT_DOC_OVERRIDES:
        targets.add(SCRIPT_DOC_OVERRIDES[script_rel])
    if module_doc:
        doc_name = Path(module_doc).name.strip()
        if doc_name in basename_map:
            targets.add(basename_map[doc_name])

    if script_rel.startswith("property_basics/list/"):
        targets.add("Property/Basic/List/property_basics-list-用例汇总.md")
    elif script_rel.startswith("property_basics/map/"):
        targets.add("Property/Basic/Map/property_basics-map-用例汇总.md")
    elif script_rel.startswith("Settings/"):
        targets.add("Tiyan/Settings/OK-AE-Settings模块-测试用例-20260414.md")

    return sorted(targets)


def collect_script_evidence() -> tuple[dict[str, dict[str, list[Evidence]]], dict[str, list[OrderedEvidence]], Report]:
    report = Report()
    basename_map = unique_by_basename(KB_ROOT.rglob("*.md"))
    evidence_by_doc: dict[str, dict[str, list[Evidence]]] = defaultdict(lambda: defaultdict(list))
    ordered_by_doc: dict[str, list[OrderedEvidence]] = defaultdict(list)

    for script in sorted(TEST_CASES_ROOT.rglob("test*.py")):
        text = script.read_text(encoding="utf-8", errors="ignore")
        script_rel = script.relative_to(TEST_CASES_ROOT).as_posix()
        module_doc_match = DOC_RE.search(text)
        module_doc = module_doc_match.group("doc") if module_doc_match else None
        target_docs = target_docs_for_script(script_rel, module_doc, basename_map)
        if not target_docs:
            continue

        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            report.conflicts.append({"path": script_rel, "reason": f"script_parse_failed: {exc}"})
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith("test"):
                continue
            decorators = "\n".join(ast.get_source_segment(text, deco) or "" for deco in node.decorator_list)
            docstring = ast.get_docstring(node, clean=False) or ""
            # Only use identifiers attached to the test itself. The body often
            # references other TC ids in comments or fallback messages, which is
            # useful for humans but too noisy for one-to-one evidence mapping.
            raw_text = "\n".join([decorators, docstring, node.name])
            tc_tokens = extract_tc_tokens(raw_text)
            if not tc_tokens:
                continue

            priority: str | None = None
            for match in PRIORITY_MARK_RE.finditer(decorators):
                priority = match.group(1).upper()
                break
            automatable = infer_automatable(decorators)
            for doc_rel in target_docs:
                ordered_by_doc[doc_rel].append(
                    OrderedEvidence(
                        priority=priority,
                        automatable=automatable,
                        script_path=script_rel,
                        test_name=node.name,
                    )
                )

            for doc_rel in target_docs:
                for token in tc_tokens:
                    keys = {tc_key(token)}
                    num_key = tc_number_key(token)
                    if num_key:
                        keys.add(num_key)
                    for key in keys:
                        evidence_by_doc[doc_rel][key].append(
                            Evidence(
                                doc_rel=doc_rel,
                                tc_key=key,
                                priority=priority,
                                automatable=automatable,
                                script_path=script_rel,
                                test_name=node.name,
                                raw_tc=token,
                            )
                        )
    return evidence_by_doc, ordered_by_doc, report


def parse_tc_blocks(text: str) -> list[TcBlock]:
    lines = text.splitlines(keepends=True)
    starts: list[tuple[int, int, str]] = []
    offset = 0
    for idx, line in enumerate(lines):
        match = HEADING_RE.match(line.rstrip("\n"))
        if match:
            tc_match = TC_TOKEN_RE.search(match.group("title"))
            if tc_match:
                starts.append((offset, idx, tc_match.group(0)))
        offset += len(line)

    blocks: list[TcBlock] = []
    for pos, (start, line_no, raw_tc) in enumerate(starts):
        end = starts[pos + 1][0] if pos + 1 < len(starts) else len(text)
        blocks.append(TcBlock(tc_id=raw_tc, start=start, end=end, heading_line=line_no, text=text[start:end]))
    return blocks


def choose_evidence(
    candidates: list[Evidence],
) -> tuple[str | None, bool | None, Evidence | None, str | None, str | None]:
    if not candidates:
        return None, None, None, None, None
    priorities = sorted({item.priority for item in candidates if item.priority})
    autos = sorted({item.automatable for item in candidates if item.automatable is not None})
    priority = priorities[0] if len(priorities) == 1 else None
    automatable = autos[0] if len(autos) == 1 else None
    priority_conflict = f"priority_conflict: {priorities}" if len(priorities) > 1 else None
    automation_conflict = f"automation_conflict: {autos}" if len(autos) > 1 else None
    return priority, automatable, candidates[0], priority_conflict, automation_conflict


def field_ui_value(block: str) -> bool | None:
    match = FIELD_UI_RE.search(block)
    if not match:
        return None
    value = re.sub(r"\s+", "", match.group("value"))
    if any(token in value for token in ("不可自动化", "未自动化", "不适合自动化")) or value.startswith("❌"):
        return False
    if "可自动化" in value or "已自动化" in value or value.startswith("✅") or value.startswith("⚠"):
        return True
    return None


def standardize_labels(text: str) -> str:
    text = re.sub(r"(\*\*)UI\s+自动化(\*\*\s*[:：])", r"\1UI自动化\2", text, flags=re.IGNORECASE)
    return re.sub(r"(\*\*)自动化(\*\*\s*[:：])", r"\1UI自动化\2", text)


def update_tc_blocks(path_rel: str, text: str, evidence: dict[str, list[Evidence]], report: Report) -> str:
    text = standardize_labels(text)
    blocks = parse_tc_blocks(text)
    replacements: list[tuple[int, int, str]] = []

    for block in blocks:
        if re.search(r"[~～]", block.tc_id + block.text) and re.search(r"^\|\s*TC", block.text, re.MULTILINE):
            continue
        keys = {tc_key(block.tc_id)}
        num_key = tc_number_key(block.tc_id)
        if num_key:
            keys.add(num_key)
        candidates: list[Evidence] = []
        for key in keys:
            candidates.extend(evidence.get(key, []))
        priority, automatable, sample, priority_conflict, automation_conflict = choose_evidence(candidates)
        if not sample:
            continue
        report.matched_evidence += 1
        if automation_conflict:
            report.conflicts.append({"path": path_rel, "tc": block.tc_id, "reason": automation_conflict})

        block_text = block.text
        inserts: list[str] = []
        priority_match = FIELD_PRIORITY_RE.search(block_text)
        if not priority_match and priority:
            inserts.append(f"**优先级**：{priority}")
            report.add_update(path_rel, "priority_added")
        elif not priority_match and priority_conflict:
            report.conflicts.append({"path": path_rel, "tc": block.tc_id, "reason": priority_conflict})

        ui_match = FIELD_UI_RE.search(block_text)
        current_ui = field_ui_value(block_text)
        if automatable is not None and not automation_conflict:
            if not ui_match:
                if automatable:
                    inserts.append(f"**UI自动化**：✅ 可自动化（已匹配自动化脚本：`{sample.script_path}::{sample.test_name}`）")
                else:
                    inserts.append(f"**UI自动化**：❌ 不可自动化（脚本标记为跳过/手动：`{sample.script_path}::{sample.test_name}`）")
                report.add_update(path_rel, "ui_added")
            elif current_ui is False and automatable is True:
                new_block_text = FIELD_UI_RE.sub(
                    lambda m: f"{m.group('prefix')}UI自动化{m.group('suffix')}✅ 可自动化（已匹配自动化脚本：`{sample.script_path}::{sample.test_name}`）",
                    block_text,
                    count=1,
                )
                block_text = new_block_text
                report.add_update(path_rel, "ui_corrected_from_false")

        if inserts:
            lines = block_text.splitlines(keepends=True)
            insert_at = 1
            while insert_at < len(lines) and not lines[insert_at].strip():
                insert_at += 1
            insert_text = "".join(line if line.endswith("\n") else line + "\n" for line in inserts) + "\n"
            lines.insert(insert_at, insert_text)
            block_text = "".join(lines)

        if block_text != block.text:
            replacements.append((block.start, block.end, block_text))

    for start, end, replacement in reversed(replacements):
        text = text[:start] + replacement + text[end:]
    return text


def update_tc_tables(path_rel: str, text: str, evidence: dict[str, list[Evidence]], report: Report) -> str:
    lines = text.splitlines()
    output: list[str] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if not (line.strip().startswith("|") and line.strip().endswith("|")):
            output.append(line)
            idx += 1
            continue

        table: list[str] = []
        while idx < len(lines) and lines[idx].strip().startswith("|") and lines[idx].strip().endswith("|"):
            table.append(lines[idx])
            idx += 1

        if len(table) < 3:
            output.extend(table)
            continue

        rows = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in table]
        header = rows[0]
        separator = rows[1]
        data = rows[2:]
        tc_col = next((i for i, name in enumerate(header) if name in {"编号", "TC", "用例编号"}), 0)
        if not any(tc_col < len(row) and TC_TOKEN_RE.search(row[tc_col]) for row in data):
            output.extend(table)
            continue
        if any("UI自动化" in name or name == "自动化" for name in header):
            output.extend(table)
            continue

        new_rows: list[list[str]] = []
        changed = False
        for row in data:
            if tc_col >= len(row):
                new_rows.append(row)
                continue
            tc_match = TC_TOKEN_RE.search(row[tc_col])
            if not tc_match:
                new_rows.append(row)
                continue
            keys = {tc_key(tc_match.group(0))}
            num_key = tc_number_key(tc_match.group(0))
            if num_key:
                keys.add(num_key)
            candidates: list[Evidence] = []
            for key in keys:
                candidates.extend(evidence.get(key, []))
            priority, automatable, sample, priority_conflict, automation_conflict = choose_evidence(candidates)
            value = "待补齐"
            if sample and automation_conflict:
                report.conflicts.append({"path": path_rel, "tc": tc_match.group(0), "reason": automation_conflict})
            elif sample and automatable is True:
                value = "✅ 可自动化"
                changed = True
            elif sample and automatable is False:
                value = "❌ 不可自动化"
                changed = True
            new_rows.append([*row, value])

        if not changed:
            output.extend(table)
            continue

        header = [*header, "UI自动化"]
        separator = [*separator, "---"]
        rendered = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(separator) + " |",
        ]
        rendered.extend("| " + " | ".join(row) + " |" for row in new_rows)
        output.extend(rendered)
        report.add_update(path_rel, "table_ui_column_added")

    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def update_automation_summary_tables(path_rel: str, text: str, report: Report) -> str:
    if not path_rel.startswith("Property/Basic/") or "自动化用例汇总" not in text[:200]:
        return text
    lines = text.splitlines()
    output: list[str] = []
    idx = 0
    changed_tables = 0
    while idx < len(lines):
        line = lines[idx]
        if not (line.strip().startswith("|") and line.strip().endswith("|")):
            output.append(line)
            idx += 1
            continue

        table: list[str] = []
        while idx < len(lines) and lines[idx].strip().startswith("|") and lines[idx].strip().endswith("|"):
            table.append(lines[idx])
            idx += 1

        if len(table) < 3:
            output.extend(table)
            continue
        rows = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in table]
        header = rows[0]
        separator = rows[1]
        data = rows[2:]
        tc_col = next((i for i, name in enumerate(header) if name in {"编号", "TC", "用例编号"}), 0)
        if not any(tc_col < len(row) and TC_TOKEN_RE.search(row[tc_col]) for row in data):
            output.extend(table)
            continue
        if any("UI自动化" in name or name == "自动化" for name in header):
            output.extend(table)
            continue

        header = [*header, "UI自动化"]
        separator = [*separator, "---"]
        rendered = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(separator) + " |",
        ]
        rendered.extend("| " + " | ".join([*row, "✅ 可自动化"]) + " |" for row in data)
        output.extend(rendered)
        changed_tables += 1

    if changed_tables:
        report.add_update(path_rel, "automation_summary_table_ui_column_added", changed_tables)
    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def update_tc_blocks_by_order(
    path_rel: str,
    text: str,
    ordered_evidence: list[OrderedEvidence],
    report: Report,
) -> str:
    blocks = [block for block in parse_tc_blocks(text) if not re.search(r"[~～]", block.text)]
    if not ordered_evidence or len(blocks) != len(ordered_evidence):
        return text

    replacements: list[tuple[int, int, str]] = []
    for block, evidence in zip(blocks, ordered_evidence):
        block_text = block.text
        inserts: list[str] = []
        priority_match = FIELD_PRIORITY_RE.search(block_text)
        if not priority_match and evidence.priority:
            inserts.append(f"**优先级**：{evidence.priority}")
            report.add_update(path_rel, "priority_added_by_order")
        ui_match = FIELD_UI_RE.search(block_text)
        current_ui = field_ui_value(block_text)
        if evidence.automatable is not None:
            if not ui_match:
                value = "✅ 可自动化" if evidence.automatable else "❌ 不可自动化"
                inserts.append(f"**UI自动化**：{value}（按脚本顺序匹配：`{evidence.script_path}::{evidence.test_name}`）")
                report.add_update(path_rel, "ui_added_by_order")
            elif current_ui is False and evidence.automatable is True:
                block_text = FIELD_UI_RE.sub(
                    lambda m: f"{m.group('prefix')}UI自动化{m.group('suffix')}✅ 可自动化（按脚本顺序匹配：`{evidence.script_path}::{evidence.test_name}`）",
                    block_text,
                    count=1,
                )
                report.add_update(path_rel, "ui_corrected_from_false_by_order")
        if inserts:
            lines = block_text.splitlines(keepends=True)
            insert_at = 1
            while insert_at < len(lines) and not lines[insert_at].strip():
                insert_at += 1
            insert_text = "".join(line if line.endswith("\n") else line + "\n" for line in inserts) + "\n"
            lines.insert(insert_at, insert_text)
            block_text = "".join(lines)
        if block_text != block.text:
            replacements.append((block.start, block.end, block_text))

    for start, end, replacement in reversed(replacements):
        text = text[:start] + replacement + text[end:]
    return text


def normalize(dry_run: bool = False) -> Report:
    evidence_by_doc, ordered_by_doc, report = collect_script_evidence()

    for path_rel, evidence in sorted(evidence_by_doc.items()):
        path = KB_ROOT / path_rel
        if not path.exists():
            for items in evidence.values():
                for item in items:
                    report.unmatched_evidence.append(
                        {"path": item.script_path, "tc": item.raw_tc, "reason": f"target_doc_missing:{path_rel}"}
                    )
            continue
        original = path.read_text(encoding="utf-8", errors="ignore")
        updated = update_automation_summary_tables(path_rel, original, report)
        updated = update_tc_tables(path_rel, updated, evidence, report)
        updated = update_tc_blocks(path_rel, updated, evidence, report)
        updated = update_tc_blocks_by_order(path_rel, updated, ordered_by_doc.get(path_rel, []), report)
        if updated != original and not dry_run:
            path.write_text(updated, encoding="utf-8")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Use UI automation scripts as evidence to normalize text case metadata.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", default=str(REPORT_DIR / "coverage_normalization_report.json"))
    args = parser.parse_args()

    report = normalize(dry_run=args.dry_run)
    payload = report.to_jsonable()
    report_path = Path(args.report)
    if not args.dry_run:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
