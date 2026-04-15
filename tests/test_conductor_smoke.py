from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.models import (
    AttributionCategory,
    ChangeMode,
    ImpactRunStatus,
    ImpactVerificationOutcome,
    ImpactVerificationRecord,
    LegacyUpdateGate,
    LegacyUpdateRoundOutcome,
    LegacyUpdateTask,
    LegacyUpdateTaskStatus,
    Phase,
    PhaseStatus,
    RunStatus,
)


class FakeImpactVerificationExecutor:
    def __init__(self, outcome: ImpactVerificationOutcome) -> None:
        self.outcome = outcome
        self.calls = 0

    def verify(self, *, run_dir: Path, packet: dict, impact_payload: dict) -> ImpactVerificationOutcome:
        del run_dir, packet, impact_payload
        self.calls += 1
        return self.outcome


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
    def _make_conductor(self, legacy_executor=None, impact_executor=None) -> QAConductor:
        root = Path(__file__).resolve().parents[1]
        return QAConductor(
            load_config(root),
            legacy_update_executor=legacy_executor,
            impact_verification_executor=impact_executor,
        )

    def _passed_verification_outcome(self, source_type: str = "existing-script") -> ImpactVerificationOutcome:
        record = ImpactVerificationRecord(
            source_type=source_type,
            target="/tmp/test_case.py",
            module="car",
            site="ae",
            run_status=ImpactRunStatus.PASSED.value,
            category=AttributionCategory.PASSED.value,
            summary="1 passed",
            reason="受影响用例执行通过",
            next_action="人工确认后继续",
        )
        return ImpactVerificationOutcome(
            selector_plan={
                "module": "car",
                "site": "ae",
                "feature_name": "列表",
                "candidate_paths": [record.target],
                "selectors": [{"kind": "path", "value": record.target}],
                "nodeids": [],
                "case_ids": [],
            },
            records=[record],
        )

    def test_plan_requires_explicit_mode(self) -> None:
        conductor = self._make_conductor()
        with self.assertRaises(ValueError):
            conductor.plan({"module": "car", "site": "ae", "change_description": "列表卡片样式调整"})

    def test_plan_new_feature(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan(
            {
                "change_mode": ChangeMode.NEW_FEATURE.value,
                "figma_url": "https://www.figma.com/design/demo",
                "site": "ae",
                "module": "car",
                "feature": "列表",
            }
        )
        self.assertEqual(state.change_mode, ChangeMode.NEW_FEATURE.value)
        self.assertEqual(state.status, RunStatus.PLANNED.value)
        self.assertEqual(state.phase_statuses[Phase.IMPACT_VERIFICATION.value], PhaseStatus.PENDING.value)
        self.assertEqual(state.phase_statuses[Phase.KNOWLEDGE_BASE_UPDATE.value], PhaseStatus.PENDING.value)

    def test_advance_regression_blocks_at_impact_verification(self) -> None:
        impact_executor = FakeImpactVerificationExecutor(self._passed_verification_outcome())
        conductor = self._make_conductor(impact_executor=impact_executor)
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "change_description": "列表卡片样式调整",
            }
        )
        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.IMPACT_VERIFICATION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.phase_statuses[Phase.IMPACT_ANALYSIS.value], PhaseStatus.COMPLETED.value)
        self.assertEqual(state.phase_statuses[Phase.IMPACT_VERIFICATION.value], PhaseStatus.BLOCKED.value)
        self.assertIn("change_attribution_report", state.artifacts)
        self.assertEqual(impact_executor.calls, 1)

    def test_complete_impact_verification_without_tasks_reaches_ok_ui(self) -> None:
        impact_executor = FakeImpactVerificationExecutor(self._passed_verification_outcome())
        conductor = self._make_conductor(impact_executor=impact_executor)
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "change_description": "列表卡片样式调整",
            }
        )
        state = conductor.advance(state.run_id)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        self.assertEqual(state.current_phase, Phase.OK_UI_REGRESSION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.phase_statuses[Phase.LEGACY_UPDATE.value], PhaseStatus.COMPLETED.value)

    def test_complete_impact_verification_generates_legacy_tasks_and_loops(self) -> None:
        impact_outcome = ImpactVerificationOutcome(
            selector_plan={
                "module": "wallet",
                "site": "ae",
                "feature_name": "withdrawal",
                "candidate_paths": ["/tmp/test_wallet.py"],
                "selectors": [{"kind": "path", "value": "/tmp/test_wallet.py"}],
                "nodeids": ["test_cases/wallet/test_wallet.py::test_xxx"],
                "case_ids": ["case_id_wallet_xxx"],
            },
            records=[
                ImpactVerificationRecord(
                    source_type="existing-script",
                    target="/tmp/test_wallet.py",
                    module="wallet",
                    site="ae",
                    related_case_id="case_id_wallet_xxx",
                    related_nodeid="test_cases/wallet/test_wallet.py::test_xxx",
                    run_status=ImpactRunStatus.FAILED.value,
                    category=AttributionCategory.LATEST_CHANGE.value,
                    summary="assert amount mismatch",
                    reason="断言不匹配，符合本次受影响范围",
                    next_action="人工确认后进入 assertion 更新任务",
                )
            ],
        )
        base_task = LegacyUpdateTask(
            task_id="legacy-1",
            target_script="/tmp/test_wallet.py",
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
        legacy_executor = FakeLegacyUpdateExecutor(
            [LegacyUpdateRoundOutcome(tasks=[retry_task], gate=pending_gate, results=[])]
        )
        conductor = self._make_conductor(
            legacy_executor=legacy_executor,
            impact_executor=FakeImpactVerificationExecutor(impact_outcome),
        )
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "wallet",
                "site": "ae",
                "change_description": "修改了提现金额校验逻辑",
            }
        )
        state = conductor.advance(state.run_id)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        self.assertEqual(state.current_phase, Phase.LEGACY_UPDATE.value)
        self.assertEqual(state.status, RunStatus.RUNNING.value)
        self.assertEqual(state.phase_statuses[Phase.LEGACY_UPDATE.value], PhaseStatus.RUNNING.value)
        self.assertIn("继续 advance 进入下一轮", state.blocked_reason)
        self.assertEqual(legacy_executor.calls, 1)

    def test_complete_ok_ui_enters_knowledge_base_update(self) -> None:
        impact_executor = FakeImpactVerificationExecutor(self._passed_verification_outcome())
        conductor = self._make_conductor(impact_executor=impact_executor)
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "change_description": "列表卡片样式调整",
            }
        )
        state = conductor.advance(state.run_id)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        state = conductor.complete_phase(state.run_id, Phase.OK_UI_REGRESSION.value)
        self.assertEqual(state.current_phase, Phase.KNOWLEDGE_BASE_UPDATE.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.phase_statuses[Phase.FINAL_REPORT.value], PhaseStatus.COMPLETED.value)
        self.assertIn(f"{Phase.KNOWLEDGE_BASE_UPDATE.value}_instruction", state.artifacts)

    def test_complete_knowledge_base_update_finishes_run(self) -> None:
        impact_executor = FakeImpactVerificationExecutor(self._passed_verification_outcome())
        conductor = self._make_conductor(impact_executor=impact_executor)
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "change_description": "列表卡片样式调整",
            }
        )
        state = conductor.advance(state.run_id)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        state = conductor.complete_phase(state.run_id, Phase.OK_UI_REGRESSION.value)
        state = conductor.complete_phase(state.run_id, Phase.KNOWLEDGE_BASE_UPDATE.value)
        self.assertEqual(state.status, RunStatus.COMPLETED.value)
        self.assertEqual(state.phase_statuses[Phase.KNOWLEDGE_BASE_UPDATE.value], PhaseStatus.COMPLETED.value)

    def test_status_returns_data(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "wallet",
                "site": "ae",
                "change_description": "test",
            }
        )
        data = conductor.status(state.run_id)
        self.assertEqual(data["run_id"], state.run_id)
        self.assertEqual(data["change_mode"], ChangeMode.REGRESSION.value)

    def test_status_nonexistent_run_raises(self) -> None:
        conductor = self._make_conductor()
        with self.assertRaises(FileNotFoundError):
            conductor.status("nonexistent")


if __name__ == "__main__":
    unittest.main()
