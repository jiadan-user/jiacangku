from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from qa_agent.adapters.dedupe_mapper import DedupeMapper
from qa_agent.markdown_cases import parse_markdown_document


SAMPLE_CASES = """# Demo

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
| --- | --- | --- |
| 站点 | ae | site |

## 核心流程

### TC001: 车列表大卡展示

#### 📋 前置条件
- 已进入车列表页

#### 🎬 执行步骤
1. 打开列表页
2. 查看首卡

#### ✅ 预期结果
- 首卡展示为大卡

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化
"""


class MarkdownCasesTests(unittest.TestCase):
    def test_parse_markdown_document_compatible_fields(self) -> None:
        document = parse_markdown_document(SAMPLE_CASES)
        self.assertEqual(document.environment["站点"], "ae")
        self.assertEqual(len(document.cases), 1)
        case = document.cases[0]
        self.assertEqual(case.tc_id, "TC001")
        self.assertTrue(case.ui_automatable)
        self.assertEqual(case.expected, ["首卡展示为大卡"])
        self.assertEqual(case.expected_results, ["首卡展示为大卡"])

    def test_dedupe_mapper_imports_shared_parser(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_doc = root / "cases.md"
            case_doc.write_text(SAMPLE_CASES, encoding="utf-8")
            output = root / "manifest.json"
            entries = DedupeMapper().build_manifest(
                case_doc,
                output,
                module="car",
                site="ae",
                feature_key="列表",
                knowledge_base_root=root / "kb",
                regression_test_root=root / "tests",
            )
            self.assertEqual(len(entries), 1)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
