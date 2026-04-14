from __future__ import annotations

import unittest
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.models import ChangeMode, Phase, PhaseStatus, RunStatus


class ConductorSmokeTests(unittest.TestCase):
    def _make_conductor(self) -> QAConductor:
        root = Path(__file__).resolve().parents[1]
        return QAConductor(load_config(root))

    def test_plan_new_feature(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan({
            "figma_url": "https://www.figma.com/design/demo",
            "site": "sg",
            "module": "login",
            "feature": "visual_optimization",
        })
        self.assertEqual(state.change_mode, ChangeMode.NEW_FEATURE.value)
        self.assertEqual(state.status, RunStatus.PLANNED.value)
        self.assertIn("requirement_packet", state.artifacts)
        self.assertEqual(state.phase_statuses[Phase.INTAKE.value], PhaseStatus.COMPLETED.value)
        self.assertEqual(state.phase_statuses[Phase.IMPACT_SPLIT.value], PhaseStatus.COMPLETED.value)

    def test_plan_regression(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan({
            "module": "wallet",
            "site": "ae",
            "change_description": "修改了提现金额校验逻辑",
        })
        self.assertEqual(state.change_mode, ChangeMode.REGRESSION.value)
        self.assertNotIn(Phase.SENIOR_QA_BRAIN.value, state.phase_statuses)
        self.assertNotIn(Phase.PLAYWRIGHT_GENERATOR.value, state.phase_statuses)
        self.assertIn(Phase.OK_UI_REGRESSION.value, state.phase_statuses)

    def test_plan_mixed(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan({
            "figma_url": "https://www.figma.com/design/demo",
            "module": "login",
            "site": "sg",
            "change_description": "同时修改了旧的注册流程",
        })
        self.assertEqual(state.change_mode, ChangeMode.MIXED.value)

    def test_advance_new_feature_blocks_at_senior_qa(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan({
            "figma_url": "https://www.figma.com/design/demo",
            "site": "sg",
            "module": "login",
        })
        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.SENIOR_QA_BRAIN.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertIn("senior-qa-brain", state.blocked_reason)
        self.assertIn(f"{Phase.SENIOR_QA_BRAIN.value}_skill_path", state.artifacts)

    def test_advance_regression_blocks_at_ok_ui(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan({
            "module": "wallet",
            "site": "ae",
            "change_description": "修改了提现逻辑",
        })
        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.OK_UI_REGRESSION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)

    def test_complete_phase_advances(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan({
            "figma_url": "https://www.figma.com/design/demo",
            "site": "sg",
            "module": "login",
        })
        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.SENIOR_QA_BRAIN.value)
        state = conductor.complete_phase(state.run_id, Phase.SENIOR_QA_BRAIN.value)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)

    def test_status_returns_data(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan({"module": "wallet", "site": "ae", "change_description": "test"})
        data = conductor.status(state.run_id)
        self.assertEqual(data["run_id"], state.run_id)
        self.assertEqual(data["change_mode"], ChangeMode.REGRESSION.value)

    def test_status_nonexistent_run_raises(self) -> None:
        conductor = self._make_conductor()
        with self.assertRaises(FileNotFoundError):
            conductor.status("nonexistent")


if __name__ == "__main__":
    unittest.main()
