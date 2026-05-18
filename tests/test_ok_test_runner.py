from __future__ import annotations

import argparse
import importlib.util
import json
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
            "failed_reruns": 1,
            "dry_run": False,
            "module": None,
            "feature": None,
            "story": None,
            "priority": None,
            "site": None,
            "case_id": None,
            "path": "test_cases/demo/",
            "nodeid": None,
            "case_timeout": 0,
            "idle_timeout": 0,
            "phase_timeout": 0,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def _case(self, name: str) -> runner.CatalogCase:
        return runner.CatalogCase(
            nodeid=f"test_cases/demo/test_demo.py::{name}",
            file_path="test_cases/demo/test_demo.py",
            test_name=name,
            case_id=None,
            priority=None,
            site=None,
            markers=[],
            allure_feature=None,
            allure_story=None,
            allure_title=None,
        )

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

    def test_failed_case_nodeids_only_include_failed_and_error(self) -> None:
        results = [
            {"nodeid": "test_a", "outcome": "passed"},
            {"nodeid": "test_b", "outcome": "failed"},
            {"nodeid": "test_c", "outcome": "error"},
            {"nodeid": "test_d", "outcome": "skipped"},
            {"nodeid": "test_e", "outcome": "not_run"},
        ]

        self.assertEqual(runner._failed_case_nodeids(results), ["test_b", "test_c"])

    def test_failed_rerun_merge_uses_rerun_outcome_and_keeps_trace(self) -> None:
        initial_results = [
            {"nodeid": "test_a", "outcome": "passed", "duration": 1.0, "reason": None},
            {"nodeid": "test_b", "outcome": "failed", "duration": 2.0, "reason": "first failure"},
            {"nodeid": "test_c", "outcome": "error", "duration": 3.0, "reason": "first error"},
            {"nodeid": "test_d", "outcome": "skipped", "duration": 0.0, "reason": "skip"},
        ]
        rerun_results = [
            {"nodeid": "test_b", "outcome": "passed", "duration": 1.5, "reason": None},
            {"nodeid": "test_c", "outcome": "failed", "duration": 1.2, "reason": "still bad"},
        ]

        merged, stats = runner._merge_failed_rerun_results(initial_results, rerun_results)
        counts = runner._result_counts(merged)

        self.assertEqual(counts["passed"], 2)
        self.assertEqual(counts["failed"], 1)
        self.assertEqual(counts["skipped"], 1)
        self.assertEqual(stats["failed_rerun_input_count"], 2)
        self.assertEqual(stats["failed_rerun_resolved_count"], 1)
        self.assertEqual(stats["failed_rerun_still_failed_count"], 1)
        self.assertTrue(merged[1]["rerun_attempted"])
        self.assertEqual(merged[1]["initial_outcome"], "failed")
        self.assertEqual(merged[1]["rerun_outcome"], "passed")
        self.assertEqual(merged[1]["rerun_phase"], "target_rerun_failed")

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

    def test_handle_run_reruns_failed_cases_after_initial_target_phase(self) -> None:
        cases = [self._case("test_a"), self._case("test_b"), self._case("test_c"), self._case("test_d")]
        calls: list[tuple[str, list[str]]] = []

        def fake_run_phase(phase_name, phase_cases, *args, **kwargs):
            del args, kwargs
            calls.append((phase_name, [case.nodeid for case in phase_cases]))
            if phase_name == "target_initial":
                return {
                    "phase": phase_name,
                    "pytest_exit_code": 1,
                    "junit_path": "initial.xml",
                    "case_results": [
                        {"nodeid": cases[0].nodeid, "outcome": "passed", "duration": 1.0, "reason": None},
                        {"nodeid": cases[1].nodeid, "outcome": "failed", "duration": 1.0, "reason": "first failure"},
                        {"nodeid": cases[2].nodeid, "outcome": "error", "duration": 1.0, "reason": "first error"},
                        {"nodeid": cases[3].nodeid, "outcome": "skipped", "duration": 0.0, "reason": "skip"},
                    ],
                }
            self.assertEqual(phase_name, "target_rerun_failed")
            self.assertEqual([case.nodeid for case in phase_cases], [cases[1].nodeid, cases[2].nodeid])
            return {
                "phase": phase_name,
                "pytest_exit_code": 1,
                "junit_path": "rerun.xml",
                "case_results": [
                    {"nodeid": cases[1].nodeid, "outcome": "passed", "duration": 1.0, "reason": None},
                    {"nodeid": cases[2].nodeid, "outcome": "failed", "duration": 1.0, "reason": "still failing"},
                ],
            }

        with tempfile.TemporaryDirectory() as tmp:
            reports_dir = Path(tmp) / "ok_test_runs"
            root_reports_dir = Path(tmp) / "reports"
            with (
                patch.object(runner, "GENERATED_CATALOG_PATH", types.SimpleNamespace(exists=lambda: True)),
                patch.object(runner, "load_catalog", return_value=cases),
                patch.object(runner, "select_cases_from_catalog", return_value=cases),
                patch.object(runner, "recommend_cases", return_value=([], [], [])),
                patch.object(runner, "_load_prerequisite_config", return_value={"features": {}, "cases": {}, "nodeids": {}}),
                patch.object(runner, "create_run_id", return_value="run-rerun"),
                patch.object(runner, "REPORTS_DIR", reports_dir),
                patch.object(runner, "ROOT_REPORTS_DIR", root_reports_dir),
                patch.object(runner, "ALLURE_RESULTS_DIR", root_reports_dir / "allure-results"),
                patch.object(runner, "resolve_pytest_command", return_value=([sys.executable], sys.executable)),
                patch.object(runner, "_run_phase", side_effect=fake_run_phase),
                patch.object(runner, "_sync_latest_report_assets"),
                patch.object(runner, "_generate_allure_report", return_value={"report_dir": str(root_reports_dir / "allure-report"), "url": None, "message": "ok"}),
                patch.object(runner, "_start_allure_server", return_value={"url": None, "message": "ok"}),
            ):
                result = runner.handle_run(self._args())

            summary = json.loads((reports_dir / "run-rerun" / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual([name for name, _nodeids in calls], ["target_initial", "target_rerun_failed"])
        self.assertEqual(summary["passed_cases"], 2)
        self.assertEqual(summary["failed_cases"], 1)
        self.assertEqual(summary["skipped_cases"], 1)
        self.assertTrue(summary["failed_rerun_attempted"])
        self.assertEqual(summary["failed_rerun_input_count"], 2)
        self.assertEqual(summary["failed_rerun_resolved_count"], 1)
        self.assertEqual(summary["failed_rerun_still_failed_count"], 1)
        self.assertEqual(summary["phase_reports"][-1]["phase"], "target_rerun_failed")

    def test_handle_run_skips_failed_rerun_when_disabled_or_blocked(self) -> None:
        cases = [self._case("test_a")]

        def run_with_initial_phase(initial_phase: dict[str, object], *, failed_reruns: int) -> dict[str, object]:
            with tempfile.TemporaryDirectory() as tmp:
                reports_dir = Path(tmp) / "ok_test_runs"
                root_reports_dir = Path(tmp) / "reports"
                with (
                    patch.object(runner, "GENERATED_CATALOG_PATH", types.SimpleNamespace(exists=lambda: True)),
                    patch.object(runner, "load_catalog", return_value=cases),
                    patch.object(runner, "select_cases_from_catalog", return_value=cases),
                    patch.object(runner, "recommend_cases", return_value=([], [], [])),
                    patch.object(runner, "_load_prerequisite_config", return_value={"features": {}, "cases": {}, "nodeids": {}}),
                    patch.object(runner, "create_run_id", return_value="run-no-rerun"),
                    patch.object(runner, "REPORTS_DIR", reports_dir),
                    patch.object(runner, "ROOT_REPORTS_DIR", root_reports_dir),
                    patch.object(runner, "ALLURE_RESULTS_DIR", root_reports_dir / "allure-results"),
                    patch.object(runner, "resolve_pytest_command", return_value=([sys.executable], sys.executable)),
                    patch.object(runner, "_run_phase", return_value=initial_phase) as run_phase,
                    patch.object(runner, "_sync_latest_report_assets"),
                    patch.object(runner, "_generate_allure_report", return_value={"report_dir": str(root_reports_dir / "allure-report"), "url": None, "message": "ok"}),
                ):
                    runner.handle_run(self._args(failed_reruns=failed_reruns))
                    summary = json.loads((reports_dir / "run-no-rerun" / "summary.json").read_text(encoding="utf-8"))
                    return {"summary": summary, "call_count": run_phase.call_count}

        failed_phase = {
            "phase": "target_initial",
            "pytest_exit_code": 1,
            "junit_path": "initial.xml",
            "case_results": [{"nodeid": cases[0].nodeid, "outcome": "failed", "duration": 1.0, "reason": "failed"}],
        }
        disabled = run_with_initial_phase(failed_phase, failed_reruns=0)
        self.assertEqual(disabled["call_count"], 1)
        self.assertFalse(disabled["summary"]["failed_rerun_attempted"])

        blocked_phase = {
            **failed_phase,
            "block_reason": "target_initial idle_timeout after 1s",
        }
        blocked = run_with_initial_phase(blocked_phase, failed_reruns=1)
        self.assertEqual(blocked["call_count"], 1)
        self.assertEqual(blocked["summary"]["run_status"], "blocked")
        self.assertFalse(blocked["summary"]["failed_rerun_attempted"])

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
