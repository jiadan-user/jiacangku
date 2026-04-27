from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


TOOLING_ROOT = (
    Path(__file__).resolve().parents[1]
    / "bundled"
    / "skills"
    / "ok_autotest_ui_skill"
    / "bundled"
    / "ok_autotest_ui_pc"
)
sys.path.insert(0, str(TOOLING_ROOT))

from tooling.ok_test.text_coverage import build_text_case_dashboard  # noqa: E402


class TextCoverageDashboardTest(unittest.TestCase):
    def test_relaxed_parser_counts_legacy_tc_headings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "wallet").mkdir()
            (root / "wallet" / "wallet_cases.md").write_text(
                """# Wallet

## 支付

### TC001：支付成功
- **优先级**: P0
- **UI自动化**: ✅ 可自动化

### TC002：支付失败
- **优先级**: P1
- **UI自动化**: ❌ 不可自动化
""",
                encoding="utf-8",
            )
            (root / "legacy").mkdir()
            (root / "legacy" / "legacy_cases.md").write_text(
                """# Legacy

## 旧格式

### TC003：有优先级但缺 UI 自动化字段
- **优先级**: P0

### TC004：缺少优先级和 UI 自动化字段
- 步骤: 打开页面
""",
                encoding="utf-8",
            )

            payload = build_text_case_dashboard(root)

        self.assertEqual(payload["total_cases"], 4)
        self.assertEqual(payload["automated_cases"], 1)
        self.assertEqual(payload["non_automated_cases"], 3)
        self.assertEqual(payload["parse_diagnostics"]["tc_headings_total"], 4)
        self.assertEqual(payload["parse_diagnostics"]["parsed_scenarios"], 4)
        self.assertEqual(payload["parse_diagnostics"]["needs_normalization_cases"], 2)
        p0 = next(item for item in payload["priorities"] if item["priority"] == "P0")
        self.assertEqual(p0["total_cases"], 2)
        self.assertEqual(p0["non_automated_cases"], 1)


if __name__ == "__main__":
    unittest.main()
