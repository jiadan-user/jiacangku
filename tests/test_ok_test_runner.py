from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


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

    def test_parallel_pytest_args_use_file_granularity(self) -> None:
        args = runner._build_pytest_args(
            ["test_cases/zhaopin/test_demo.py"],
            Path("junit.xml"),
            Path("allure-results"),
            workers=4,
        )

        self.assertIn("-n", args)
        self.assertIn("4", args)
        self.assertIn("--dist", args)
        self.assertIn("loadfile", args)
        self.assertNotIn("loadscope", args)

    def test_pytest_args_include_case_timeout_when_plugin_available(self) -> None:
        args = runner._build_pytest_args(
            ["test_cases/zhaopin/test_demo.py"],
            Path("junit.xml"),
            Path("allure-results"),
            workers=1,
            case_timeout=300,
            pytest_timeout_available=True,
        )

        self.assertIn("--timeout", args)
        self.assertIn("300", args)
        self.assertIn("--timeout-method", args)
        self.assertIn("thread", args)

    def test_pytest_args_skip_case_timeout_when_plugin_missing(self) -> None:
        args = runner._build_pytest_args(
            ["test_cases/zhaopin/test_demo.py"],
            Path("junit.xml"),
            Path("allure-results"),
            workers=1,
            case_timeout=300,
            pytest_timeout_available=False,
        )

        self.assertNotIn("--timeout", args)
        self.assertNotIn("--timeout-method", args)

    def test_path_only_selection_prefers_file_targets(self) -> None:
        case = runner.CatalogCase(
            nodeid="test_cases/zhaopin/test_demo.py::test_a",
            file_path="test_cases/zhaopin/test_demo.py",
            test_name="test_a",
            case_id=None,
            priority=None,
            site=None,
            markers=[],
            allure_feature=None,
            allure_story=None,
            allure_title=None,
        )
        criteria = runner.SelectionCriteria(path="test_cases/zhaopin/")

        targets, mode = runner._execution_targets([case], [case], criteria)

        self.assertEqual(targets, ["test_cases/zhaopin/test_demo.py"])
        self.assertEqual(mode, "file")

    def test_filtered_selection_keeps_nodeid_targets(self) -> None:
        case = runner.CatalogCase(
            nodeid="test_cases/zhaopin/test_demo.py::test_a",
            file_path="test_cases/zhaopin/test_demo.py",
            test_name="test_a",
            case_id=None,
            priority="p0",
            site=None,
            markers=["p0"],
            allure_feature=None,
            allure_story=None,
            allure_title=None,
        )
        criteria = runner.SelectionCriteria(path="test_cases/zhaopin/", priority="p0")

        targets, mode = runner._execution_targets([case], [case], criteria)

        self.assertEqual(targets, [case.nodeid])
        self.assertEqual(mode, "nodeid")

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

    def test_watchdog_kills_idle_subprocess_group(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_path = root / "pytest_output.txt"
            result = runner._run_pytest_process(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                output_path=output_path,
                allure_dir=root / "allure-results",
                idle_timeout=1,
                phase_timeout=0,
            )

            self.assertTrue(result["timed_out"])
            self.assertEqual(result["timeout_type"], "idle_timeout")
            self.assertNotEqual(result["returncode"], 0)
            self.assertIn("idle timeout", output_path.read_text(encoding="utf-8"))

    def test_run_phase_returns_blocked_report_on_timeout(self) -> None:
        case = runner.CatalogCase(
            nodeid="test_cases/demo/test_sleep.py::test_sleep",
            file_path="test_cases/demo/test_sleep.py",
            test_name="test_sleep",
            case_id=None,
            priority=None,
            site=None,
            markers=[],
            allure_feature=None,
            allure_story=None,
            allure_title=None,
        )
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            phase = runner._run_phase(
                "target_initial",
                [case],
                [case],
                runner.SelectionCriteria(path="test_cases/demo/"),
                run_dir,
                run_dir / "allure-results",
                [sys.executable, "-c", "import time; time.sleep(5)"],
                workers=1,
                case_timeout=0,
                idle_timeout=1,
                phase_timeout=0,
                pytest_timeout_available=False,
            )

            self.assertTrue(phase["timed_out"])
            self.assertEqual(phase["timeout_type"], "idle_timeout")
            self.assertEqual(phase["case_results"][0]["outcome"], "not_run")
            self.assertIn("block_reason", phase)
            self.assertTrue(Path(phase["output_path"]).exists())

    def test_serial_subprocess_output_written_to_phase_output(self) -> None:
        case = runner.CatalogCase(
            nodeid="test_cases/demo/test_output.py::test_output",
            file_path="test_cases/demo/test_output.py",
            test_name="test_output",
            case_id=None,
            priority=None,
            site=None,
            markers=[],
            allure_feature=None,
            allure_story=None,
            allure_title=None,
        )
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            phase = runner._run_phase(
                "target_initial",
                [case],
                [case],
                runner.SelectionCriteria(path="test_cases/demo/"),
                run_dir,
                run_dir / "allure-results",
                [sys.executable, "-c", "import sys; print('hello stdout'); sys.stderr.write('hello stderr\\n')"],
                workers=1,
                case_timeout=0,
                idle_timeout=5,
                phase_timeout=0,
                pytest_timeout_available=False,
            )

            output = Path(phase["output_path"]).read_text(encoding="utf-8")
            self.assertIn("hello stdout", output)
            self.assertIn("hello stderr", output)

    def test_generate_allure_report_uses_run_scoped_report_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "allure-results"
            report_dir = root / "ok_test_runs" / "run-1" / "allure-report"
            results_dir.mkdir()

            def fake_run(command, capture_output=True, text=True):
                self.assertEqual(command[2], str(results_dir))
                self.assertEqual(command[4], str(report_dir))
                report_dir.mkdir(parents=True)
                (report_dir / "index.html").write_text("<html></html>", encoding="utf-8")
                return types.SimpleNamespace(returncode=0, stdout="", stderr="")

            with (
                patch.object(runner, "_ensure_allure_cli", return_value=("allure", "Allure CLI 已就绪。")),
                patch.object(runner.subprocess, "run", side_effect=fake_run),
                patch.object(runner, "_sync_latest_static_report"),
                patch.object(runner, "_start_allure_server", return_value={"url": "http://127.0.0.1:1/index.html", "message": "ok"}),
            ):
                result = runner._generate_allure_report(results_dir, report_dir)

            self.assertTrue(result["generated"])
            self.assertEqual(result["report_dir"], str(report_dir))


if __name__ == "__main__":
    unittest.main()
