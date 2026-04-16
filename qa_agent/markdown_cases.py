from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MarkdownCase:
    tc_id: str
    title: str
    group: str = ""
    priority: str = ""
    test_type: str = ""
    ui_automatable: bool = False
    ui_automation_label: str = ""
    preconditions: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    expected: list[str] = field(default_factory=list)
    expected_results: list[str] = field(default_factory=list)
    source_doc: str = ""

    def __post_init__(self) -> None:
        if self.expected and not self.expected_results:
            self.expected_results = list(self.expected)
        if self.expected_results and not self.expected:
            self.expected = list(self.expected_results)


@dataclass
class MarkdownDocument:
    source_doc: str = ""
    environment: dict[str, str] = field(default_factory=dict)
    cases: list[MarkdownCase] = field(default_factory=list)


def parse_markdown_document(path_or_text: str | Path) -> MarkdownDocument:
    source_doc, text = _load_text(path_or_text)
    cases = _parse_cases(text, source_doc)
    return MarkdownDocument(
        source_doc=source_doc,
        environment=parse_environment_config(text),
        cases=cases,
    )


def parse_environment_config(text: str) -> dict[str, str]:
    match = re.search(r"##\s*测试环境配置.*?(?=\n##\s+|\Z)", text or "", flags=re.S)
    if not match:
        return {}
    environment: dict[str, str] = {}
    for line in match.group(0).splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 2:
            continue
        if parts[0] in {"字段", "---", "------"} or parts[0].startswith("---"):
            continue
        environment[parts[0]] = parts[1]
    return environment


def _load_text(path_or_text: str | Path) -> tuple[str, str]:
    if isinstance(path_or_text, Path):
        return str(path_or_text), path_or_text.read_text(encoding="utf-8")
    value = str(path_or_text)
    path = Path(value)
    if path.exists() and path.is_file():
        return str(path), path.read_text(encoding="utf-8")
    return "", value


def _parse_cases(text: str, source_doc: str) -> list[MarkdownCase]:
    pattern = re.compile(r"^###\s*(TC\d+)\s*[:：]\s*(.+)$", flags=re.M)
    matches = list(pattern.finditer(text or ""))
    cases: list[MarkdownCase] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        expected = _extract_case_section(block, "预期结果")
        ui_label = _extract_case_attribute(block, "UI自动化")
        cases.append(
            MarkdownCase(
                tc_id=match.group(1).strip(),
                title=match.group(2).strip(),
                group=_nearest_group(text[: match.start()]),
                priority=_extract_case_attribute(block, "优先级"),
                test_type=_extract_case_attribute(block, "测试类型"),
                ui_automatable=_is_ui_automatable(ui_label),
                ui_automation_label=ui_label,
                preconditions=_extract_case_section(block, "前置条件"),
                steps=_extract_case_section(block, "执行步骤"),
                expected=expected,
                expected_results=expected,
                source_doc=source_doc,
            )
        )
    return cases


def _nearest_group(prefix: str) -> str:
    groups = re.findall(r"^##\s+(.+)$", prefix or "", flags=re.M)
    if not groups:
        return ""
    group = groups[-1].strip()
    return "" if group in {"测试用例", "测试概述", "测试统计"} else group


def _extract_case_attribute(block: str, name: str) -> str:
    match = re.search(rf"-\s*\*\*{re.escape(name)}\*\*:\s*(.+)", block or "")
    return match.group(1).strip() if match else ""


def _is_ui_automatable(value: str) -> bool:
    if not value:
        return False
    return "✅" in value or ("可自动化" in value and "❌" not in value)


def _extract_case_section(block: str, section_name: str) -> list[str]:
    pattern = re.compile(
        rf"####\s*.*?{re.escape(section_name)}\s*(.*?)(?=\n####\s+|\Z)",
        flags=re.S,
    )
    match = pattern.search(block or "")
    if not match:
        return []
    lines: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        stripped = re.sub(r"^\d+\.\s*", "", stripped)
        stripped = re.sub(r"^-\s*", "", stripped)
        if stripped:
            lines.append(stripped)
    return lines
