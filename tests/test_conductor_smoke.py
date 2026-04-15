from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.io import write_json
from qa_agent.models import (
    ChangeMode,
    LegacyUpdateGate,
    LegacyUpdateRoundOutcome,
    LegacyUpdateTask,
    LegacyUpdateTaskStatus,
    Phase,
    PhaseStatus,
    RunStatus,
)


class FakeLegacyUpdateExecutor:
    def __init__(self, outcomes: list[LegacyUpdateRoundOutcome]) -> None:
        self.outcomes = outcomes
        self.calls = 0

    def run_round(self, *, run_dir: Path, tasks: list[LegacyUpdateTask], round_index: int) -> LegacyUpdateRoundOutcome:
        del run_dir, tasks, round_index
        outcome = self.outcomes[min(self.calls, len(self.outcomes) - 1)]
        self.calls += 1
        return outcome


class ConductorSmokeTests(unittest.TestCase):
    def _make_conductor(self, executor=None) -> QAConductor:
        root = Path(__file__).resolve().parents[1]
        return QAConductor(load_config(root), legacy_update_executor=executor)

    def _seed_legacy_tasks(self, conductor: QAConductor, run_id: str, tasks: list[LegacyUpdateTask]) -> None:
        state = conductor.store.load(run_id)
        seed_path = conductor.store.artifact_path(run_id, "legacy_update_tasks_seed.json")
        write_json(seed_path, [task.__dict__ for task in tasks])
        state.artifacts["legacy_update_tasks_seed"] = str(seed_path)
        conductor.store.save(state)

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
        self.assertIn(Phase.IMPACT_ANALYSIS.value, state.phase_statuses)
        self.assertIn(Phase.LEGACY_UPDATE.value, state.phase_statuses)

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
        self.assertIn(Phase.IMPACT_ANALYSIS.value, state.phase_statuses)
        self.assertIn(Phase.LEGACY_UPDATE.value, state.phase_statuses)
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

    def test_advance_regression_without_legacy_tasks_reaches_ok_ui(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan({
            "module": "unknown_module",
            "site": "ae",
            "change_description": "修改了一个很小的文案",
        })
        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.OK_UI_REGRESSION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertIn("ok_autotest_ui_skill", state.blocked_reason)
        self.assertEqual(state.phase_statuses[Phase.IMPACT_ANALYSIS.value], PhaseStatus.COMPLETED.value)
        self.assertEqual(state.phase_statuses[Phase.LEGACY_UPDATE.value], PhaseStatus.COMPLETED.value)

    def test_legacy_update_stays_in_loop_until_next_round(self) -> None:
        base_task = LegacyUpdateTask(
            task_id="legacy-1",
            target_script="/tmp/fake.py",
            target_nodeid="test_cases/wallet/test_wallet.py::test_xxx",
            recommended_action="update-assertion",
            status=LegacyUpdateTaskStatus.PENDING.value,
        )
        retry_task = replace(base_task, status=LegacyUpdateTaskStatus.RETRY.value, attempts=1)
        pending_gate = LegacyUpdateGate(
            round_index=1,
            total_count=1,
            retry_count=1,
            all_completed=False,
            has_manual_review=False,
        )
        done_task = replace(base_task, status=LegacyUpdateTaskStatus.COMPLETED.value, attempts=2)
        done_gate = LegacyUpdateGate(
            round_index=2,
            total_count=1,
            completed_count=1,
            all_completed=True,
            has_manual_review=False,
        )
        executor = FakeLegacyUpdateExecutor(
            [
                LegacyUpdateRoundOutcome(tasks=[retry_task], gate=pending_gate, results=[]),
                LegacyUpdateRoundOutcome(tasks=[done_task], gate=done_gate, results=[]),
            ]
        )
        conductor = self._make_conductor(executor)
        state = conductor.plan({
            "module": "wallet",
            "site": "ae",
            "change_description": "修改了提现金额校验逻辑",
        })
        self._seed_legacy_tasks(conductor, state.run_id, [base_task])

        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.LEGACY_UPDATE.value)
        self.assertEqual(state.status, RunStatus.RUNNING.value)
        self.assertEqual(state.phase_statuses[Phase.LEGACY_UPDATE.value], PhaseStatus.RUNNING.value)
        self.assertIn("继续 advance 进入下一轮", state.blocked_reason)

        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.OK_UI_REGRESSION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.phase_statuses[Phase.LEGACY_UPDATE.value], PhaseStatus.COMPLETED.value)
        self.assertEqual(executor.calls, 2)

    def test_legacy_update_manual_review_blocks_current_phase(self) -> None:
        manual_task = LegacyUpdateTask(
            task_id="legacy-2",
            target_script="/tmp/fake.py",
            target_nodeid="test_cases/wallet/test_wallet.py::test_xxx",
            recommended_action="manual-review",
            status=LegacyUpdateTaskStatus.MANUAL_REVIEW.value,
            attempts=3,
        )
        manual_gate = LegacyUpdateGate(
            round_index=1,
            total_count=1,
            manual_review_count=1,
            all_completed=False,
            has_manual_review=True,
        )
        executor = FakeLegacyUpdateExecutor(
            [LegacyUpdateRoundOutcome(tasks=[manual_task], gate=manual_gate, results=[])]
        )
        conductor = self._make_conductor(executor)
        state = conductor.plan({
            "module": "wallet",
            "site": "ae",
            "change_description": "修改了提现金额校验逻辑",
        })
        self._seed_legacy_tasks(conductor, state.run_id, [manual_task])

        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.LEGACY_UPDATE.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.phase_statuses[Phase.LEGACY_UPDATE.value], PhaseStatus.BLOCKED.value)
        self.assertIn("manual-review", state.blocked_reason)

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
