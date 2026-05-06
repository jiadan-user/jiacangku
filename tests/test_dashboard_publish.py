import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qa_agent.dashboard_publish import DEFAULT_DASHBOARD_URL, _dashboard_url, _find_ok_ui_artifacts, build_ok_ui_publish_payload


class DashboardPublishConfigTest(unittest.TestCase):
    def test_default_dashboard_url_is_remote_dashboard(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(_dashboard_url(), DEFAULT_DASHBOARD_URL)

    def test_env_url_overrides_default(self) -> None:
        with patch.dict(os.environ, {"QA_AGENT_DASHBOARD_URL": "http://127.0.0.1:8001"}, clear=True):
            self.assertEqual(_dashboard_url(), "http://127.0.0.1:8001")

    def test_explicit_url_overrides_env(self) -> None:
        with patch.dict(os.environ, {"QA_AGENT_DASHBOARD_URL": "http://127.0.0.1:8001"}, clear=True):
            self.assertEqual(_dashboard_url("http://example.test:8001"), "http://example.test:8001")

    def test_full_run_publish_does_not_fallback_to_unrelated_latest_ok_ui_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            unrelated = Path(tmp) / "reports" / "ok_test_runs" / "latest"
            unrelated.mkdir(parents=True)
            (unrelated / "summary.json").write_text(json.dumps({"run_id": "latest"}), encoding="utf-8")

            summary, coverage, decision = _find_ok_ui_artifacts(
                {"artifacts": {"ok_ui_execution_report": str(Path(tmp) / "phase3_report.md")}}
            )

        self.assertEqual(summary, {})
        self.assertEqual(coverage, {})
        self.assertEqual(decision, {})

    def test_build_ok_ui_publish_payload_uses_standalone_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = (
                root
                / "bundled"
                / "skills"
                / "ok_autotest_ui_skill"
                / "bundled"
                / "ok_autotest_ui_pc"
                / "reports"
                / "ok_test_runs"
                / "ok-run-1"
            )
            run_dir.mkdir(parents=True)
            summary = {
                "run_id": "ok-run-1",
                "run_status": "passed",
                "selected_count": 2,
                "executed_cases": 2,
                "passed_cases": 2,
                "failed_cases": 0,
                "skipped_cases": 0,
                "selected_modules": ["zhaopin"],
                "selection": {"path": "test_cases/zhaopin"},
                "selected_nodeids": ["test_cases/zhaopin/test_demo.py::test_a"],
                "resolved_workers": 1,
            }
            (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
            (run_dir / "coverage_report.json").write_text(json.dumps({"executed_cases": 2}), encoding="utf-8")
            (run_dir / "decision_report.json").write_text(json.dumps({"risk_level": "low"}), encoding="utf-8")

            payload = build_ok_ui_publish_payload(root, "ok-run-1", project_key="OK")

        self.assertEqual(payload["run_id"], "ok-run-1")
        self.assertEqual(payload["project_key"], "OK")
        self.assertEqual(payload["change_mode"], "OK UI 独立回归")
        self.assertEqual(payload["module"], ["zhaopin"])
        self.assertEqual(payload["trigger_source"], "ok_ui_skill_cli")
        self.assertEqual(payload["artifacts"]["summary"]["run_status"], "passed")
        self.assertIn("OK UI 独立回归报告", payload["artifacts"]["final_report"])

    def test_ok_ui_publish_payload_compacts_large_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = (
                root
                / "bundled"
                / "skills"
                / "ok_autotest_ui_skill"
                / "bundled"
                / "ok_autotest_ui_pc"
                / "reports"
                / "ok_test_runs"
                / "ok-run-large"
            )
            run_dir.mkdir(parents=True)
            summary = {
                "run_id": "ok-run-large",
                "run_status": "failed",
                "selected_count": 2286,
                "executed_cases": 2118,
                "passed_cases": 1465,
                "failed_cases": 653,
                "skipped_cases": 168,
                "requested_workers": "6",
                "resolved_workers": 4,
                "selected_modules": ["zhaopin"],
                "selection": {"path": "test_cases/"},
                "selected_nodeids": [f"test_cases/demo/test_{idx}.py::test_case" for idx in range(2286)],
                "case_results": [
                    {"nodeid": f"test_cases/demo/test_{idx}.py::test_case", "outcome": "failed"}
                    for idx in range(653)
                ],
                "phase_reports": [
                    {
                        "phase": "target_initial",
                        "pytest_exit_code": 1,
                        "case_results": [
                            {"nodeid": f"test_cases/demo/test_{idx}.py::test_case", "outcome": "failed"}
                            for idx in range(653)
                        ],
                    }
                ],
            }
            (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
            (run_dir / "coverage_report.json").write_text(json.dumps({}), encoding="utf-8")
            (run_dir / "decision_report.json").write_text(json.dumps({}), encoding="utf-8")

            payload = build_ok_ui_publish_payload(root, "ok-run-large", project_key="OK")

        compact = payload["artifacts"]["summary"]
        self.assertEqual(compact["run_status"], "failed")
        self.assertNotIn("selected_nodeids", compact)
        self.assertNotIn("case_results", compact)
        self.assertEqual(compact["selected_nodeids_sample"]["total"], 2286)
        self.assertEqual(len(compact["selected_nodeids_sample"]["items"]), 50)
        self.assertEqual(compact["case_results_total"], 653)
        self.assertEqual(compact["phase_reports"][0]["case_results_total"], 653)
        self.assertLess(len(json.dumps(compact)), 20000)

    def test_ok_ui_publish_payload_drops_loopback_allure_url_when_report_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = (
                root
                / "bundled"
                / "skills"
                / "ok_autotest_ui_skill"
                / "bundled"
                / "ok_autotest_ui_pc"
                / "reports"
                / "ok_test_runs"
                / "ok-run-loopback"
            )
            run_dir.mkdir(parents=True)
            summary = {
                "run_id": "ok-run-loopback",
                "run_status": "failed",
                "selected_count": 1,
                "executed_cases": 1,
                "passed_cases": 0,
                "failed_cases": 1,
                "skipped_cases": 0,
                "allure_url": "http://127.0.0.1:57788/index.html",
                "allure_report": str(Path(tmp) / "missing-allure-report"),
            }
            (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
            (run_dir / "coverage_report.json").write_text(json.dumps({}), encoding="utf-8")
            (run_dir / "decision_report.json").write_text(json.dumps({}), encoding="utf-8")

            payload = build_ok_ui_publish_payload(root, "ok-run-loopback", project_key="OK")

        self.assertNotIn("allure_url", payload["artifacts"]["summary"])
        self.assertEqual(payload["artifacts"]["allure_report"], {})

    def test_ok_ui_publish_payload_defers_large_allure_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tooling_root = (
                root
                / "bundled"
                / "skills"
                / "ok_autotest_ui_skill"
                / "bundled"
                / "ok_autotest_ui_pc"
            )
            run_dir = tooling_root / "reports" / "ok_test_runs" / "ok-run-allure"
            allure_dir = tooling_root / "reports" / "allure-report"
            run_dir.mkdir(parents=True)
            allure_dir.mkdir(parents=True)
            (tooling_root / "reports" / "ok_test_latest_run.txt").write_text("ok-run-allure\n", encoding="utf-8")
            (allure_dir / "index.html").write_text("<html></html>", encoding="utf-8")
            (allure_dir / "large.js").write_text("x" * 100, encoding="utf-8")
            summary = {
                "run_id": "ok-run-allure",
                "run_status": "passed",
                "selected_count": 1,
                "executed_cases": 1,
                "passed_cases": 1,
                "failed_cases": 0,
                "skipped_cases": 0,
                "allure_report": str(allure_dir),
            }
            (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
            (run_dir / "coverage_report.json").write_text(json.dumps({}), encoding="utf-8")
            (run_dir / "decision_report.json").write_text(json.dumps({}), encoding="utf-8")

            with patch.dict(os.environ, {"QA_AGENT_MAX_ALLURE_PACKAGE_BYTES": "10"}):
                payload = build_ok_ui_publish_payload(root, "ok-run-allure", project_key="OK")

        allure_report = payload["artifacts"]["allure_report"]
        self.assertTrue(allure_report["deferred_upload"])
        self.assertEqual(allure_report["reason"], "allure report package too large for inline publish")
        self.assertEqual(allure_report["report_dir"], str(allure_dir))
        self.assertNotIn("files", allure_report)

    def test_ok_ui_publish_payload_uses_run_scoped_allure_for_non_latest_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tooling_root = (
                root
                / "bundled"
                / "skills"
                / "ok_autotest_ui_skill"
                / "bundled"
                / "ok_autotest_ui_pc"
            )
            run_dir = tooling_root / "reports" / "ok_test_runs" / "old-run"
            run_allure_dir = run_dir / "allure-report"
            shared_allure_dir = tooling_root / "reports" / "allure-report"
            run_allure_dir.mkdir(parents=True)
            shared_allure_dir.mkdir(parents=True)
            (tooling_root / "reports" / "ok_test_latest_run.txt").write_text("newer-run\n", encoding="utf-8")
            (run_allure_dir / "index.html").write_text("<html>old</html>", encoding="utf-8")
            (shared_allure_dir / "index.html").write_text("<html>new</html>", encoding="utf-8")
            summary = {
                "run_id": "old-run",
                "run_status": "passed",
                "selected_count": 1,
                "executed_cases": 1,
                "passed_cases": 1,
                "failed_cases": 0,
                "skipped_cases": 0,
                "allure_report": str(shared_allure_dir),
            }
            (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
            (run_dir / "coverage_report.json").write_text(json.dumps({}), encoding="utf-8")
            (run_dir / "decision_report.json").write_text(json.dumps({}), encoding="utf-8")

            payload = build_ok_ui_publish_payload(root, "old-run", project_key="OK")

        files = payload["artifacts"]["allure_report"]["files"]
        self.assertEqual(files[0]["path"], "index.html")
        self.assertEqual(payload["artifacts"]["allure_report"].get("deferred_upload"), None)


if __name__ == "__main__":
    unittest.main()
