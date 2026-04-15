from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from qa_agent.config import load_config
from qa_agent.conductor import QAConductor
from qa_agent.io import read_json, read_text
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
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.kb_root = self.temp_path / "knowledge_base"
        (self.kb_root / "文本用例").mkdir(parents=True, exist_ok=True)
        self.regression_root = self.temp_path / "regression_project"
        (self.regression_root / "test_cases").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _make_conductor(self, legacy_executor=None, impact_executor=None) -> QAConductor:
        root = Path(__file__).resolve().parents[1]
        config = load_config(root)
        config.skills["paths"]["knowledge_base_root"] = str(self.kb_root)
        config.skills["paths"]["regression_project_root"] = str(self.regression_root)
        return QAConductor(
            config,
            legacy_update_executor=legacy_executor,
            impact_verification_executor=impact_executor,
        )

    def _passed_verification_outcome(self, source_type: str = "existing-script") -> ImpactVerificationOutcome:
        record = ImpactVerificationRecord(
            source_type=source_type,
            target=str(self.temp_path / "impact_case.py"),
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

    def _write_temp_file(self, relative_path: str, content: str) -> str:
        path = self.temp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)

    def _new_feature_inputs(self) -> dict[str, str]:
        return {
            "change_mode": ChangeMode.NEW_FEATURE.value,
            "figma_url": "https://www.figma.com/design/demo",
            "site": "ae",
            "module": "car",
            "feature": "列表",
        }

    def _sample_analysis_report(self) -> str:
        return "# 列表测试分析报告\n\n- 风险点: 卡片布局、字段展示、跳转入口\n"

    def _sample_textcases(self, *, missing_ui_marker: bool = False) -> str:
        ui_line = "" if missing_ui_marker else "- **UI自动化**: ✅ 可自动化\n"
        return (
            "# OK-AE-Car-列表-测试用例\n\n"
            "## 测试环境配置（必填）\n\n"
            "| 字段 | 值 | 说明 |\n"
            "| --- | --- | --- |\n"
            "| 站点 | ae | 站点 |\n"
            "| 基础URL | https://ae.example.com/car | 基础地址 |\n"
            "| 角色 | visitor | 角色 |\n\n"
            "## 测试用例\n\n"
            "### TC001: 车列表大卡样式展示\n\n"
            "#### 📋 前置条件\n"
            "- 已进入车列表页\n\n"
            "#### 🎬 执行步骤\n"
            "1. 打开车列表页\n"
            "2. 观察首屏列表卡片\n\n"
            "#### ✅ 预期结果\n"
            "- 卡片展示为大卡样式\n\n"
            "#### 📊 用例属性\n"
            "- **优先级**: P0\n"
            "- **测试类型**: 功能测试\n"
            f"{ui_line}\n"
            "---\n\n"
            "### TC002: 车列表卡片视觉感受\n\n"
            "#### 📋 前置条件\n"
            "- 已进入车列表页\n\n"
            "#### 🎬 执行步骤\n"
            "1. 观察卡片阴影和动效\n\n"
            "#### ✅ 预期结果\n"
            "- 动效平滑，视觉符合设计\n\n"
            "#### 📊 用例属性\n"
            "- **优先级**: P2\n"
            "- **测试类型**: UI测试\n"
            "- **UI自动化**: ❌ 不可自动化\n"
        )

    def _plan_and_enter_stage1(self, conductor: QAConductor):
        state = conductor.plan(self._new_feature_inputs())
        state = conductor.advance(state.run_id)
        self.assertEqual(state.current_phase, Phase.SENIOR_QA_BRAIN.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        return state

    def _complete_stage1(self, conductor: QAConductor, state, *, missing_ui_marker: bool = False):
        analysis_path = self._write_temp_file("artifacts/analysis_report.md", self._sample_analysis_report())
        textcases_path = self._write_temp_file(
            "artifacts/textcases.md",
            self._sample_textcases(missing_ui_marker=missing_ui_marker),
        )
        return conductor.complete_phase(
            state.run_id,
            Phase.SENIOR_QA_BRAIN.value,
            {"analysis_report": analysis_path, "textcases": textcases_path},
        )

    def _complete_stage2(self, conductor: QAConductor, state, *, with_outcomes: bool = True):
        if with_outcomes:
            script_path = self._write_temp_file(
                "generated/test_car_list_cards.py",
                "def test_card_layout():\n    assert True\n",
            )
            outcome_payload = (
                "[\n"
                "  {\n"
                '    "tc_id": "TC001",\n'
                '    "outcome": "script_generated",\n'
                f'    "script_path": "{script_path}",\n'
                '    "collect_only_passed": true,\n'
                '    "pytest_passed": true\n'
                "  }\n"
                "]\n"
            )
        else:
            outcome_payload = "[]\n"
        outcomes_path = self._write_temp_file("artifacts/playwright_case_outcomes.json", outcome_payload)
        return conductor.complete_phase(
            state.run_id,
            Phase.PLAYWRIGHT_GENERATOR.value,
            {"playwright_case_outcomes": outcomes_path},
        )

    def _reach_kb_phase(self, conductor: QAConductor):
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)
        state = self._complete_stage2(conductor, state)
        self.assertEqual(state.current_phase, Phase.IMPACT_VERIFICATION.value)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        self.assertEqual(state.current_phase, Phase.OK_UI_REGRESSION.value)
        dry_run_path = self._write_temp_file("artifacts/ok_ui_dry_run.md", "# dry run\n\n- test_cases/car/test_card.py\n")
        report_path = self._write_temp_file("artifacts/ok_ui_report.md", "# 回归结果\n\n- passed: 1/1\n")
        recommendation_path = self._write_temp_file("artifacts/release_recommendation.md", "建议上线\n")
        state = conductor.complete_phase(
            state.run_id,
            Phase.OK_UI_REGRESSION.value,
            {
                "ok_ui_dry_run_preview": dry_run_path,
                "ok_ui_execution_report": report_path,
                "release_recommendation": recommendation_path,
            },
        )
        self.assertEqual(state.current_phase, Phase.KNOWLEDGE_BASE_UPDATE.value)
        return state

    def test_plan_requires_explicit_mode(self) -> None:
        conductor = self._make_conductor()
        with self.assertRaises(ValueError):
            conductor.plan({"module": "car", "site": "ae", "change_description": "列表卡片样式调整"})

    def test_stage1_gate_writes_kb_draft_and_manifest(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)
        manifest = read_json(state.artifacts["text_case_manifest"], default={})
        self.assertEqual(manifest["module"], "car")
        self.assertEqual(len(manifest["cases"]), 2)
        kb_draft = Path(state.artifacts["kb_text_case_draft_path"])
        self.assertTrue(kb_draft.exists())
        self.assertEqual(kb_draft.parent, self.kb_root / "文本用例" / "test_car")
        self.assertIn("TC001", read_text(kb_draft))
        gate = read_json(state.artifacts["phase1_gate_result"], default={})
        self.assertTrue(gate["ok"])

    def test_stage1_gate_blocks_when_ui_automation_marker_missing(self) -> None:
        conductor = self._make_conductor()
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state, missing_ui_marker=True)
        self.assertEqual(state.current_phase, Phase.SENIOR_QA_BRAIN.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        gate = read_json(state.artifacts["phase1_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("UI自动化", " ".join(gate["blocking_reasons"]))

    def test_stage2_gate_blocks_when_automatable_case_has_no_outcome(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2(conductor, state, with_outcomes=False)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        gate = read_json(state.artifacts["phase2_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("唯一 outcome", " ".join(gate["blocking_reasons"]))

    def test_stage2_gate_success_generates_script_manifest_and_enters_impact_verification(self) -> None:
        impact_executor = FakeImpactVerificationExecutor(self._passed_verification_outcome())
        conductor = self._make_conductor(impact_executor=impact_executor)
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2(conductor, state, with_outcomes=True)
        self.assertEqual(state.current_phase, Phase.IMPACT_VERIFICATION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertIn("generated_scripts_manifest", state.artifacts)
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
        retry_task = LegacyUpdateTask(
            task_id=base_task.task_id,
            target_script=base_task.target_script,
            target_nodeid=base_task.target_nodeid,
            recommended_action=base_task.recommended_action,
            status=LegacyUpdateTaskStatus.RETRY.value,
            attempts=1,
        )
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

    def test_kb_update_context_binds_stage1_draft_path(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._reach_kb_phase(conductor)
        instruction = read_text(state.artifacts[f"{Phase.KNOWLEDGE_BASE_UPDATE.value}_instruction"])
        context = read_text(state.artifacts["knowledge_base_update_context"])
        self.assertIn("kb_text_case_draft_path", context)
        self.assertIn(state.artifacts["kb_text_case_draft_path"], context)
        self.assertIn("优先读取并回写该路径", instruction)

    def test_complete_knowledge_base_update_requires_preview_and_result_then_finishes(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._reach_kb_phase(conductor)
        state = conductor.complete_phase(state.run_id, Phase.KNOWLEDGE_BASE_UPDATE.value)
        self.assertEqual(state.current_phase, Phase.KNOWLEDGE_BASE_UPDATE.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        preview_path = self._write_temp_file("artifacts/kb_preview.md", "# KB Preview\n\n- 更新文本用例\n")
        result_path = self._write_temp_file("artifacts/kb_result.json", '{"written": true}\n')
        state = conductor.complete_phase(
            state.run_id,
            Phase.KNOWLEDGE_BASE_UPDATE.value,
            {
                "knowledge_base_update_preview": preview_path,
                "knowledge_base_update_result": result_path,
            },
        )
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


if __name__ == "__main__":
    unittest.main()
