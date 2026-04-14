from __future__ import annotations

import unittest
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.exceptions import PhaseBlockedError


class ConductorSmokeTests(unittest.TestCase):
    def test_plan_creates_requirement_packet(self) -> None:
        root = Path(__file__).resolve().parents[1]
        conductor = QAConductor(load_config(root))
        state = conductor.plan(
            {
                "figma_url": "https://www.figma.com/design/demo",
                "site": "sg",
                "module": "zhaopin",
                "feature": "job_preferences",
                "change_mode": "auto",
            }
        )
        status = conductor.status(state.run_id)
        self.assertEqual(status["change_mode"], "仅新需求")
        self.assertIn("requirement_packet", status["artifacts"])

    def test_run_blocks_at_analysis_bundle_without_external_output(self) -> None:
        root = Path(__file__).resolve().parents[1]
        conductor = QAConductor(load_config(root))
        with self.assertRaises(PhaseBlockedError) as ctx:
            conductor.run(
                {
                    "figma_url": "https://www.figma.com/design/demo",
                    "site": "sg",
                    "module": "zhaopin",
                    "feature": "job_preferences",
                    "change_mode": "auto",
                }
            )
        run_id = ctx.exception.run_id
        self.assertTrue(run_id)
        status = conductor.status(run_id)
        self.assertEqual(status["current_phase"], "分析资料包")
        self.assertIn("analysis_bundle", status["artifacts"])


if __name__ == "__main__":
    unittest.main()
