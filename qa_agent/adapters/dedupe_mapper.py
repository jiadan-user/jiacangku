from __future__ import annotations

import difflib
import re
from pathlib import Path

from qa_agent.io import write_json
from qa_agent.markdown_cases import parse_markdown_document
from qa_agent.models import CaseManifestEntry, CaseStatus
from qa_agent.utils import normalize_text, slugify


class DedupeMapper:
    def build_manifest(
        self,
        enriched_markdown_path: str | Path,
        output_path: str | Path,
        module: str,
        site: str,
        feature_key: str,
        knowledge_base_root: str | Path,
        regression_test_root: str | Path,
    ) -> list[CaseManifestEntry]:
        document = parse_markdown_document(enriched_markdown_path)
        existing_docs = self._index_markdown_docs(Path(knowledge_base_root))
        existing_scripts = self._index_python_scripts(Path(regression_test_root))
        entries: list[CaseManifestEntry] = []
        for case in document.cases:
            generated_case_id = self._stable_case_id(module, case.tc_id, case.title)
            existing_doc_key = self._find_duplicate(case, module, site, existing_docs)
            existing_script_key, regen_required = self._find_script_match(case, module, site, existing_scripts)
            if not case.ui_automatable:
                status = CaseStatus.NON_AUTOMATABLE.value
                rationale = "用例标记为不可自动化"
            elif existing_script_key and regen_required:
                status = CaseStatus.REGEN_REQUIRED.value
                rationale = f"已有近似脚本但断言或行为变化: {existing_script_key}"
            elif existing_script_key or existing_doc_key:
                status = CaseStatus.EXISTING_AUTOMATED.value
                rationale = f"已存在脚本/知识库资产: {existing_script_key or existing_doc_key}"
            else:
                status = CaseStatus.NEW_CANDIDATE.value
                rationale = "未命中现有脚本或文本资产"
            entries.append(
                CaseManifestEntry(
                    tc_id=case.tc_id,
                    title=case.title,
                    module=module,
                    site=site,
                    feature_key=feature_key,
                    source_doc=str(enriched_markdown_path),
                    priority=case.priority,
                    test_type=case.test_type,
                    ui_automatable=case.ui_automatable,
                    generated_case_id=generated_case_id,
                    status=status,
                    group=case.group,
                    target_script_path=f"test_cases/{module}/test_{module}_{slugify(feature_key)}.py",
                    duplicate_of=existing_script_key or existing_doc_key or "",
                    rationale=rationale,
                )
            )
        write_json(output_path, [entry.__dict__ for entry in entries])
        return entries

    def _index_markdown_docs(self, root: Path) -> list[tuple[str, str]]:
        indexed: list[tuple[str, str]] = []
        if not root.exists():
            return indexed
        for path in sorted(root.rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            indexed.append((str(path), normalize_text(text)))
        return indexed

    def _index_python_scripts(self, root: Path) -> list[tuple[str, str]]:
        indexed: list[tuple[str, str]] = []
        if not root.exists():
            return indexed
        for path in sorted(root.rglob("test_*.py")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            titles = re.findall(r'@allure\.title\("([^"]+)"\)', text)
            body = " ".join(titles) if titles else text
            indexed.append((str(path), normalize_text(body)))
        return indexed

    def _find_duplicate(self, case, module: str, site: str, existing_docs: list[tuple[str, str]]) -> str:
        signature = self._signature(case, module, site)
        for path, text in existing_docs:
            if self._similarity(signature, text) >= 0.92:
                return path
        return ""

    def _find_script_match(self, case, module: str, site: str, existing_scripts: list[tuple[str, str]]) -> tuple[str, bool]:
        title_sig = normalize_text(case.title)
        full_sig = self._signature(case, module, site)
        for path, text in existing_scripts:
            if title_sig and title_sig in text:
                return path, False
            title_score = self._similarity(title_sig, text)
            full_score = self._similarity(full_sig, text)
            if full_score >= 0.92:
                return path, False
            if title_score >= 0.85:
                return path, True
        return "", False

    def _signature(self, case, module: str, site: str) -> str:
        return normalize_text(
            " ".join(
                [
                    module,
                    site,
                    case.title,
                    " ".join(case.steps[:3]),
                    " ".join(case.expected[:2]),
                ]
            )
        )

    def _stable_case_id(self, module: str, tc_id: str, title: str) -> str:
        return f"case_id_{slugify(module)}_{slugify(tc_id)}_{slugify(title)[:32]}"

    def _similarity(self, left: str, right: str) -> float:
        return difflib.SequenceMatcher(a=left, b=right).ratio()
