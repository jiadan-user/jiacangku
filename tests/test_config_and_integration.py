from __future__ import annotations

import sys
import unittest
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.integrations.ok_ui_skill import OkUISkillIntegration


class ConfigAndIntegrationTests(unittest.TestCase):
    def test_load_config_resolves_bundled_relative_paths(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_config(root)
        self.assertTrue(str(config.skills["paths"]["senior_qa_brain_root"]).startswith(str(root)))
        self.assertTrue(str(config.skills["paths"]["knowledge_base_root"]).startswith(str(root)))
        self.assertTrue(str(config.skills["commands"]["ok_ui_skill"]["script"]).startswith(str(root)))

    def test_ok_ui_skill_falls_back_to_current_python_when_venv_missing(self) -> None:
        integration = OkUISkillIntegration(
            script_path=Path(__file__),
            project_root=Path(__file__).resolve().parents[1],
            venv_python=Path(__file__).resolve().parents[1] / "missing-venv" / "bin" / "python",
        )
        self.assertEqual(integration.python_bin, sys.executable)


if __name__ == "__main__":
    unittest.main()
