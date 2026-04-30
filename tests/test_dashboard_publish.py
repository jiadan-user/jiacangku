import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qa_agent.dashboard_publish import DEFAULT_DASHBOARD_URL, _dashboard_url, build_ok_ui_publish_payload


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


if __name__ == "__main__":
    unittest.main()
