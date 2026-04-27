from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path


OK_UI_ROOT = Path(__file__).resolve().parents[1] / "bundled" / "skills" / "ok_autotest_ui_skill" / "bundled" / "ok_autotest_ui_pc"
sys.path.insert(0, str(OK_UI_ROOT))
if importlib.util.find_spec("pytest") is None:
    sys.modules["pytest"] = types.SimpleNamespace(TestReport=object, main=lambda *args, **kwargs: 0)

from tooling.ok_test import runner  # noqa: E402


class OkTestRunnerTests(unittest.TestCase):
    def _args(self, **overrides):
        values = {
            "workers": None,
            "max_workers": None,
            "artifact_retention": "lean",
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_prerequisites_force_serial_workers(self) -> None:
        result = runner._resolve_workers(self._args(workers="auto", max_workers=4), selected_count=20, has_prerequisites=True)

        self.assertEqual(result["resolved_workers"], 1)
        self.assertFalse(result["parallel_enabled"])
        self.assertIn("prerequisite", result["parallel_reason"])

    def test_junit_parser_maps_class_parametrized_unicode_nodeid(self) -> None:
        selected = ["test_cases/wallet/test_wallet_balance.py::TestBalance::test_total[中文]"]
        with tempfile.TemporaryDirectory() as tmp:
            junit_path = Path(tmp) / "junit.xml"
            junit_path.write_text(
                '<testsuite><testcase classname="test_cases.wallet.test_wallet_balance.TestBalance" '
                'name="test_total[中文]" time="0.25" /></testsuite>',
                encoding="utf-8",
            )

            results, warnings = runner._parse_junit_results(junit_path, selected)

        self.assertFalse(warnings)
        self.assertEqual(results[selected[0]]["outcome"], "passed")
        self.assertEqual(results[selected[0]]["duration"], 0.25)

    def test_lean_cleanup_only_deletes_passed_run_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            for name in ("coverage_input.json", "decision_input.json", "selection.json", "pytest_command.txt"):
                (run_dir / name).write_text("debug", encoding="utf-8")
            output_path = run_dir / "pytest_output_target_initial.txt"
            output_path.write_text("ok", encoding="utf-8")
            junit_path = run_dir / "junit_target_initial.xml"
            junit_path.write_text("<testsuite />", encoding="utf-8")
            summary = {
                "dry_run": False,
                "run_status": "passed",
                "artifact_retention": "lean",
                "phase_reports": [
                    {
                        "pytest_exit_code": 0,
                        "output_path": str(output_path),
                        "junit_path": str(junit_path),
                        "case_results": [{"nodeid": "test_demo.py::test_ok", "outcome": "passed"}],
                    }
                ],
            }

            cleanup = runner._lean_cleanup(run_dir, summary)

            self.assertTrue(cleanup["enabled"])
            self.assertFalse((run_dir / "coverage_input.json").exists())
            self.assertFalse(output_path.exists())
            self.assertTrue(junit_path.exists())

    def test_lean_cleanup_keeps_failed_run_debug_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            debug_path = run_dir / "pytest_output_target_initial.txt"
            debug_path.write_text("failed", encoding="utf-8")
            summary = {
                "dry_run": False,
                "run_status": "failed",
                "artifact_retention": "lean",
                "phase_reports": [{"output_path": str(debug_path)}],
            }

            cleanup = runner._lean_cleanup(run_dir, summary)

            self.assertFalse(cleanup["enabled"])
            self.assertTrue(debug_path.exists())


if __name__ == "__main__":
    unittest.main()
