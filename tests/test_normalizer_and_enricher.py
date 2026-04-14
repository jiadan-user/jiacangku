from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from qa_agent.adapters.script_normalizer import ScriptNormalizer
from qa_agent.adapters.ui_probe_enricher import UIProbeEnricher
from qa_agent.models import CaseManifestEntry


RAW_MD = """# Demo - 测试用例文档

## 测试概述

### 测试目标
- 验证功能

## 测试用例

### TC001: 核心流程成功

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击 Continue

#### ✅ 预期结果
- 成功跳转

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
"""


class EnricherAndNormalizerTests(unittest.TestCase):
    def test_probe_enricher_blocks_without_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            md = Path(tmp) / "raw.md"
            md.write_text(RAW_MD, encoding="utf-8")
            enricher = UIProbeEnricher()
            result = enricher.enrich(run_dir, md)
            self.assertEqual(result["status"], "阻塞")
            checklist = Path(result["probe_checklist_path"])
            self.assertTrue(checklist.exists())

    def test_probe_enricher_creates_enriched_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            md = Path(tmp) / "raw.md"
            md.write_text(RAW_MD, encoding="utf-8")
            probe = Path(tmp) / "probe.json"
            probe.write_text(
                json.dumps(
                    {
                        "page_entries": ["真实入口 https://sg.example.com/jobs"],
                        "field_notes": ["Continue 按钮来自 page.getByRole('button', { name: 'Continue' })"],
                        "success_checks": ["URL 跳转到列表页"],
                        "failure_checks": ["错误提示为 Don't leave this field empty."],
                        "design_diffs": ["Figma 中按钮文案与真实页面略有差异"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            enricher = UIProbeEnricher()
            result = enricher.enrich(run_dir, md, probe)
            text = Path(result["enriched_path"]).read_text(encoding="utf-8")
            self.assertIn("页面入口（MCP实测确认）", text)
            self.assertIn("设计与真实环境差异（MCP实测确认）", text)

    def test_script_normalizer_selects_stateful_and_clamps_waits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "test_demo.py"
            draft.write_text(
                "\n".join(
                    [
                        "import pytest",
                        "import allure",
                        "from utils.logger import setup_logger",
                        "",
                        "logger = setup_logger()",
                        "",
                        '_CONFIG = {"site": "sg", "base_url": "https://sg.example.com"}',
                        "",
                        "@pytest.mark.case_id_demo",
                        "@pytest.mark.p0",
                        "@pytest.mark.demo",
                        "@pytest.mark.sg",
                        '@allure.feature("OK")',
                        '@allure.story("demo")',
                        '@allure.title("核心流程成功")',
                        "def test_demo(page, config):",
                        '    """TC001: 核心流程成功"""',
                        "    page.wait_for_timeout(1200)",
                        "    assert True",
                    ]
                ),
                encoding="utf-8",
            )
            entry = CaseManifestEntry(
                tc_id="TC001",
                title="核心流程成功",
                module="demo",
                site="sg",
                feature_key="demo",
                source_doc="demo.md",
                priority="P0",
                test_type="功能测试",
                ui_automatable=True,
                generated_case_id="case_id_demo",
                status="新增候选",
            )
            normalizer = ScriptNormalizer(max_wait_ms=300)
            normalized = normalizer.normalize(
                draft_paths=[str(draft)],
                entries=[entry],
                output_dir=Path(tmp) / "normalized",
                env_config={
                    "site": "sg",
                    "role": "seller",
                    "user_name": "demo",
                    "base_url": "https://sg.example.com",
                    "test_account": {"username": "demo@example.com", "password": "x"},
                },
            )
            text = Path(list(normalized.values())[0]).read_text(encoding="utf-8")
            self.assertIn("def prepared_page", text)
            self.assertIn("已从 1200ms 规范化", text)


if __name__ == "__main__":
    unittest.main()
