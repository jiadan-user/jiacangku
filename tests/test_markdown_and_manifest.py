from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from qa_agent.adapters.dedupe_mapper import DedupeMapper
from qa_agent.markdown_cases import parse_markdown_document


SAMPLE_MD = """# 示例功能 - 测试用例文档

## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | sg | 新加坡站 |
| 基础URL | https://sg.example.com | 测试站点地址 |
| 角色 | seller | seller角色 |
| 账号名称 | demo_sg | 用于 session 命名 |
| 测试账号 | test@example.com | 登录邮箱 |
| 测试密码 | Secret123 | 登录密码 |

## 测试用例

## 正向场景

### TC001: 提交成功应跳转列表页

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 点击 Continue

#### ✅ 预期结果
- 页面跳转到列表页

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 功能测试
- **UI自动化**: ✅ 可自动化

### TC002: 空表单提交应提示错误

#### 📋 前置条件
- 已登录

#### 🎬 执行步骤
1. 直接点击 Continue

#### ✅ 预期结果
- 显示错误提示

#### 📊 用例属性
- **优先级**: P1
- **测试类型**: 异常测试
- **UI自动化**: ✅ 可自动化
"""


class MarkdownAndManifestTests(unittest.TestCase):
    def test_parse_markdown_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.md"
            path.write_text(SAMPLE_MD, encoding="utf-8")
            document = parse_markdown_document(path)
            self.assertEqual(document.env_config["站点"], "sg")
            self.assertEqual(len(document.cases), 2)
            self.assertEqual(document.cases[0].tc_id, "TC001")
            self.assertEqual(document.cases[1].priority, "P1")

    def test_dedupe_mapper_marks_existing_and_new(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            markdown_path = root / "enriched.md"
            markdown_path.write_text(SAMPLE_MD, encoding="utf-8")
            knowledge_root = root / "knowledge_base"
            knowledge_root.mkdir()
            regression_root = root / "test_cases" / "zhaopin"
            regression_root.mkdir(parents=True)
            (regression_root / "test_existing.py").write_text(
                "\n".join(
                    [
                        "import allure",
                        '@allure.title("提交成功应跳转列表页")',
                    ]
                ),
                encoding="utf-8",
            )
            mapper = DedupeMapper()
            manifest_path = root / "case_manifest.json"
            entries = mapper.build_manifest(
                enriched_markdown_path=markdown_path,
                output_path=manifest_path,
                module="zhaopin",
                site="sg",
                feature_key="job_preferences",
                knowledge_base_root=knowledge_root,
                regression_test_root=root / "test_cases",
            )
            status_by_tc = {entry.tc_id: entry.status for entry in entries}
            self.assertEqual(status_by_tc["TC001"], "已有自动化")
            self.assertEqual(status_by_tc["TC002"], "新增候选")


if __name__ == "__main__":
    unittest.main()
