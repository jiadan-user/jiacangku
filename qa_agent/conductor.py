from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from qa_agent.adapters.dedupe_mapper import DedupeMapper
from qa_agent.adapters.promotion_guard import PromotionGuard
from qa_agent.adapters.script_normalizer import ScriptNormalizer
from qa_agent.adapters.ui_probe_enricher import UIProbeEnricher
from qa_agent.config import AppConfig
from qa_agent.exceptions import PhaseBlockedError
from qa_agent.integrations.ok_ui_skill import OkUISkillIntegration
from qa_agent.integrations.playwright_generator import PlaywrightGeneratorIntegration
from qa_agent.integrations.senior_qa_brain import SeniorQABrainIntegration
from qa_agent.io import read_json, write_json, write_text
from qa_agent.models import (
    CaseManifestEntry,
    CaseStatus,
    ChangeMode,
    ConductorPhase,
    GateReport,
    PhaseStatus,
    RequirementPacket,
    RunState,
    RunStatus,
    to_data,
)
from qa_agent.presentation import artifact_label, normalize_change_mode
from qa_agent.state import RunStore
from qa_agent.utils import read_if_exists, slugify


class QAConductor:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.store = RunStore(config.qa_state_root)
        skills_paths = config.skills.get("paths", {})
        commands = config.skills.get("commands", {})
        thresholds = config.thresholds.get("gates", {})
        promotion_cfg = config.thresholds.get("promotion", {})
        self.senior_qa = SeniorQABrainIntegration(skills_paths["senior_qa_brain_root"])
        self.playwright = PlaywrightGeneratorIntegration(skills_paths["playwright_test_generator_root"])
        self.ok_ui = OkUISkillIntegration(
            script_path=commands["ok_ui_skill"]["script"],
            project_root=skills_paths["regression_project_root"],
            venv_python=commands["ok_ui_skill"]["venv_python"],
        )
        self.probe_enricher = UIProbeEnricher()
        self.dedupe_mapper = DedupeMapper()
        self.normalizer = ScriptNormalizer(max_wait_ms=int(thresholds.get("max_wait_timeout_ms", 300)))
        self.guard = PromotionGuard(
            ok_ui_skill=self.ok_ui,
            max_wait_ms=int(thresholds.get("max_wait_timeout_ms", 300)),
            require_runtime_checks=True,
            keep_staging_files=bool(promotion_cfg.get("keep_staging_files", False)),
        )

    def plan(self, inputs: dict[str, Any]) -> RunState:
        self._validate_minimal_inputs(inputs)
        state = self._ensure_run(inputs)
        state = self._phase_intake(state, inputs)
        state = self._phase_impact_split(state, inputs)
        state.status = RunStatus.PLANNED.value
        self.store.save(state)
        return state

    def _validate_minimal_inputs(self, inputs: dict[str, Any]) -> None:
        has_figma = bool(inputs.get("figma_url"))
        has_diff = bool(inputs.get("git_diff_summary") or inputs.get("git_diff_file"))
        has_run_id = bool(inputs.get("run_id"))
        if not has_figma and not has_diff and not has_run_id:
            raise ValueError(
                "至少需要提供以下输入之一：\n"
                "  --figma-url / --figma链接（新需求场景）\n"
                "  --git-diff-file / --git-diff-summary（回归场景）\n"
                "  --run-id / --运行ID（恢复已有运行）"
            )

    def run(self, inputs: dict[str, Any]) -> RunState:
        self._validate_minimal_inputs(inputs)
        state = self._ensure_run(inputs)
        state = self._phase_intake(state, inputs)
        state = self._phase_impact_split(state, inputs)

        if state.change_mode in {ChangeMode.NEW_FEATURE_ONLY.value, ChangeMode.MIXED.value}:
            state = self._phase_analysis_bundle(state, inputs)
            state = self._phase_analysis_review(state, inputs)
            state = self._phase_testcase_gen(state, inputs)
            state = self._phase_ui_probe_enrich(state, inputs)
            state = self._phase_dedupe_map(state, inputs)
            state = self._phase_batch_plan(state)
            state = self._phase_readiness_gate(state)
            state = self._phase_proof_ingest(state, inputs)
            state = self._phase_codegen(state)
            state = self._phase_normalize(state)
            state = self._phase_promotion_guard(state)
            if inputs.get("auto_promote", True):
                state = self._phase_promote(state)

        if state.change_mode in {ChangeMode.REGRESSION_ONLY.value, ChangeMode.MIXED.value}:
            state = self._phase_regression_plan(state, inputs)
            if inputs.get("execute_regression", False):
                state = self._phase_regression_dry_run(state)
                if inputs.get("execute_real_run", False):
                    state = self._phase_regression_run(state)

        state = self._phase_gate_reports(state, inputs)
        state = self._phase_final_report(state)
        state.status = RunStatus.COMPLETED.value
        self.store.save(state)
        return state

    def resume(self, run_id: str, inputs: dict[str, Any]) -> RunState:
        inputs = dict(inputs)
        inputs["run_id"] = run_id
        state = self.store.load(run_id)
        artifact_to_input = {
            "analysis_report": "analysis_report",
            "testcases_raw": "testcases_raw",
            "testcases_enriched": "testcases_enriched",
            "probe_notes": "probe_notes",
            "proof_dir": "proof_dir",
            "visual_report": "visual_report",
            "ui_report": "ui_report",
            "api_report": "api_report",
        }
        for artifact_key, input_key in artifact_to_input.items():
            if not inputs.get(input_key) and state.artifacts.get(artifact_key):
                inputs[input_key] = state.artifacts[artifact_key]
        packet = read_json(state.artifacts.get("requirement_packet", ""), default={}) or {}
        if not inputs.get("figma_url") and packet.get("figma_url"):
            inputs["figma_url"] = packet["figma_url"]
        if not inputs.get("site") and packet.get("site"):
            inputs["site"] = packet["site"]
        if not inputs.get("module") and packet.get("candidate_modules"):
            inputs["module"] = packet["candidate_modules"][0]
        if not inputs.get("feature") and packet.get("feature_name"):
            inputs["feature"] = packet["feature_name"]
        if not inputs.get("change_mode") or inputs.get("change_mode") == "auto":
            inputs["change_mode"] = state.change_mode
        return self.run(inputs)

    def status(self, run_id: str) -> dict[str, Any]:
        state = self.store.load(run_id)
        return to_data(state)

    def promote(self, run_id: str) -> RunState:
        state = self.store.load(run_id)
        return self._phase_promote(state)

    def _ensure_run(self, inputs: dict[str, Any]) -> RunState:
        run_id = inputs.get("run_id")
        if run_id:
            state = self.store.load(run_id)
        else:
            provisional_mode = self._resolve_change_mode(inputs)
            state = self.store.create_run(provisional_mode)
        state.status = RunStatus.RUNNING.value
        self._register_input_artifacts(state, inputs)
        self.store.save(state)
        return state

    def _register_input_artifacts(self, state: RunState, inputs: dict[str, Any]) -> None:
        for key in [
            "analysis_report",
            "testcases_raw",
            "testcases_enriched",
            "probe_notes",
            "proof_dir",
            "visual_report",
            "ui_report",
            "api_report",
        ]:
            if inputs.get(key):
                state.artifacts[key] = str(inputs[key])

    def _resolve_change_mode(self, inputs: dict[str, Any]) -> str:
        explicit = normalize_change_mode(inputs.get("change_mode"))
        if explicit and explicit != "auto":
            return explicit
        has_figma = bool(inputs.get("figma_url"))
        has_diff = bool(inputs.get("git_diff_summary") or inputs.get("git_diff_file"))
        if has_figma and has_diff:
            return ChangeMode.MIXED.value
        if has_figma:
            return ChangeMode.NEW_FEATURE_ONLY.value
        return ChangeMode.REGRESSION_ONLY.value

    def _phase_intake(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        if state.artifacts.get("requirement_packet"):
            self._mark_phase(state, ConductorPhase.INTAKE, PhaseStatus.COMPLETED)
            return state
        self._mark_phase(state, ConductorPhase.INTAKE, PhaseStatus.RUNNING)
        requirement = RequirementPacket(
            change_mode=self._resolve_change_mode(inputs),
            figma_url=inputs.get("figma_url", ""),
            prd_refs=list(inputs.get("prd_refs", []) or []),
            git_diff_summary=self._load_git_diff(inputs),
            candidate_modules=[item for item in [inputs.get("module")] if item],
            site=inputs.get("site", ""),
            feature_name=inputs.get("feature", ""),
            risk_hints=list(inputs.get("risk_hints", []) or []),
            assumptions=["原型来源=Figma"],
        )
        path = self.store.artifact_path(state.run_id, "requirement_packet.json")
        write_json(path, asdict(requirement))
        state.artifacts["requirement_packet"] = str(path)
        state.change_mode = requirement.change_mode
        self._mark_phase(state, ConductorPhase.INTAKE, PhaseStatus.COMPLETED)
        return state

    def _phase_impact_split(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        self._mark_phase(state, ConductorPhase.IMPACT_SPLIT, PhaseStatus.RUNNING)
        state.change_mode = self._resolve_change_mode(inputs)
        write_json(self.store.artifact_path(state.run_id, "impact_split.json"), {"change_mode": state.change_mode})
        self._mark_phase(state, ConductorPhase.IMPACT_SPLIT, PhaseStatus.COMPLETED)
        return state

    def _phase_analysis_bundle(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        if state.artifacts.get("analysis_report"):
            self._mark_phase(state, ConductorPhase.ANALYSIS_BUNDLE, PhaseStatus.COMPLETED)
            return state
        self._mark_phase(state, ConductorPhase.ANALYSIS_BUNDLE, PhaseStatus.RUNNING)
        requirement = RequirementPacket(**read_json(state.artifacts["requirement_packet"]))
        bundle = self.senior_qa.prepare_analysis_bundle(self.store.run_dir(state.run_id), requirement)
        state.artifacts.update({"analysis_bundle": bundle["bundle_dir"], "analysis_next_step": bundle["next_step"]})
        self._block(state, ConductorPhase.ANALYSIS_BUNDLE, "等待 senior-qa-brain 分析报告产物")
        raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)

    def _phase_analysis_review(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        self._mark_phase(state, ConductorPhase.ANALYSIS_REVIEW, PhaseStatus.RUNNING)
        if not inputs.get("analysis_approved", False):
            self._block(state, ConductorPhase.ANALYSIS_REVIEW, "等待人工确认分析报告")
            raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)
        self._mark_phase(state, ConductorPhase.ANALYSIS_REVIEW, PhaseStatus.COMPLETED)
        return state

    def _phase_testcase_gen(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        if state.artifacts.get("testcases_raw"):
            self._mark_phase(state, ConductorPhase.TESTCASE_GEN, PhaseStatus.COMPLETED)
            return state
        self._mark_phase(state, ConductorPhase.TESTCASE_GEN, PhaseStatus.RUNNING)
        bundle = self.senior_qa.prepare_testcase_bundle(self.store.run_dir(state.run_id), state.artifacts["analysis_report"])
        state.artifacts.update({"testcase_bundle": bundle["bundle_dir"], "testcase_next_step": bundle["next_step"]})
        self._block(state, ConductorPhase.TESTCASE_GEN, "等待 senior-qa-brain 生成原始 Markdown 用例")
        raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)

    def _phase_ui_probe_enrich(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        if state.artifacts.get("testcases_enriched"):
            self._mark_phase(state, ConductorPhase.UI_PROBE_ENRICH, PhaseStatus.COMPLETED)
            return state
        self._mark_phase(state, ConductorPhase.UI_PROBE_ENRICH, PhaseStatus.RUNNING)
        result = self.probe_enricher.enrich(
            self.store.run_dir(state.run_id),
            state.artifacts["testcases_raw"],
            inputs.get("probe_notes") or state.artifacts.get("probe_notes"),
        )
        if result["status"] != "完成":
            state.artifacts["probe_checklist"] = result["probe_checklist_path"]
            self._block(state, ConductorPhase.UI_PROBE_ENRICH, "等待 UI Probe/MCP 实测补充")
            raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)
        state.artifacts["testcases_enriched"] = result["enriched_path"]
        state.artifacts["reality_diff"] = result["reality_diff_path"]
        self._mark_phase(state, ConductorPhase.UI_PROBE_ENRICH, PhaseStatus.COMPLETED)
        return state

    def _phase_dedupe_map(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        self._mark_phase(state, ConductorPhase.DEDUPE_MAP, PhaseStatus.RUNNING)
        output_path = self.store.artifact_path(state.run_id, "case_manifest.json")
        entries = self.dedupe_mapper.build_manifest(
            enriched_markdown_path=state.artifacts["testcases_enriched"],
            output_path=output_path,
            module=inputs.get("module") or self._default_module(state),
            site=inputs.get("site") or self._default_site(state),
            feature_key=inputs.get("feature") or self._default_feature(state),
            knowledge_base_root=self.config.skills["paths"]["knowledge_base_root"],
            regression_test_root=self.ok_ui.project_root / "test_cases",
        )
        state.artifacts["case_manifest"] = str(output_path)
        candidate_md = self._write_module_map_candidate(state.run_id, entries)
        state.artifacts["module_map_candidate"] = str(candidate_md)
        self._mark_phase(state, ConductorPhase.DEDUPE_MAP, PhaseStatus.COMPLETED)
        return state

    def _phase_batch_plan(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.BATCH_PLAN, PhaseStatus.RUNNING)
        entries = [CaseManifestEntry(**item) for item in read_json(state.artifacts["case_manifest"], default=[])]
        batches = self.playwright.build_batches(entries, max_cases=int(self.config.thresholds["batches"]["max_cases_per_batch"]))
        batch_path = self.store.artifact_path(state.run_id, "batch_plan.json")
        write_json(batch_path, [[asdict(entry) for entry in batch] for batch in batches])
        state.artifacts["batch_plan"] = str(batch_path)
        self._mark_phase(state, ConductorPhase.BATCH_PLAN, PhaseStatus.COMPLETED)
        return state

    def _phase_readiness_gate(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.READINESS_GATE, PhaseStatus.RUNNING)
        checks = self.playwright.readiness_checks(state.artifacts["testcases_enriched"])
        path = self.store.artifact_path(state.run_id, "readiness_gate.json")
        write_json(path, [asdict(item) for item in checks])
        state.artifacts["readiness_gate"] = str(path)
        failed = [item for item in checks if not item.ok]
        if failed:
            details = "\n".join(f"  - {item.name}: {item.message}" for item in failed)
            reason = (
                "录制环境未准备完成，以下检查项未通过（后续录制步骤依赖这些环境，请先解决）：\n"
                + details
                + "\n\n请安装/配置好以上依赖后，使用 resume 命令继续。"
            )
            self._block(state, ConductorPhase.READINESS_GATE, reason)
            raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)
        self._mark_phase(state, ConductorPhase.READINESS_GATE, PhaseStatus.COMPLETED)
        return state

    def _phase_proof_ingest(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        self._mark_phase(state, ConductorPhase.PROOF_INGEST, PhaseStatus.RUNNING)
        proof_dir = inputs.get("proof_dir") or state.artifacts.get("proof_dir")
        entries = [CaseManifestEntry(**item) for item in read_json(state.artifacts["case_manifest"], default=[])]
        candidate_entries = [
            entry
            for entry in entries
            if entry.status in {CaseStatus.NEW_CANDIDATE.value, CaseStatus.REGEN_REQUIRED.value} and entry.ui_automatable
        ]
        if not proof_dir:
            bundle = self.playwright.build_recording_bundle(
                self.store.run_dir(state.run_id),
                state.artifacts["testcases_enriched"],
                candidate_entries,
            )
            state.artifacts["recording_bundle"] = bundle["bundle_dir"]
            state.artifacts["recording_next_step"] = bundle["next_step"]
            self._block(state, ConductorPhase.PROOF_INGEST, "等待 playwright-test-generator 证明产物")
            raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)
        artifacts = self.playwright.load_proof_artifacts(proof_dir)
        if not artifacts:
            self._block(state, ConductorPhase.PROOF_INGEST, "证明产物目录为空")
            raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)
        proof_path = self.store.artifact_path(state.run_id, "proof_artifacts.json")
        write_json(proof_path, {key: asdict(value) for key, value in artifacts.items()})
        state.artifacts["proof_artifacts"] = str(proof_path)
        self._mark_phase(state, ConductorPhase.PROOF_INGEST, PhaseStatus.COMPLETED)
        return state

    def _phase_codegen(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.CODEGEN, PhaseStatus.RUNNING)
        entries = [CaseManifestEntry(**item) for item in read_json(state.artifacts["case_manifest"], default=[])]
        proof_payload = read_json(state.artifacts["proof_artifacts"], default={})
        from qa_agent.models import ProofArtifact

        proof_artifacts = {key: ProofArtifact(**value) for key, value in proof_payload.items()}
        env_config = self.playwright.env_config_from_markdown(state.artifacts["testcases_enriched"])
        paths = self.playwright.generate_python_drafts(
            run_dir=self.store.run_dir(state.run_id),
            env_config=env_config,
            module=self._default_module(state),
            feature_key=self._default_feature(state),
            entries=entries,
            proof_artifacts=proof_artifacts,
        )
        drafts_path = self.store.artifact_path(state.run_id, "generated_drafts.json")
        write_json(drafts_path, paths)
        state.artifacts["generated_drafts"] = str(drafts_path)
        self._mark_phase(state, ConductorPhase.CODEGEN, PhaseStatus.COMPLETED)
        return state

    def _phase_normalize(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.NORMALIZE, PhaseStatus.RUNNING)
        draft_paths = read_json(state.artifacts["generated_drafts"], default=[])
        entries = [CaseManifestEntry(**item) for item in read_json(state.artifacts["case_manifest"], default=[])]
        env_config = self.playwright.env_config_from_markdown(state.artifacts["testcases_enriched"])
        normalized = self.normalizer.normalize(
            draft_paths=draft_paths,
            entries=entries,
            output_dir=self.store.artifact_path(state.run_id, "normalized_scripts").parent / "normalized_scripts",
            env_config=env_config,
        )
        path = self.store.artifact_path(state.run_id, "normalized_scripts.json")
        write_json(path, normalized)
        state.artifacts["normalized_scripts"] = str(path)
        self._mark_phase(state, ConductorPhase.NORMALIZE, PhaseStatus.COMPLETED)
        return state

    def _phase_promotion_guard(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.PROMOTION_GUARD, PhaseStatus.RUNNING)
        normalized = read_json(state.artifacts["normalized_scripts"], default={})
        normalized_paths = list(normalized.values())
        results = self.guard.evaluate(normalized_paths, module=self._default_module(state))
        path = self.store.artifact_path(state.run_id, "promotion_guard.json")
        write_json(path, {script: [asdict(item) for item in checks] for script, checks in results.items()})
        state.artifacts["promotion_guard"] = str(path)
        if not all(item["ok"] for checks in read_json(path).values() for item in checks):
            self._block(state, ConductorPhase.PROMOTION_GUARD, "promotion guard 未通过")
            raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)
        self._mark_phase(state, ConductorPhase.PROMOTION_GUARD, PhaseStatus.COMPLETED)
        return state

    def _phase_promote(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.PROMOTE, PhaseStatus.RUNNING)
        normalized = read_json(state.artifacts["normalized_scripts"], default={})
        normalized_paths = list(normalized.values())
        promoted = self.guard.promote(normalized_paths, module=self._default_module(state))
        promoted_path = self.store.artifact_path(state.run_id, "promoted_scripts.json")
        write_json(promoted_path, promoted)
        state.artifacts["promoted_scripts"] = str(promoted_path)
        entries = [CaseManifestEntry(**item) for item in read_json(state.artifacts["case_manifest"], default=[])]
        for entry in entries:
            if entry.status in {CaseStatus.NEW_CANDIDATE.value, CaseStatus.REGEN_REQUIRED.value}:
                entry.status = CaseStatus.PROMOTED.value
        write_json(state.artifacts["case_manifest"], [asdict(entry) for entry in entries])
        self._mark_phase(state, ConductorPhase.PROMOTE, PhaseStatus.COMPLETED)
        return state

    def _phase_regression_plan(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        self._mark_phase(state, ConductorPhase.REGRESSION_PLAN, PhaseStatus.RUNNING)
        module = inputs.get("module") or self._default_module(state)
        feature = inputs.get("feature") or self._default_feature(state)
        selectors = []
        if feature:
            selectors.extend(["--module", module, "--feature", slugify(feature)])
        else:
            selectors.extend(["--module", module])
        promoted = read_json(state.artifacts.get("promoted_scripts", ""), default=[])
        if promoted:
            first = Path(promoted[0]).relative_to(self.ok_ui.project_root).as_posix()
            selectors.extend(["--path", first])
        plan = {"module": module, "feature": feature, "selectors": selectors}
        path = self.store.artifact_path(state.run_id, "regression_plan.json")
        write_json(path, plan)
        state.artifacts["regression_plan"] = str(path)
        self._mark_phase(state, ConductorPhase.REGRESSION_PLAN, PhaseStatus.COMPLETED)
        return state

    def _phase_regression_dry_run(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.REGRESSION_DRY_RUN, PhaseStatus.RUNNING)
        plan = read_json(state.artifacts["regression_plan"])
        relative_path = ""
        selectors = plan["selectors"]
        if "--path" in selectors:
            relative_path = selectors[selectors.index("--path") + 1]
        result = self.ok_ui.dry_run(plan["module"], relative_path) if relative_path else self.ok_ui.dry_run(plan["module"], f"test_cases/{plan['module']}")
        path = self.store.artifact_path(state.run_id, "regression_dry_run.txt")
        write_text(path, (result.stdout or "") + "\n" + (result.stderr or ""))
        state.artifacts["regression_dry_run"] = str(path)
        if result.returncode != 0:
            self._block(state, ConductorPhase.REGRESSION_DRY_RUN, "回归预演执行失败")
            raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)
        self._mark_phase(state, ConductorPhase.REGRESSION_DRY_RUN, PhaseStatus.COMPLETED)
        return state

    def _phase_regression_run(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.REGRESSION_RUN, PhaseStatus.RUNNING)
        plan = read_json(state.artifacts["regression_plan"])
        result = self.ok_ui.real_run(plan["selectors"])
        path = self.store.artifact_path(state.run_id, "regression_run.txt")
        write_text(path, (result.stdout or "") + "\n" + (result.stderr or ""))
        state.artifacts["regression_run"] = str(path)
        if result.returncode != 0:
            self._block(state, ConductorPhase.REGRESSION_RUN, "回归执行失败")
            raise PhaseBlockedError(state.blocked_reason, run_id=state.run_id)
        self._mark_phase(state, ConductorPhase.REGRESSION_RUN, PhaseStatus.COMPLETED)
        return state

    def _phase_gate_reports(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        gate = GateReport(
            visual_scores=read_json(inputs.get("visual_report") or state.artifacts.get("visual_report", ""), default=[]) or [],
            ui_pass_rate=self._load_rate(inputs.get("ui_report") or state.artifacts.get("ui_report", "")),
            api_pass_rate=self._load_rate(inputs.get("api_report") or state.artifacts.get("api_report", "")),
        )
        visual_threshold = float(self.config.thresholds["gates"]["visual_score_min"])
        if gate.visual_scores and any(float(item.get("score", 0)) < visual_threshold for item in gate.visual_scores):
            gate.failed_checks.append("视觉门禁")
        if gate.ui_pass_rate is not None and gate.ui_pass_rate < float(self.config.thresholds["gates"]["ui_pass_rate_min"]):
            gate.failed_checks.append("UI门禁")
        if gate.api_pass_rate is not None and gate.api_pass_rate < float(self.config.thresholds["gates"]["api_pass_rate_min"]):
            gate.failed_checks.append("API门禁")
        gate.release_recommendation = "建议上线" if not gate.failed_checks else "暂缓上线"
        path = self.store.artifact_path(state.run_id, "gate_report.json")
        write_json(path, asdict(gate))
        state.artifacts["gate_report"] = str(path)
        return state

    def _phase_final_report(self, state: RunState) -> RunState:
        self._mark_phase(state, ConductorPhase.FINAL_REPORT, PhaseStatus.RUNNING)
        gate_report = read_json(state.artifacts.get("gate_report", ""), default={}) or {}
        report_lines = [
            f"# QA Agent 最终报告 - {state.run_id}",
            "",
            f"- 变更模式: {state.change_mode}",
            f"- 当前阶段: {state.current_phase}",
            f"- 阻塞原因: {state.blocked_reason or '无'}",
            "",
            "## 产物清单",
        ]
        for key, value in sorted(state.artifacts.items()):
            report_lines.append(f"- {artifact_label(key)}: {value}")
        report_lines.extend(
            [
                "",
                "## 门禁结论",
                f"- 上线建议: {gate_report.get('release_recommendation', '待定')}",
                f"- 未通过项: {', '.join(gate_report.get('failed_checks', [])) or '无'}",
            ]
        )
        path = self.store.artifact_path(state.run_id, "final_report.md")
        write_text(path, "\n".join(report_lines) + "\n")
        state.artifacts["final_report"] = str(path)
        self._mark_phase(state, ConductorPhase.FINAL_REPORT, PhaseStatus.COMPLETED)
        return state

    def _mark_phase(self, state: RunState, phase: ConductorPhase, status: PhaseStatus) -> None:
        state.current_phase = phase.value
        state.phase_statuses[phase.value] = status.value
        state.status = RunStatus.RUNNING.value if status == PhaseStatus.RUNNING else state.status
        self.store.save(state)

    def _block(self, state: RunState, phase: ConductorPhase, reason: str) -> None:
        state.current_phase = phase.value
        state.phase_statuses[phase.value] = PhaseStatus.BLOCKED.value
        state.status = RunStatus.BLOCKED.value
        state.blocked_reason = reason
        self.store.save(state)

    def _default_module(self, state: RunState) -> str:
        packet = read_json(state.artifacts.get("requirement_packet", ""), default={}) or {}
        modules = packet.get("candidate_modules") or []
        return modules[0] if modules else "ai"

    def _default_site(self, state: RunState) -> str:
        packet = read_json(state.artifacts.get("requirement_packet", ""), default={}) or {}
        return packet.get("site") or "us"

    def _default_feature(self, state: RunState) -> str:
        packet = read_json(state.artifacts.get("requirement_packet", ""), default={}) or {}
        return packet.get("feature_name") or "自动生成功能"

    def _load_git_diff(self, inputs: dict[str, Any]) -> str:
        if inputs.get("git_diff_summary"):
            return str(inputs["git_diff_summary"])
        if inputs.get("git_diff_file"):
            return read_if_exists(inputs["git_diff_file"])
        return ""

    def _load_rate(self, report_path: str | None) -> float | None:
        if not report_path:
            return None
        payload = read_json(report_path, default=None)
        if payload is None:
            return None
        if isinstance(payload, dict):
            for key in ("pass_rate", "ui_pass_rate", "api_pass_rate"):
                if key in payload:
                    return float(payload[key])
        if isinstance(payload, (int, float)):
            return float(payload)
        return None

    def _write_module_map_candidate(self, run_id: str, entries: list[CaseManifestEntry]) -> Path:
        candidate_path = self.store.artifact_path(run_id, "module_map_candidate.md")
        lines = [
            "# module-map 候选映射",
            "",
            "| 开发常说的功能 | 推荐 selector | 说明 |",
            "| --- | --- | --- |",
        ]
        seen: set[str] = set()
        for entry in entries:
            key = f"{entry.module}-{entry.feature_key}"
            if key in seen:
                continue
            seen.add(key)
            selector = f"`--module {entry.module} --path {entry.target_script_path}`"
            lines.append(f"| `{entry.feature_key}` | {selector} | 来自 QA Agent 生成候选映射 |")
        write_text(candidate_path, "\n".join(lines) + "\n")
        return candidate_path
