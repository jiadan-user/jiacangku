from __future__ import annotations

import re
from pathlib import Path

from qa_agent.models import MarkdownCase, MarkdownDocument


CASE_HEADING_RE = re.compile(r"^###\s+(TC[\w-]+)\s*:\s*(.+)$", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)


def _clean_line(line: str) -> str:
    return line.strip().lstrip("-").strip()


def _section_block(chunk: str, heading: str) -> str:
    pattern = re.compile(rf"^####\s+.*?{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(chunk)
    if not match:
        return ""
    start = match.end()
    remainder = chunk[start:]
    next_heading = re.search(r"^####\s+", remainder, re.MULTILINE)
    return remainder[: next_heading.start()] if next_heading else remainder


def _parse_bullets(block: str) -> list[str]:
    lines = []
    for raw in block.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if re.match(r"^\d+\.\s+", stripped):
            lines.append(re.sub(r"^\d+\.\s+", "", stripped))
        elif stripped.startswith("-"):
            lines.append(_clean_line(stripped))
    return lines


def _parse_priority(chunk: str) -> str:
    match = re.search(r"\*\*优先级\*\*:\s*(P[0-3])", chunk, re.IGNORECASE)
    return match.group(1).upper() if match else "P1"


def _parse_test_type(chunk: str) -> str:
    match = re.search(r"\*\*测试类型\*\*:\s*([^\n]+)", chunk)
    return match.group(1).strip() if match else ""


def _parse_ui_automatable(chunk: str) -> bool:
    if "❌ 不可自动化" in chunk:
        return False
    return True


def parse_env_config(markdown_text: str) -> dict[str, str]:
    lines = markdown_text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip().startswith("## 测试环境配置"):
            start = index + 1
            break
    if start is None:
        return {}

    table_lines: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped and table_lines:
            break
        if stripped.startswith("|"):
            table_lines.append(stripped)
        elif table_lines:
            break

    config: dict[str, str] = {}
    for line in table_lines[2:]:
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) >= 2:
            config[parts[0]] = parts[1]
    return config


def parse_markdown_document(path: str | Path) -> MarkdownDocument:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else target.stem
    env_config = parse_env_config(text)

    cases: list[MarkdownCase] = []
    headings = list(CASE_HEADING_RE.finditer(text))
    group_lookup: list[tuple[int, str]] = []
    for match in HEADING_RE.finditer(text):
        heading_text = match.group(2).strip()
        if heading_text not in {"测试用例", "测试概述", "测试环境配置（必填）", "测试环境配置"} and not heading_text.startswith("TC"):
            group_lookup.append((match.start(), heading_text))

    for index, match in enumerate(headings):
        start = match.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        chunk = text[start:end]
        group = ""
        for group_pos, group_name in group_lookup:
            if group_pos < start:
                group = group_name
            else:
                break
        cases.append(
            MarkdownCase(
                tc_id=match.group(1).strip(),
                title=match.group(2).strip(),
                priority=_parse_priority(chunk),
                test_type=_parse_test_type(chunk),
                ui_automatable=_parse_ui_automatable(chunk),
                group=group,
                preconditions=_parse_bullets(_section_block(chunk, "📋 前置条件")),
                steps=_parse_bullets(_section_block(chunk, "🎬 执行步骤")),
                expected=_parse_bullets(_section_block(chunk, "✅ 预期结果")),
            )
        )

    return MarkdownDocument(
        title=title,
        env_config=env_config,
        cases=cases,
        raw_text=text,
        path=str(target),
    )
