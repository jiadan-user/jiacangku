from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qa_agent.adapters.impact_verification import ImpactVerificationExecutor
from qa_agent.adapters.legacy_update import LegacyUpdateExecutor, LegacyUpdateValidator
from qa_agent.config import _resolve_nested_paths, load_config
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
    PlaywrightCaseOutcome,
    RunState,
    RunStatus,
    ValidationResult,
)


class FakeImpactVerificationExecutor:
    def __init__(self, outcome: ImpactVerificationOutcome) -> None:
        self.outcome = outcome
        self.calls = 0

    def verify(self, *, run_dir: Path, packet: dict, impact_payload: dict) -> ImpactVerificationOutcome:
        del run_dir, packet, impact_payload
        self.calls += 1
        return self.outcome


class RaisingImpactVerificationExecutor:
    def verify(self, *, run_dir: Path, packet: dict, impact_payload: dict) -> ImpactVerificationOutcome:
        del run_dir, packet, impact_payload
        raise RuntimeError("boom")


class FakeLegacyUpdateExecutor:
    def __init__(
        self,
        outcomes: list[LegacyUpdateRoundOutcome],
        refresh_result: dict | None = None,
    ) -> None:
        self.outcomes = outcomes
        self.calls = 0
        self.refresh_result = refresh_result
        self.refresh_calls = 0

    def run_round(self, *, run_dir: Path, tasks: list[LegacyUpdateTask], round_index: int) -> LegacyUpdateRoundOutcome:
        del run_dir, tasks, round_index
        outcome = self.outcomes[min(self.calls, len(self.outcomes) - 1)]
        self.calls += 1
        return outcome

    def refresh_catalog_after_script_changes(self, tasks: list[LegacyUpdateTask]) -> dict:
        del tasks
        self.refresh_calls += 1
        return self.refresh_result or {
            "needed": False,
            "ok": True,
            "changed_task_ids": [],
            "promotion_task_ids": [],
            "legacy_task_ids": [],
        }


class AlwaysPassLegacyValidator(LegacyUpdateValidator):
    def validate(self, candidate_path: Path, task: LegacyUpdateTask) -> list[ValidationResult]:
        del candidate_path, task
        return [ValidationResult(ok=True, name="fake", message="ok")]


class RecordingRefreshLegacyUpdateExecutor(LegacyUpdateExecutor):
    def __init__(self, config) -> None:
        super().__init__(config, validator=AlwaysPassLegacyValidator())
        self.refresh_commands: list[str] = []

    def _run_refresh_command(self, name: str, command_fn) -> dict:
        del command_fn
        self.refresh_commands.append(name)
        return {"name": name, "ok": True, "returncode": 0, "stdout": "", "stderr": ""}


class ConductorSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.kb_root = self.temp_path / "knowledge_base"
        (self.kb_root / "文本用例").mkdir(parents=True, exist_ok=True)
        (self.kb_root / "业务规则库" / "车辆模块").mkdir(parents=True, exist_ok=True)
        self.regression_root = self.temp_path / "regression_project"
        (self.regression_root / "test_cases").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _make_conductor(self, legacy_executor=None, impact_executor=None) -> QAConductor:
        root = Path(__file__).resolve().parents[1]
        config = load_config(root)
        config.skills["paths"]["knowledge_base_root"] = str(self.kb_root)
        config.skills["paths"]["regression_project_root"] = str(self.regression_root)
        config.skills["paths"]["agent_memory_root"] = str(self.temp_path / ".agent_memory")
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

    def _mixed_inputs(self) -> dict[str, str]:
        return {
            "change_mode": ChangeMode.MIXED.value,
            "figma_url": "https://www.figma.com/design/demo",
            "site": "ae",
            "module": "car",
            "feature": "列表",
            "change_description": "列表卡片样式改大卡",
        }

    def _sample_analysis_report(self) -> str:
        return (
            "# 列表测试分析报告\n\n"
            "## 知识库依据\n"
            "- bundled/knowledge_base/业务规则库/车辆模块/车辆列表页规则.md\n\n"
            "- 风险点: 卡片布局、字段展示、跳转入口\n"
        )

    def _sample_textcases(
        self,
        *,
        missing_ui_marker: bool = False,
        missing_business_sections: bool = False,
        vague_preconditions: bool = False,
    ) -> str:
        ui_line = "" if missing_ui_marker else "- **UI自动化**: ✅ 可自动化\n"
        business_sections = (
            "## 业务属性\n"
            "- 业务域: 车辆业务域\n"
            "- 模块: 车辆列表\n"
            "- 功能: 列表卡片展示\n"
            "- 用户角色: 访客\n"
            "- 入口位置: 首页 Cars 图标 / Browse 菜单\n"
            "- 知识库依据: bundled/knowledge_base/业务规则库/车辆模块/车辆列表页规则.md\n\n"
            "## 测试范围\n"
            "- 覆盖范围: AE 站车辆列表首屏卡片展示\n"
            "- 不覆盖范围: 支付、第三方授权\n\n"
        )
        if missing_business_sections:
            business_sections = ""
        tc001_precondition = (
            "- 已进入车列表页\n"
            if vague_preconditions
            else "- 访客身份，无需登录；打开 https://ae.example.com/en/city-abu-dhabi/cate-car/?iconSource=car；确认页面标题含 Cars 且筛选栏可见\n"
        )
        return (
            "# OK-AE-Car-列表-测试用例\n\n"
            "## 测试环境配置（必填）\n\n"
            "| 字段 | 值 | 说明 |\n"
            "| --- | --- | --- |\n"
            "| 站点 | ae | 站点 |\n"
            "| 基础URL | https://ae.example.com/car | 基础地址 |\n"
            "| 角色 | visitor | 角色 |\n\n"
            f"{business_sections}"
            "## 测试用例\n\n"
            "### TC001: 车列表大卡样式展示\n\n"
            "#### 📋 前置条件\n"
            f"{tc001_precondition}\n"
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
            "- 访客身份，无需登录；打开 https://ae.example.com/en/city-abu-dhabi/cate-car/?iconSource=car\n\n"
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

    def test_plan_attaches_memory_context_artifact(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan(self._new_feature_inputs())

        self.assertIn("memory_context", state.artifacts)
        self.assertTrue(Path(state.artifacts["memory_context"]).exists())
        self.assertIn("Usage Rule", read_text(state.artifacts["memory_context"]))

    def _complete_stage1(
        self,
        conductor: QAConductor,
        state,
        *,
        missing_ui_marker: bool = False,
        analysis_text: str | None = None,
        textcases_text: str | None = None,
    ):
        analysis_path = self._write_temp_file("artifacts/analysis_report.md", analysis_text or self._sample_analysis_report())
        textcases_path = self._write_temp_file(
            "artifacts/textcases.md",
            textcases_text or self._sample_textcases(missing_ui_marker=missing_ui_marker),
        )
        return conductor.complete_phase(
            state.run_id,
            Phase.SENIOR_QA_BRAIN.value,
            {"analysis_report": analysis_path, "textcases": textcases_path},
        )

    def _complete_stage2_recording(
        self,
        conductor: QAConductor,
        state,
        *,
        with_outcomes: bool = True,
        missing_proof: bool = False,
        bug_recorded: bool = False,
        missing_bug_report: bool = False,
        manual_review: bool = False,
        missing_global_bug_report: bool = False,
    ):
        bug_path = ""
        if with_outcomes:
            if manual_review:
                outcome_payload = (
                    "[\n"
                    "  {\n"
                    '    "tc_id": "TC001",\n'
                    '    "outcome": "manual_review",\n'
                    '    "manual_review_reason": "needs product decision"\n'
                    "  }\n"
                    "]\n"
                )
            elif bug_recorded:
                bug_path = (
                    str(self.temp_path / "missing_bug_report.md")
                    if missing_bug_report
                    else self._write_temp_file("artifacts/playwright_bug_report.md", "## TC001: bug\n")
                )
                outcome_payload = (
                    "[\n"
                    "  {\n"
                    '    "tc_id": "TC001",\n'
                    '    "outcome": "bug_recorded",\n'
                    f'    "bug_report_path": "{bug_path}"\n'
                    "  }\n"
                    "]\n"
                )
            else:
                proof_path = (
                    str(self.temp_path / "missing_proof.md")
                    if missing_proof
                    else self._write_temp_file("artifacts/proof_tc001.md", "# proof\n")
                )
                trace_path = self._write_temp_file("artifacts/recording_trace_tc001.json", "{}\n")
                outcome_payload = (
                    "[\n"
                    "  {\n"
                    '    "tc_id": "TC001",\n'
                    '    "outcome": "recording_passed",\n'
                    f'    "proof_artifact_path": "{proof_path}",\n'
                    f'    "details": {{"recording_trace_path": "{trace_path}"}}\n'
                    "  }\n"
                    "]\n"
                )
        else:
            outcome_payload = "[]\n"
        outcomes_path = self._write_temp_file("artifacts/playwright_recording_outcomes.json", outcome_payload)
        report_path = self._write_temp_file("artifacts/playwright_recording_report.md", "# recording report\n")
        if missing_global_bug_report:
            global_bug_report = str(self.temp_path / "missing_global_bug_report.md")
        elif bug_recorded and not missing_bug_report:
            global_bug_report = bug_path
        else:
            global_bug_report = self._write_temp_file("artifacts/playwright_bug_report.md", "本轮未发现 bug\n")
        artifacts = {
            "playwright_recording_outcomes": outcomes_path,
            "playwright_recording_report": report_path,
            "playwright_bug_report": global_bug_report,
        }
        if bug_recorded and not missing_bug_report:
            artifacts["playwright_bug_report"] = bug_path
        return conductor.complete_phase(
            state.run_id,
            Phase.PLAYWRIGHT_GENERATOR.value,
            artifacts,
        )

    def _confirm_stage2_recording(self, conductor: QAConductor, state):
        return conductor.complete_phase(state.run_id, Phase.PLAYWRIGHT_GENERATOR.value)

    def _complete_stage2_scripts(
        self,
        conductor: QAConductor,
        state,
        *,
        with_outcomes: bool = True,
        script_blocked: bool = False,
    ):
        if with_outcomes:
            if script_blocked:
                blocker_path = self._write_temp_file("artifacts/script_blocker_report.md", "# blocked\n")
                outcome_payload = (
                    "[\n"
                    "  {\n"
                    '    "tc_id": "TC001",\n'
                    '    "outcome": "script_blocked",\n'
                    f'    "script_blocker_report_path": "{blocker_path}"\n'
                    "  }\n"
                    "]\n"
                )
            else:
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

    def _complete_stage2(self, conductor: QAConductor, state, *, with_outcomes: bool = True):
        state = self._complete_stage2_recording(conductor, state, with_outcomes=with_outcomes)
        if not with_outcomes or state.status == RunStatus.BLOCKED.value and state.next_action.kind != "confirm_phase":
            return state
        state = self._confirm_stage2_recording(conductor, state)
        if state.current_phase != Phase.PLAYWRIGHT_GENERATOR.value:
            return state
        return self._complete_stage2_scripts(conductor, state, with_outcomes=with_outcomes)

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

    def test_drive_to_action_stops_at_first_skill_with_next_action(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan(self._new_feature_inputs())
        state = conductor.drive_to_action(state.run_id)
        self.assertEqual(state.current_phase, Phase.SENIOR_QA_BRAIN.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.next_action.kind, "run_skill")
        self.assertEqual(state.next_action.required_artifacts, ["analysis_report", "textcases"])
        self.assertIn("complete", state.next_action.resume_command)

    def test_stage1_instruction_includes_rule_library_paths(self) -> None:
        conductor = self._make_conductor()
        state = self._plan_and_enter_stage1(conductor)
        instruction = read_text(state.artifacts[f"{Phase.SENIOR_QA_BRAIN.value}_instruction"])
        self.assertIn("业务规则库读取要求", instruction)
        self.assertIn(str(self.kb_root / "业务规则库" / "车辆模块"), instruction)

    def test_stage1_instruction_reports_rule_library_miss(self) -> None:
        conductor = self._make_conductor()
        conductor.config.knowledge_base_routing["rule_library_routes"].pop("car", None)
        state = conductor.plan(self._new_feature_inputs())
        state = conductor.advance(state.run_id)
        instruction = read_text(state.artifacts[f"{Phase.SENIOR_QA_BRAIN.value}_instruction"])
        self.assertIn("规则库未命中", instruction)
        self.assertIn("不要编造业务规则", instruction)

    def test_stage1_gate_writes_kb_draft_and_manifest(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)
        manifest = read_json(state.artifacts["text_case_manifest"], default={})
        self.assertEqual(manifest["module"], "car")
        self.assertEqual(len(manifest["cases"]), 2)
        self.assertEqual(manifest["business_attributes"][0], "业务域: 车辆业务域")
        self.assertIn(str(self.kb_root / "业务规则库" / "车辆模块"), manifest["rule_library_paths"])
        kb_draft = Path(state.artifacts["kb_text_case_draft_path"])
        self.assertTrue(kb_draft.exists())
        self.assertEqual(kb_draft.parent, self.kb_root / "文本用例" / "test_car")
        self.assertIn("TC001", read_text(kb_draft))
        gate = read_json(state.artifacts["phase1_gate_result"], default={})
        self.assertTrue(gate["ok"])

    def test_stage1_gate_keeps_nested_bucket_relative_to_kb_text_root(self) -> None:
        conductor = self._make_conductor()
        packet = {"candidate_modules": ["homepage"], "site": "ae", "feature_name": "首页"}
        bucket = conductor._knowledge_base_bucket(packet)
        self.assertEqual(bucket, "Tiyan/首页")
        path = conductor._knowledge_base_draft_path(packet, "textcases.md", bucket)
        self.assertEqual(path.parent, self.kb_root / "文本用例" / "Tiyan" / "首页")

    def test_stage1_gate_blocks_absolute_text_case_bucket(self) -> None:
        conductor = self._make_conductor()
        conductor.config.knowledge_base_routing["text_case_buckets"]["car"]["bucket"] = str(self.temp_path / "outside")
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        gate = read_json(state.artifacts["phase1_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("bucket 必须是相对路径片段", " ".join(gate["blocking_reasons"]))

    def test_stage1_gate_blocks_when_ui_automation_marker_missing(self) -> None:
        conductor = self._make_conductor()
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state, missing_ui_marker=True)
        self.assertEqual(state.current_phase, Phase.SENIOR_QA_BRAIN.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        gate = read_json(state.artifacts["phase1_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("UI自动化", " ".join(gate["blocking_reasons"]))

    def test_stage1_gate_blocks_when_analysis_report_lacks_kb_basis(self) -> None:
        conductor = self._make_conductor()
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state, analysis_text="# 列表测试分析报告\n\n- 风险点: 卡片布局\n")
        gate = read_json(state.artifacts["phase1_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("知识库依据", " ".join(gate["blocking_reasons"]))

    def test_stage1_gate_blocks_when_business_sections_missing(self) -> None:
        conductor = self._make_conductor()
        state = self._plan_and_enter_stage1(conductor)
        textcases = self._sample_textcases(missing_business_sections=True)
        state = self._complete_stage1(conductor, state, textcases_text=textcases)
        gate = read_json(state.artifacts["phase1_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("业务属性", " ".join(gate["blocking_reasons"]))
        self.assertIn("测试范围", " ".join(gate["blocking_reasons"]))

    def test_stage1_gate_blocks_vague_automatable_preconditions(self) -> None:
        conductor = self._make_conductor()
        state = self._plan_and_enter_stage1(conductor)
        textcases = self._sample_textcases(vague_preconditions=True)
        state = self._complete_stage1(conductor, state, textcases_text=textcases)
        gate = read_json(state.artifacts["phase1_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("前置条件不可执行", " ".join(gate["blocking_reasons"]))

    def test_stage2_gate_blocks_when_automatable_case_has_no_outcome(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2(conductor, state, with_outcomes=False)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        gate = read_json(state.artifacts["phase2_recording_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("recording outcome", " ".join(gate["blocking_reasons"]))
        self.assertEqual(gate["details"]["missing_case_ids"], ["TC001"])

    def test_stage2a_success_waits_for_confirmation_before_script_generation(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2_recording(conductor, state)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.next_action.kind, "confirm_phase")
        self.assertIn("proof_artifacts_manifest", state.artifacts)
        self.assertNotIn("generated_scripts_manifest", state.artifacts)

    def test_stage2a_blocks_when_recording_passed_missing_proof(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2_recording(conductor, state, missing_proof=True)
        gate = read_json(state.artifacts["phase2_recording_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("proof_artifact_path", " ".join(gate["blocking_reasons"]))

    def test_stage2a_blocks_when_bug_recorded_missing_bug_report(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2_recording(
            conductor,
            state,
            bug_recorded=True,
            missing_bug_report=True,
        )
        gate = read_json(state.artifacts["phase2_recording_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("可追溯的 bug 记录", " ".join(gate["blocking_reasons"]))

    def test_stage2a_blocks_when_bug_report_missing_even_without_bugs(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2_recording(conductor, state, missing_global_bug_report=True)
        gate = read_json(state.artifacts["phase2_recording_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("playwright_bug_report.md", " ".join(gate["blocking_reasons"]))

    def test_stage2a_blocks_when_manual_review_outcome_is_used(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2_recording(conductor, state, manual_review=True)
        gate = read_json(state.artifacts["phase2_recording_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("manual_review", " ".join(gate["blocking_reasons"]))

    def test_stage2a_confirmation_requests_stage2b_script_outcomes(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2_recording(conductor, state)
        state = self._confirm_stage2_recording(conductor, state)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.next_action.kind, "run_skill")
        self.assertEqual(state.next_action.required_artifacts, ["playwright_case_outcomes"])

    def test_stage2b_auto_skips_when_no_recording_passed_cases(self) -> None:
        impact_executor = FakeImpactVerificationExecutor(self._passed_verification_outcome())
        conductor = self._make_conductor(impact_executor=impact_executor)
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2_recording(conductor, state, bug_recorded=True)
        state = self._confirm_stage2_recording(conductor, state)
        self.assertEqual(state.current_phase, Phase.IMPACT_VERIFICATION.value)
        self.assertIn("generated_scripts_manifest", state.artifacts)
        self.assertIn("stage2b_conversion_metrics", state.artifacts)
        self.assertEqual(read_json(state.artifacts["generated_scripts_manifest"], default=None), [])
        self.assertEqual(read_json(state.artifacts["playwright_case_outcomes"], default=None), [])
        metrics = read_json(state.artifacts["stage2b_conversion_metrics"], default={})
        self.assertEqual(metrics["eligible_count"], 0)
        self.assertIsNone(metrics["success_rate"])
        self.assertEqual(metrics["round_count"], 0)
        self.assertEqual(impact_executor.calls, 1)

    def test_stage2b_blocks_when_script_generation_not_closed(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2_recording(conductor, state)
        state = self._confirm_stage2_recording(conductor, state)
        state = self._complete_stage2_scripts(conductor, state, script_blocked=True)
        self.assertEqual(state.current_phase, Phase.PLAYWRIGHT_GENERATOR.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        gate = read_json(state.artifacts["phase2_gate_result"], default={})
        self.assertFalse(gate["ok"])
        self.assertIn("script_blocked", read_text(state.artifacts["playwright_case_outcomes"]))

    def test_stage2_gate_success_generates_script_manifest_and_enters_impact_verification(self) -> None:
        impact_executor = FakeImpactVerificationExecutor(self._passed_verification_outcome())
        conductor = self._make_conductor(impact_executor=impact_executor)
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2(conductor, state, with_outcomes=True)
        self.assertEqual(state.current_phase, Phase.IMPACT_VERIFICATION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertIn("generated_scripts_manifest", state.artifacts)
        self.assertIn("stage2b_conversion_metrics", state.artifacts)
        metrics = read_json(state.artifacts["stage2b_conversion_metrics"], default={})
        self.assertEqual(metrics["eligible_count"], 1)
        self.assertEqual(metrics["converted_count"], 1)
        self.assertEqual(metrics["success_rate"], 1.0)
        self.assertIsNone(metrics["round_count"])
        self.assertEqual(impact_executor.calls, 1)

    def test_stage2b_conversion_metrics_records_one_round_success(self) -> None:
        conductor = self._make_conductor()
        outcomes = [
            PlaywrightCaseOutcome(
                tc_id=f"TC{idx:03d}",
                outcome="script_generated",
                script_path=f"/tmp/test_{idx}.py",
                collect_only_passed=True,
                pytest_passed=True,
                details={
                    "first_success_round": 1,
                    "attempts": [{"round": 1, "collect_only_passed": True, "pytest_passed": True}],
                },
            )
            for idx in range(1, 11)
        ]

        metrics = conductor._build_stage2b_conversion_metrics([f"TC{idx:03d}" for idx in range(1, 11)], outcomes)

        self.assertEqual(metrics["converted_count"], 10)
        self.assertEqual(metrics["success_rate"], 1.0)
        self.assertEqual(metrics["round_count"], 1)
        self.assertEqual(metrics["rounds"][0]["attempted_count"], 10)
        self.assertEqual(metrics["rounds"][0]["cumulative_success_rate"], 1.0)

    def test_stage2b_conversion_metrics_records_cumulative_second_round_success(self) -> None:
        conductor = self._make_conductor()
        outcomes = []
        for idx in range(1, 11):
            if idx <= 6:
                attempts = [{"round": 1, "collect_only_passed": True, "pytest_passed": True}]
                first_success_round = 1
            else:
                attempts = [
                    {"round": 1, "collect_only_passed": True, "pytest_passed": False, "failure_reason": "pytest failed"},
                    {"round": 2, "collect_only_passed": True, "pytest_passed": True, "fix_summary": "fixed assertion"},
                ]
                first_success_round = 2
            outcomes.append(
                PlaywrightCaseOutcome(
                    tc_id=f"TC{idx:03d}",
                    outcome="script_generated",
                    script_path=f"/tmp/test_{idx}.py",
                    collect_only_passed=True,
                    pytest_passed=True,
                    details={"first_success_round": first_success_round, "attempts": attempts},
                )
            )

        metrics = conductor._build_stage2b_conversion_metrics([f"TC{idx:03d}" for idx in range(1, 11)], outcomes)

        self.assertEqual(metrics["converted_count"], 10)
        self.assertEqual(metrics["success_rate"], 1.0)
        self.assertEqual(metrics["round_count"], 2)
        self.assertEqual(metrics["rounds"][0]["attempted_count"], 10)
        self.assertEqual(metrics["rounds"][0]["new_success_count"], 6)
        self.assertEqual(metrics["rounds"][0]["cumulative_success_rate"], 0.6)
        self.assertEqual(metrics["rounds"][1]["attempted_count"], 4)
        self.assertEqual(metrics["rounds"][1]["new_success_count"], 4)
        self.assertEqual(metrics["rounds"][1]["cumulative_success_rate"], 1.0)

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

    def test_complete_impact_verification_blocks_for_playwright_when_patch_is_missing(self) -> None:
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
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.phase_statuses[Phase.LEGACY_UPDATE.value], PhaseStatus.BLOCKED.value)
        self.assertEqual(state.next_action.kind, "run_skill")
        self.assertIn("playwright-test-generator", state.next_action.skill_path)
        self.assertEqual(state.next_action.required_artifacts, ["legacy_update_candidate_manifest"])
        request = read_json(state.artifacts["legacy_rerecord_request"], default={})
        self.assertEqual(request["tasks"][0]["recommended_action"], "re-record")
        self.assertEqual(legacy_executor.calls, 0)

    def test_drive_to_action_auto_consumes_legacy_retry_until_next_skill(self) -> None:
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
                    reason="断言不匹配",
                    next_action="更新断言",
                )
            ],
        )
        retry_task = LegacyUpdateTask(
            task_id="legacy-1",
            target_script="/tmp/test_wallet.py",
            target_nodeid="test_cases/wallet/test_wallet.py::test_xxx",
            recommended_action="promote-new-script",
            status=LegacyUpdateTaskStatus.RETRY.value,
            attempts=1,
            details={"replacement_text": "def test_xxx():\n    assert True\n"},
        )
        done_task = LegacyUpdateTask(
            task_id="legacy-1",
            target_script="/tmp/test_wallet.py",
            target_nodeid="test_cases/wallet/test_wallet.py::test_xxx",
            recommended_action="promote-new-script",
            status=LegacyUpdateTaskStatus.COMPLETED.value,
            attempts=2,
            details={"replacement_text": "def test_xxx():\n    assert True\n"},
        )
        legacy_executor = FakeLegacyUpdateExecutor(
            [
                LegacyUpdateRoundOutcome(
                    tasks=[retry_task],
                    gate=LegacyUpdateGate(round_index=1, total_count=1, retry_count=1),
                    results=[],
                ),
                LegacyUpdateRoundOutcome(
                    tasks=[done_task],
                    gate=LegacyUpdateGate(round_index=2, total_count=1, completed_count=1, all_completed=True),
                    results=[],
                ),
            ]
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
        state = conductor.drive_to_action(state.run_id)
        seed_path = self._write_temp_file(
            "artifacts/legacy_update_tasks_seed.json",
            "["
            '{"task_id":"legacy-1",'
            '"target_script":"/tmp/test_wallet.py",'
            '"target_nodeid":"test_cases/wallet/test_wallet.py::test_xxx",'
            '"recommended_action":"promote-new-script",'
            '"status":"pending",'
            '"details":{"replacement_text":"def test_xxx():\\n    assert True\\n"}}'
            "]",
        )
        state.artifacts["legacy_update_tasks_seed"] = seed_path
        conductor.store.save(state)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        self.assertEqual(state.current_phase, Phase.LEGACY_UPDATE.value)
        state = conductor.drive_to_action(state.run_id)
        self.assertEqual(state.current_phase, Phase.OK_UI_REGRESSION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertEqual(state.next_action.kind, "run_skill")
        self.assertEqual(legacy_executor.calls, 2)

    def test_script_change_requires_catalog_refresh_before_ok_ui(self) -> None:
        done_task = LegacyUpdateTask(
            task_id="promotion-1",
            target_script="/tmp/test_new_car.py",
            recommended_action="promote-new-script",
            status=LegacyUpdateTaskStatus.COMPLETED.value,
            impact_type="new-script-promotion",
        )
        legacy_executor = FakeLegacyUpdateExecutor(
            [
                LegacyUpdateRoundOutcome(
                    tasks=[done_task],
                    gate=LegacyUpdateGate(round_index=1, total_count=1, completed_count=1, all_completed=True),
                    results=[],
                )
            ],
            refresh_result={
                "needed": True,
                "ok": True,
                "changed_task_ids": ["promotion-1"],
                "promotion_task_ids": ["promotion-1"],
                "legacy_task_ids": [],
                "commands": {"catalog_build": {"ok": True}, "audit_identifiers": {"ok": True}},
            },
        )
        conductor = self._make_conductor(
            legacy_executor=legacy_executor,
            impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()),
        )
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "change_description": "新增车列表脚本",
            }
        )
        state = conductor.drive_to_action(state.run_id)
        seed_path = self._write_temp_file(
            "artifacts/legacy_update_tasks_seed.json",
            "[{"
            '"task_id":"promotion-1",'
            '"target_script":"/tmp/test_new_car.py",'
            '"recommended_action":"promote-new-script",'
            '"impact_type":"new-script-promotion",'
            '"status":"pending"'
            "}]",
        )
        state.artifacts["legacy_update_tasks_seed"] = seed_path
        conductor.store.save(state)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        state = conductor.drive_to_action(state.run_id)
        self.assertEqual(state.current_phase, Phase.OK_UI_REGRESSION.value)
        self.assertEqual(legacy_executor.refresh_calls, 1)
        self.assertIn("catalog_refresh_after_script_changes_round_01", state.artifacts)
        self.assertIn("catalog_refresh_after_promotion_round_01", state.artifacts)

    def test_script_change_blocks_when_catalog_refresh_fails(self) -> None:
        done_task = LegacyUpdateTask(
            task_id="promotion-1",
            target_script="/tmp/test_new_car.py",
            recommended_action="promote-new-script",
            status=LegacyUpdateTaskStatus.COMPLETED.value,
            impact_type="new-script-promotion",
        )
        legacy_executor = FakeLegacyUpdateExecutor(
            [
                LegacyUpdateRoundOutcome(
                    tasks=[done_task],
                    gate=LegacyUpdateGate(round_index=1, total_count=1, completed_count=1, all_completed=True),
                    results=[],
                )
            ],
            refresh_result={
                "needed": True,
                "ok": False,
                "changed_task_ids": ["promotion-1"],
                "promotion_task_ids": ["promotion-1"],
                "legacy_task_ids": [],
                "commands": {"catalog_build": {"ok": True}, "audit_identifiers": {"ok": False}},
            },
        )
        conductor = self._make_conductor(
            legacy_executor=legacy_executor,
            impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()),
        )
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "change_description": "新增车列表脚本",
            }
        )
        state = conductor.drive_to_action(state.run_id)
        seed_path = self._write_temp_file(
            "artifacts/legacy_update_tasks_seed.json",
            "[{"
            '"task_id":"promotion-1",'
            '"target_script":"/tmp/test_new_car.py",'
            '"recommended_action":"promote-new-script",'
            '"impact_type":"new-script-promotion",'
            '"status":"pending"'
            "}]",
        )
        state.artifacts["legacy_update_tasks_seed"] = seed_path
        conductor.store.save(state)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        state = conductor.drive_to_action(state.run_id)
        self.assertEqual(state.current_phase, Phase.LEGACY_UPDATE.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertIn("catalog refresh/audit", state.blocked_reason)

    def test_legacy_test_case_update_triggers_catalog_refresh(self) -> None:
        conductor = self._make_conductor()
        executor = RecordingRefreshLegacyUpdateExecutor(conductor.config)
        task = LegacyUpdateTask(
            task_id="legacy-1",
            target_script=str(self.regression_root / "test_cases" / "car" / "test_car_list.py"),
            recommended_action="update-assertion",
            status=LegacyUpdateTaskStatus.COMPLETED.value,
        )
        result = executor.refresh_catalog_after_script_changes([task])
        self.assertTrue(result["needed"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["changed_task_ids"], ["legacy-1"])
        self.assertEqual(result["legacy_task_ids"], ["legacy-1"])
        self.assertEqual(result["promotion_task_ids"], [])
        self.assertEqual(executor.refresh_commands, ["catalog_build", "audit_identifiers"])

    def test_non_test_case_update_does_not_refresh_catalog(self) -> None:
        conductor = self._make_conductor()
        executor = RecordingRefreshLegacyUpdateExecutor(conductor.config)
        task = LegacyUpdateTask(
            task_id="page-1",
            target_script=str(self.regression_root / "pages" / "car_page.py"),
            recommended_action="update-selector",
            status=LegacyUpdateTaskStatus.COMPLETED.value,
        )
        result = executor.refresh_catalog_after_script_changes([task])
        self.assertFalse(result["needed"])
        self.assertEqual(executor.refresh_commands, [])

    def test_legacy_update_candidate_manifest_resumes_loop_and_merges_candidate(self) -> None:
        target_script = self.regression_root / "test_cases" / "car" / "test_car_list.py"
        target_script.parent.mkdir(parents=True, exist_ok=True)
        target_script.write_text("def test_old():\n    assert False\n", encoding="utf-8")
        impact_outcome = ImpactVerificationOutcome(
            selector_plan={
                "module": "car",
                "site": "ae",
                "feature_name": "列表",
                "candidate_paths": [str(target_script)],
                "selectors": [{"kind": "path", "value": str(target_script)}],
                "nodeids": [f"{target_script}::test_old"],
                "case_ids": ["case_id_car_list"],
            },
            records=[
                ImpactVerificationRecord(
                    source_type="existing-script",
                    target=str(target_script),
                    module="car",
                    site="ae",
                    related_case_id="case_id_car_list",
                    related_nodeid=f"{target_script}::test_old",
                    run_status=ImpactRunStatus.FAILED.value,
                    category=AttributionCategory.LATEST_CHANGE.value,
                    summary="需要重新录制",
                    reason="旧脚本逻辑已不适配最新列表改动",
                    next_action="重录",
                )
            ],
        )
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(impact_outcome))
        conductor.legacy_update_executor = RecordingRefreshLegacyUpdateExecutor(conductor.config)
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "feature": "列表",
                "change_description": "列表卡片样式改大卡",
            }
        )
        state = conductor.drive_to_action(state.run_id)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        self.assertEqual(state.current_phase, Phase.LEGACY_UPDATE.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)

        tasks = read_json(state.artifacts["legacy_update_tasks"], default=[])
        candidate = self._write_temp_file("generated/re_recorded_car_list.py", "def test_new():\n    assert True\n")
        proof = self._write_temp_file("generated/re_recorded_car_list_proof.md", "# proof\n\n- collect-only passed\n")
        bad_manifest = self._write_temp_file(
            "generated/legacy_update_candidate_manifest_without_proof.json",
            "[{"
            f'"task_id": "{tasks[0]["task_id"]}", '
            f'"replacement_source_path": "{candidate}", '
            '"recommended_action": "re-record"'
            "}]",
        )
        state = conductor.complete_phase(
            state.run_id,
            Phase.LEGACY_UPDATE.value,
            {"legacy_update_candidate_manifest": bad_manifest},
        )
        self.assertEqual(state.current_phase, Phase.LEGACY_UPDATE.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertIn("proof_artifact_path", state.blocked_reason)

        manifest = self._write_temp_file(
            "generated/legacy_update_candidate_manifest.json",
            "[{"
            f'"task_id": "{tasks[0]["task_id"]}", '
            f'"replacement_source_path": "{candidate}", '
            f'"proof_artifact_path": "{proof}", '
            '"recommended_action": "re-record"'
            "}]",
        )
        state = conductor.complete_phase(
            state.run_id,
            Phase.LEGACY_UPDATE.value,
            {"legacy_update_candidate_manifest": manifest},
        )
        self.assertEqual(state.current_phase, Phase.OK_UI_REGRESSION.value)
        self.assertEqual(state.status, RunStatus.BLOCKED.value)
        self.assertIn("test_new", target_script.read_text(encoding="utf-8"))
        self.assertIn("catalog_refresh_after_script_changes_round_01", state.artifacts)

    def test_drive_to_action_records_error_state(self) -> None:
        conductor = self._make_conductor(impact_executor=RaisingImpactVerificationExecutor())
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "change_description": "列表卡片样式调整",
            }
        )
        state = conductor.drive_to_action(state.run_id)
        self.assertEqual(state.status, RunStatus.ERROR.value)
        self.assertEqual(state.next_action.kind, "error")
        self.assertIn("RuntimeError", state.error_reason)

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

    def test_plan_records_requested_multi_module_and_site_scope(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": ["wallet,car", "wallet"],
                "site": ["ae,sg"],
                "change_description": "多模块纯回归",
            }
        )
        packet = read_json(state.artifacts["requirement_packet"], default={})

        self.assertEqual(packet["candidate_modules"], ["wallet", "car"])
        self.assertEqual(packet["requested_modules"], ["wallet", "car"])
        self.assertEqual(packet["site"], "ae")
        self.assertEqual(packet["requested_sites"], ["ae", "sg"])

    def test_impact_split_is_idempotent_and_complete_uses_phase_value_key(self) -> None:
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = self._plan_and_enter_stage1(conductor)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2(conductor, state)
        self.assertIn(Phase.PLAYWRIGHT_GENERATOR.value, state.phase_statuses)
        self.assertNotIn("playwright-generator", state.phase_statuses)
        before = dict(state.phase_statuses)
        current_phase = state.current_phase
        state = conductor._phase_impact_split(state, state.change_mode)
        self.assertEqual(before[Phase.SENIOR_QA_BRAIN.value], state.phase_statuses[Phase.SENIOR_QA_BRAIN.value])
        self.assertEqual(current_phase, state.current_phase)

    def test_doctor_reports_warnings_without_fatal_for_missing_regression_env(self) -> None:
        conductor = self._make_conductor()
        result = conductor.doctor()
        self.assertFalse(result.has_fatal)
        self.assertTrue(any(check.severity == "warning" for check in result.checks))

    def test_doctor_reports_fatal_when_knowledge_base_manager_missing(self) -> None:
        conductor = self._make_conductor()
        conductor.config.skills["paths"]["knowledge_base_manager_root"] = str(self.temp_path / "missing-kb-manager")
        result = conductor.doctor()
        self.assertTrue(result.has_fatal)
        self.assertTrue(any(check.name == "knowledge_base_manager_root" for check in result.fatals))

    def test_config_path_resolution_preserves_venv_python_symlink(self) -> None:
        project_root = self.temp_path / "project"
        target_python = self.temp_path / "real" / "python3.13"
        link_python = project_root / "venv" / "bin" / "python"
        target_python.parent.mkdir(parents=True, exist_ok=True)
        link_python.parent.mkdir(parents=True, exist_ok=True)
        target_python.write_text("# fake interpreter\n", encoding="utf-8")
        link_python.symlink_to(target_python)

        resolved = Path(_resolve_nested_paths("venv/bin/python", project_root))

        self.assertEqual(resolved, link_python)
        self.assertTrue(resolved.is_symlink())
        self.assertNotEqual(resolved, target_python.resolve())

    def test_config_keeps_knowledge_base_routing_fragments_relative(self) -> None:
        config = load_config(Path(__file__).resolve().parents[1])
        buckets = config.knowledge_base_routing["text_case_buckets"]
        self.assertEqual(buckets["homepage"]["bucket"], "Tiyan/首页")
        self.assertEqual(buckets["property"]["bucket"], "Property/Basic/List")
        self.assertFalse(Path(buckets["homepage"]["bucket"]).is_absolute())
        self.assertFalse(Path(buckets["property"]["bucket"]).is_absolute())

    def test_impact_analysis_uses_scoped_reasons_not_generic_case_metadata(self) -> None:
        matching_script = self.regression_root / "test_cases" / "car" / "test_car_list.py"
        matching_script.parent.mkdir(parents=True, exist_ok=True)
        matching_script.write_text(
            "import pytest\n"
            "@pytest.mark.ae\n"
            "@pytest.mark.case_id_car_list\n"
            "def test_car_list_card():\n"
            "    assert True\n",
            encoding="utf-8",
        )
        unrelated_script = self.regression_root / "test_cases" / "wallet" / "test_wallet.py"
        unrelated_script.parent.mkdir(parents=True, exist_ok=True)
        unrelated_script.write_text(
            "import pytest\n"
            "@pytest.mark.case_id_wallet_balance\n"
            "def test_wallet_balance():\n"
            "    assert True\n",
            encoding="utf-8",
        )
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "feature": "列表",
                "change_description": "列表卡片样式改大卡",
            }
        )
        state = conductor.advance(state.run_id)
        candidates = read_json(state.artifacts["impact_candidates"], default={})
        targets = {item["target"] for item in candidates["existing_cases"]}
        self.assertIn(str(matching_script), targets)
        self.assertNotIn(str(unrelated_script), targets)
        reasons = candidates["existing_cases"][0]["details"]["impact_reasons"]
        self.assertIn("存在 case_id 元数据", reasons)

    def test_impact_analysis_groups_multiple_tests_in_one_script_candidate(self) -> None:
        script = self.regression_root / "test_cases" / "car" / "test_favorites_page_batch5.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(
            "import pytest\n"
            "@pytest.mark.car\n"
            "@pytest.mark.ae\n"
            "@pytest.mark.case_id_fav_tc001\n"
            "def test_fav_001():\n"
            "    assert True\n"
            "@pytest.mark.case_id_fav_tc002\n"
            "def test_fav_002():\n"
            "    assert True\n"
            "@pytest.mark.case_id_fav_tc003\n"
            "def test_fav_003():\n"
            "    assert True\n"
            "@pytest.mark.case_id_fav_tc004\n"
            "def test_fav_004():\n"
            "    assert True\n"
            "@pytest.mark.case_id_fav_tc005\n"
            "def test_fav_005():\n"
            "    assert True\n",
            encoding="utf-8",
        )
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car",
                "site": "ae",
                "change_description": "car favorites 纯回归",
            }
        )
        state = conductor.advance(state.run_id)
        candidates = read_json(state.artifacts["impact_candidates"], default={})

        self.assertEqual(len(candidates["existing_cases"]), 1)
        details = candidates["existing_cases"][0]["details"]
        self.assertEqual(details["match_count"], 5)
        self.assertEqual(len(details["matched_nodeids"]), 5)
        self.assertEqual(candidates["merged_regression_candidates"], [str(script)])

    def test_marketplace_order_impact_analysis_ignores_split_module_keywords(self) -> None:
        matching_script = self.regression_root / "test_cases" / "marketplace_order" / "test_order_flow_v2.py"
        matching_script.parent.mkdir(parents=True, exist_ok=True)
        matching_script.write_text(
            "import pytest\n"
            "@pytest.mark.case_id_order_flow_v2_tc001\n"
            "@pytest.mark.marketplace\n"
            "@pytest.mark.ae\n"
            "def test_checkout_core_elements():\n"
            "    assert True\n",
            encoding="utf-8",
        )
        unrelated_marketplace = self.regression_root / "test_cases" / "marketplace" / "test_ae_marketplace_list.py"
        unrelated_marketplace.parent.mkdir(parents=True, exist_ok=True)
        unrelated_marketplace.write_text(
            "import pytest\n"
            "@pytest.mark.case_id_marketplace_list_tc001\n"
            "@pytest.mark.marketplace\n"
            "@pytest.mark.ae\n"
            "def test_marketplace_list_cards():\n"
            "    assert True\n",
            encoding="utf-8",
        )
        unrelated_order = self.regression_root / "test_cases" / "ai" / "test_ai_order_copy.py"
        unrelated_order.parent.mkdir(parents=True, exist_ok=True)
        unrelated_order.write_text(
            "import pytest\n"
            "@pytest.mark.case_id_ai_order_copy_tc001\n"
            "@pytest.mark.ae\n"
            "def test_order_copy_is_visible():\n"
            "    assert True\n",
            encoding="utf-8",
        )

        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "marketplace_order",
                "site": "ae",
                "change_description": "marketplace_order纯回归",
            }
        )
        state = conductor.advance(state.run_id)
        candidates = read_json(state.artifacts["impact_candidates"], default={})
        targets = {item["target"] for item in candidates["existing_cases"]}

        self.assertEqual(targets, {str(matching_script)})
        reasons = candidates["existing_cases"][0]["details"]["impact_reasons"]
        self.assertIn("路径命中 module", reasons)
        self.assertIn("pytest marker 命中 site", reasons)

    def test_mixed_mode_keeps_new_and_regression_sources_in_selector_plan(self) -> None:
        existing_script = self.regression_root / "test_cases" / "car" / "test_car_list_existing.py"
        existing_script.parent.mkdir(parents=True, exist_ok=True)
        existing_script.write_text(
            "import pytest\n"
            "@pytest.mark.car\n"
            "@pytest.mark.case_id_car_list_existing\n"
            "def test_car_list_existing():\n"
            "    assert True\n",
            encoding="utf-8",
        )
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = conductor.plan(self._mixed_inputs())
        state = conductor.drive_to_action(state.run_id)
        state = self._complete_stage1(conductor, state)
        state = self._complete_stage2(conductor, state)
        candidates = read_json(state.artifacts["impact_candidates"], default={})
        source_groups = {
            item["source_group"]
            for item in [*candidates["new_cases"], *candidates["existing_cases"]]
        }
        self.assertIn("new_feature", source_groups)
        self.assertIn("regression", source_groups)

        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        selector_plan = read_json(state.artifacts["regression_selector_plan"], default={})
        selector_sources = {item["source_group"] for item in selector_plan["sources"]}
        self.assertIn("new_feature", selector_sources)
        self.assertIn("regression", selector_sources)

    def test_regression_selector_plan_expands_multi_scope_execution_tasks(self) -> None:
        car_script = self.regression_root / "test_cases" / "car" / "test_car_list.py"
        wallet_script = self.regression_root / "test_cases" / "wallet" / "test_wallet_balance.py"
        car_script.parent.mkdir(parents=True, exist_ok=True)
        wallet_script.parent.mkdir(parents=True, exist_ok=True)
        car_script.write_text(
            "import pytest\n"
            "@pytest.mark.car\n"
            "@pytest.mark.ae\n"
            "@pytest.mark.case_id_car_tc001\n"
            "def test_car_card():\n"
            "    assert True\n",
            encoding="utf-8",
        )
        wallet_script.write_text(
            "import pytest\n"
            "@pytest.mark.wallet\n"
            "@pytest.mark.sg\n"
            "@pytest.mark.case_id_wallet_tc001\n"
            "def test_wallet_balance():\n"
            "    assert True\n",
            encoding="utf-8",
        )
        conductor = self._make_conductor(impact_executor=FakeImpactVerificationExecutor(self._passed_verification_outcome()))
        state = conductor.plan(
            {
                "change_mode": ChangeMode.REGRESSION.value,
                "module": "car,wallet",
                "site": "ae,sg",
                "change_description": "car wallet 纯回归",
            }
        )
        state = conductor.drive_to_action(state.run_id)
        state = conductor.complete_phase(state.run_id, Phase.IMPACT_VERIFICATION.value)
        selector_plan = read_json(state.artifacts["regression_selector_plan"], default={})

        self.assertEqual(selector_plan["requested_modules"], ["car", "wallet"])
        self.assertEqual(selector_plan["requested_sites"], ["ae", "sg"])
        tasks = selector_plan["execution_tasks"]
        self.assertEqual([(task["module"], task["site"]) for task in tasks], [
            ("car", "ae"),
            ("car", "sg"),
            ("wallet", "ae"),
            ("wallet", "sg"),
        ])
        selected = {(task["module"], task["site"]): task["selected_count"] for task in tasks}
        self.assertGreater(selected[("car", "ae")], 0)
        self.assertGreater(selected[("wallet", "sg")], 0)
        self.assertEqual(selected[("car", "sg")], 0)
        self.assertEqual(selected[("wallet", "ae")], 0)

    def test_impact_verification_batches_matched_nodeids_in_one_pytest_call(self) -> None:
        script = self.regression_root / "test_cases" / "car" / "test_favorites_page_batch5.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("def test_fav_001():\n    assert True\n\ndef test_fav_002():\n    assert False\n", encoding="utf-8")
        nodeids = [f"{script}::test_fav_001", f"{script}::test_fav_002"]
        commands: list[list[str]] = []

        def fake_run_command(command, cwd=None, env=None, check=False):
            del cwd, env, check
            commands.append(list(command))
            junit_path = Path(command[command.index("--junitxml") + 1])
            junit_path.parent.mkdir(parents=True, exist_ok=True)
            junit_path.write_text(
                '<testsuite><testcase name="test_fav_001" />'
                '<testcase name="test_fav_002"><failure>boom</failure></testcase></testsuite>',
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 1, stdout="FAILED test_fav_002", stderr="")

        executor = ImpactVerificationExecutor(self._make_conductor().config)
        impact_payload = {
            "existing_cases": [
                {
                    "source_type": "existing-script",
                    "target": str(script),
                    "module": "car",
                    "site": "ae",
                    "source_group": "regression",
                    "reason": "路径命中 module",
                    "details": {
                        "matched_nodeids": nodeids,
                        "matched_case_ids": ["case_id_fav_tc001", "case_id_fav_tc002"],
                        "nodeid_case_ids": {
                            nodeids[0]: "case_id_fav_tc001",
                            nodeids[1]: "case_id_fav_tc002",
                        },
                    },
                }
            ]
        }

        with patch("qa_agent.adapters.impact_verification.run_command", side_effect=fake_run_command):
            outcome = executor.verify(
                run_dir=self.temp_path / "run",
                packet={
                    "change_mode": ChangeMode.REGRESSION.value,
                    "candidate_modules": ["car"],
                    "site": "ae",
                    "change_description": "favorites 改动",
                },
                impact_payload=impact_payload,
            )

        self.assertEqual(len(commands), 1)
        self.assertIn(nodeids[0], commands[0])
        self.assertIn(nodeids[1], commands[0])
        self.assertEqual(outcome.records[0].details["failed_nodeids"], [nodeids[1]])
        self.assertEqual(outcome.records[0].related_nodeid, nodeids[1])
        self.assertEqual(outcome.records[0].related_case_id, "case_id_fav_tc002")

    def test_status_warns_for_stale_blocked_without_changing_state(self) -> None:
        conductor = self._make_conductor()
        conductor.config.thresholds["gates"]["blocked_warn_after_seconds"] = 1
        state = conductor.plan(self._new_feature_inputs())
        state = conductor.drive_to_action(state.run_id)
        state.blocked_since = "2000-01-01T00:00:00+00:00"
        conductor.store.save(state)

        data = conductor.status(state.run_id)
        self.assertEqual(data["status"], RunStatus.BLOCKED.value)
        self.assertIn("stale_warning", data)

    def test_phase_timings_are_recorded_for_auto_and_blocked_phases(self) -> None:
        conductor = self._make_conductor()
        state = conductor.plan(self._new_feature_inputs())
        state = conductor.drive_to_action(state.run_id)

        timings = state.phase_timings
        self.assertEqual(timings[Phase.INTAKE.value]["last_status"], "completed")
        self.assertEqual(timings[Phase.IMPACT_SPLIT.value]["last_status"], "completed")
        self.assertEqual(timings[Phase.SENIOR_QA_BRAIN.value]["last_status"], "blocked")
        self.assertGreaterEqual(timings[Phase.SENIOR_QA_BRAIN.value]["attempts_count"], 1)
        self.assertTrue(timings[Phase.SENIOR_QA_BRAIN.value]["blocked_at"])

    def test_run_state_loads_legacy_payload_with_next_action_defaults(self) -> None:
        payload = {
            "run_id": "legacy",
            "status": RunStatus.PLANNED.value,
            "current_phase": Phase.INTAKE.value,
            "change_mode": ChangeMode.REGRESSION.value,
        }
        state = RunState(**payload)
        self.assertEqual(state.version, 0)
        self.assertEqual(state.next_action.kind, "")
        self.assertEqual(state.phase_timings, {})


if __name__ == "__main__":
    unittest.main()
