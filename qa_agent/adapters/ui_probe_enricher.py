from __future__ import annotations

import json
from pathlib import Path

from qa_agent.io import write_json, write_text
from qa_agent.markdown_cases import parse_markdown_document


REQUIRED_HEADINGS = [
    "页面入口（MCP实测确认）",
    "页面字段说明（MCP录制确认）",
    "成功验证（MCP实测确认）",
    "失败验证（MCP实测确认）",
    "设计与真实环境差异（MCP实测确认）",
]


class UIProbeEnricher:
    def enrich(
        self,
        run_dir: Path,
        raw_markdown_path: str | Path,
        probe_notes_path: str | Path | None = None,
    ) -> dict[str, str]:
        raw_path = Path(raw_markdown_path)
        text = raw_path.read_text(encoding="utf-8")
        output_dir = run_dir / "cases"
        output_dir.mkdir(parents=True, exist_ok=True)
        enriched_path = output_dir / "testcases_enriched.md"
        reality_diff_path = output_dir / "reality_diff.json"
        checklist_path = output_dir / "probe_checklist.md"

        if self.is_enriched(text):
            write_text(enriched_path, text)
            write_json(reality_diff_path, {"status": "原文已增强", "differences": []})
            return {"status": "完成", "enriched_path": str(enriched_path), "reality_diff_path": str(reality_diff_path)}

        if not probe_notes_path:
            document = parse_markdown_document(raw_path)
            write_text(checklist_path, self._build_checklist(document))
            return {"status": "阻塞", "probe_checklist_path": str(checklist_path)}

        probe_payload = self._load_probe_notes(Path(probe_notes_path))
        enriched_text = self._inject_probe_sections(text, probe_payload)
        write_text(enriched_path, enriched_text)
        write_json(reality_diff_path, {"status": "已补充增强", "probe_notes_path": str(probe_notes_path), "differences": probe_payload})
        return {"status": "完成", "enriched_path": str(enriched_path), "reality_diff_path": str(reality_diff_path)}

    def is_enriched(self, markdown_text: str) -> bool:
        return all(heading in markdown_text for heading in REQUIRED_HEADINGS)

    def _load_probe_notes(self, path: Path) -> dict[str, object]:
        if path.suffix == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        return {
            "page_entries": [path.read_text(encoding="utf-8")],
            "field_notes": [],
            "success_checks": [],
            "failure_checks": [],
            "design_diffs": [],
        }

    def _inject_probe_sections(self, text: str, payload: dict[str, object]) -> str:
        sections = [
            "",
            "### 页面入口（MCP实测确认）",
            *self._as_bullets(payload.get("page_entries")),
            "",
            "### 页面字段说明（MCP录制确认）",
            *self._as_bullets(payload.get("field_notes")),
            "",
            "### 成功验证（MCP实测确认）",
            *self._as_bullets(payload.get("success_checks")),
            "",
            "### 失败验证（MCP实测确认）",
            *self._as_bullets(payload.get("failure_checks")),
            "",
            "### 设计与真实环境差异（MCP实测确认）",
            *self._as_bullets(payload.get("design_diffs")),
            "",
        ]
        if "## 测试用例" in text:
            return text.replace("## 测试用例", "\n".join(sections) + "\n## 测试用例", 1)
        return text.rstrip() + "\n\n" + "\n".join(sections)

    def _as_bullets(self, value: object | None) -> list[str]:
        if not value:
            return ["- 待补充"]
        if isinstance(value, list):
            return [f"- {item}" for item in value]
        return [f"- {value}"]

    def _build_checklist(self, document) -> str:
        lines = [
            "# UI Probe 检查清单",
            "",
            f"文档: {document.path}",
            "",
            "补充以下真实环境信息后，再继续录制流程：",
            "",
            "## 页面入口（MCP实测确认）",
            "- 真实入口 URL",
            "- 登录前/登录后跳转行为",
            "",
            "## 页面字段说明（MCP录制确认）",
            "- 关键字段",
            "- 选择器来源",
            "- 必填/选填与交互行为",
            "",
            "## 成功验证（MCP实测确认）",
            "- 成功态 URL / 文案 / 元素",
            "",
            "## 失败验证（MCP实测确认）",
            "- 错误态 URL / 文案 / 元素",
            "",
            "## 设计与真实环境差异（MCP实测确认）",
            "- Figma 与真实页面不一致项",
            "",
            "## 用例清单",
        ]
        for case in document.cases:
            lines.append(f"- {case.tc_id}: {case.title}")
        return "\n".join(lines) + "\n"
