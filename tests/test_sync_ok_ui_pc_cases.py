from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


def load_sync_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "sync_ok_ui_pc_cases.py"
    spec = importlib.util.spec_from_file_location("sync_ok_ui_pc_cases", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SyncOkUiPcCasesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sync = load_sync_module()

    def test_marker_lines_ignore_case_id_and_non_marker_config(self) -> None:
        text = """
[pytest]
markers =
    p0: priority marker
    case_id_tc001: dynamic case id marker
    smoke: smoke marker
# 日志配置
log_cli = true
log_file_format = %(asctime)s:%(message)s
"""

        self.assertEqual(
            ["    p0: priority marker", "    smoke: smoke marker"],
            self.sync.marker_lines(text),
        )

    def test_fixed_exclusions_keep_test_data_reports_out(self) -> None:
        self.assertFalse(self.sync.is_allowed_candidate("test_data/images/reports/junit.xml"))
        self.assertFalse(self.sync.is_allowed_candidate("test_data/images/.DS_Store"))
        self.assertTrue(self.sync.is_allowed_candidate("test_data/images/photo.png"))
        self.assertTrue(self.sync.is_allowed_candidate("test_cases/module/test_demo.py"))


if __name__ == "__main__":
    unittest.main()
