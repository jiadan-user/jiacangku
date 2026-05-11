from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from qa_agent import cli


class CliOkUiRunTests(unittest.TestCase):
    def _args(self, **overrides):
        values = {
            "module": None,
            "feature": None,
            "story": None,
            "priority": None,
            "site": None,
            "case_id": None,
            "path": "test_cases/property_list/",
            "nodeid": None,
            "workers": "2",
            "max_workers": 4,
            "artifact_retention": "lean",
            "case_timeout": 300,
            "idle_timeout": 900,
            "phase_timeout": 0,
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_ok_ui_run_command_forwards_timeout_args(self) -> None:
        config = SimpleNamespace(project_root=Path("/repo"))

        command = cli._build_ok_ui_run_command(config, self._args())

        self.assertEqual(command[:3], [sys.executable, "/repo/bundled/skills/ok_autotest_ui_skill/scripts/ok_test.py", "run"])
        self.assertIn("--case-timeout", command)
        self.assertIn("300", command)
        self.assertIn("--idle-timeout", command)
        self.assertIn("900", command)
        self.assertIn("--phase-timeout", command)
        self.assertIn("0", command)

    def test_outer_timeout_returns_without_run_id_for_publish_skip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            returncode, stdout, stderr, timed_out = cli._run_ok_ui_command(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                cwd=Path(tmp),
                timeout_seconds=1,
                stream=False,
            )

        self.assertTrue(timed_out)
        self.assertNotEqual(returncode, 0)
        self.assertEqual(cli._extract_ok_ui_run_id(stdout + stderr), "")

    def test_outer_timeout_with_run_id_but_missing_summary_does_not_raise(self) -> None:
        argv = [
            "qa-agent",
            "dashboard",
            "run-ok-ui",
            "--path",
            "test_cases/property_list/",
            "--outer-timeout",
            "1",
            "--json",
        ]
        with (
            patch.object(sys, "argv", argv),
            patch.object(cli, "load_config", return_value=SimpleNamespace(project_root=Path("/repo"))),
            patch.object(cli, "_run_ok_ui_command", return_value=(-9, "run_id=ok-timeout\n", "", True)),
            patch.object(cli, "publish_ok_ui_run", side_effect=FileNotFoundError("summary missing")),
        ):
            with redirect_stdout(StringIO()):
                result = cli.main()

        self.assertEqual(result, -9)


if __name__ == "__main__":
    unittest.main()
