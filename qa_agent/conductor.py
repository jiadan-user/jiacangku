"""
QA Agent 编排层 - 纯状态机。

只管阶段流转，不执行 skill 的内部推理流程；编排层自带的阶段只做候选识别、
影响回归验证、任务编排和产物落盘。
"""
from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from qa_agent.adapters.impact_verification import ImpactVerificationExecutor
from qa_agent.adapters.legacy_update import LegacyUpdateExecutor, make_task_id
from qa_agent.config import AppConfig
from qa_agent.io import read_json, read_text, write_json, write_text
from qa_agent.models import (
    AttributionCategory,
    ChangeMode,
    ImpactCandidate,
    ImpactRunStatus,
    ImpactVerificationRecord,
    LegacyUpdateGate,
    LegacyUpdateTask,
    LegacyUpdateTaskStatus,
    OverlapDecision,
    Phase,
    PhaseStatus,
    RequirementPacket,
    RunState,
    RunStatus,
    to_data,
)
from qa_agent.state import RunStore
from qa_agent.utils import normalize_text

SKILL_PATHS = {
    Phase.SENIOR_QA_BRAIN: "bundled/skills/senior-qa-brain/SKILL.md",
    Phase.PLAYWRIGHT_GENERATOR: "bundled/skills/playwright-test-generator/SKILL.md",
    Phase.OK_UI_REGRESSION: "bundled/skills/ok_autotest_ui_skill/SKILL.md",
    Phase.KNOWLEDGE_BASE_UPDATE: "bundled/skills/knowledge-base-manager/SKILL.md",
}

NEW_FEATURE_PHASES = [
    Phase.INTAKE,
    Phase.IMPACT_SPLIT,
    Phase.SENIOR_QA_BRAIN,
    Phase.PLAYWRIGHT_GENERATOR,
    Phase.IMPACT_ANALYSIS,
    Phase.IMPACT_VERIFICATION,
    Phase.LEGACY_UPDATE,
    Phase.OK_UI_REGRESSION,
    Phase.FINAL_REPORT,
    Phase.KNOWLEDGE_BASE_UPDATE,
]

REGRESSION_PHASES = [
    Phase.INTAKE,
    Phase.IMPACT_SPLIT,
    Phase.IMPACT_ANALYSIS,
    Phase.IMPACT_VERIFICATION,
    Phase.LEGACY_UPDATE,
    Phase.OK_UI_REGRESSION,
    Phase.FINAL_REPORT,
    Phase.KNOWLEDGE_BASE_UPDATE,
]

MIXED_PHASES = NEW_FEATURE_PHASES


class QAConductor:
    def __init__(
        self,
        config: AppConfig,
        legacy_update_executor: LegacyUpdateExecutor | None = None,
        impact_verification_executor: ImpactVerificationExecutor | None = None,
    ) -> None:
        self.config = config
        self.store = RunStore(config.qa_state_root)
        self.legacy_update_executor = legacy_update_executor or LegacyUpdateExecutor(config)
        self.impact_verification_executor = impact_verification_executor or ImpactVerificationExecutor(config)

    def plan(self, inputs: dict[str, Any]) -> RunState:
        mode = self._coerce_mode(inputs.get("change_mode"))
        state = self.store.create_run(mode)
        state = self._phase_intake(state, inputs)
        state = self._phase_impact_split(state, mode)
        state.status = RunStatus.PLANNED.value
        self.store.save(state)
        return state

    def status(self, run_id: str) -> dict[str, Any]:
        state = self.store.load(run_id)
        return to_data(state)

    def advance(self, run_id: str, inputs: dict[str, Any] | None = None) -> RunState:
        inputs = inputs or {}
        state = self.store.load(run_id)
        phases = self._phases_for_mode(state.change_mode)

        for phase in phases:
            phase_state = state.phase_statuses.get(phase.value, PhaseStatus.PENDING.value)
            if phase_state in (PhaseStatus.COMPLETED.value, PhaseStatus.SKIPPED.value):
                continue
            state = self._execute_phase(state, phase, inputs)
            phase_state = state.phase_statuses.get(phase.value, PhaseStatus.PENDING.value)
            if phase_state == PhaseStatus.COMPLETED.value:
                continue
            self.store.save(state)
            return state

        if all(
            state.phase_statuses.get(phase.value) in (PhaseStatus.COMPLETED.value, PhaseStatus.SKIPPED.value)
            for phase in phases
        ):
            state.status = RunStatus.COMPLETED.value
            state.blocked_reason = ""
        self.store.save(state)
        return state

    def complete_phase(self, run_id: str, phase_name: str, artifacts: dict[str, str] | None = None) -> RunState:
        state = self.store.load(run_id)
        if artifacts:
            state.artifacts.update(artifacts)
        if phase_name == Phase.IMPACT_VERIFICATION.value:
            state = self._confirm_impact_verification(state)
        state.phase_statuses[phase_name] = PhaseStatus.COMPLETED.value
        state.current_phase = phase_name
        state.blocked_reason = ""
        state.status = RunStatus.RUNNING.value
        self.store.save(state)
        return self.advance(run_id)

    def _execute_phase(self, state: RunState, phase: Phase, inputs: dict[str, Any]) -> RunState:
        if phase == Phase.INTAKE:
            return self._phase_intake(state, inputs)
        if phase == Phase.IMPACT_SPLIT:
            return self._phase_impact_split(state, state.change_mode)
        if phase in (
            Phase.SENIOR_QA_BRAIN,
            Phase.PLAYWRIGHT_GENERATOR,
            Phase.OK_UI_REGRESSION,
            Phase.KNOWLEDGE_BASE_UPDATE,
        ):
            return self._phase_skill(state, phase, inputs)
        if phase == Phase.IMPACT_ANALYSIS:
            return self._phase_impact_analysis(state)
        if phase == Phase.IMPACT_VERIFICATION:
            return self._phase_impact_verification(state)
        if phase == Phase.LEGACY_UPDATE:
            return self._phase_legacy_update(state)
        if phase == Phase.FINAL_REPORT:
            return self._phase_final_report(state)
        return state

    def _coerce_mode(self, value: str | None) -> str:
        aliases = {
            ChangeMode.NEW_FEATURE.value: ChangeMode.NEW_FEATURE.value,
            ChangeMode.REGRESSION.value: ChangeMode.REGRESSION.value,
            ChangeMode.MIXED.value: ChangeMode.MIXED.value,
            "a": ChangeMode.NEW_FEATURE.value,
            "b": ChangeMode.REGRESSION.value,
            "c": ChangeMode.MIXED.value,
            "新需求模式": ChangeMode.NEW_FEATURE.value,
            "纯回归模式": ChangeMode.REGRESSION.value,
            "混合模式": ChangeMode.MIXED.value,
        }
        normalized = (value or "").strip()
        if normalized in aliases:
            return aliases[normalized]
        raise ValueError(
            "必须显式选择变更模式：A 新需求模式（--change-mode 新需求）、"
            "B 纯回归模式（--change-mode 纯回归）、C 混合模式（--change-mode 混合）"
        )

    def _phases_for_mode(self, mode: str) -> list[Phase]:
        if mode == ChangeMode.REGRESSION.value:
            return REGRESSION_PHASES
        if mode == ChangeMode.MIXED.value:
            return MIXED_PHASES
        return NEW_FEATURE_PHASES

    def _phase_intake(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        if state.artifacts.get("requirement_packet"):
            self._mark(state, Phase.INTAKE, PhaseStatus.COMPLETED)
            return state
        self._mark(state, Phase.INTAKE, PhaseStatus.RUNNING)
        packet = RequirementPacket(
            change_mode=state.change_mode,
            figma_url=inputs.get("figma_url", ""),
            prd_refs=list(inputs.get("prd_refs", []) or []),
            candidate_modules=[m for m in [inputs.get("module")] if m],
            site=inputs.get("site", ""),
            feature_name=inputs.get("feature", ""),
            change_description=inputs.get("change_description", ""),
        )
        path = self.store.artifact_path(state.run_id, "requirement_packet.json")
        write_json(path, asdict(packet))
        state.artifacts["requirement_packet"] = str(path)
        state.change_mode = packet.change_mode
        self._mark(state, Phase.INTAKE, PhaseStatus.COMPLETED)
        return state

    def _phase_impact_split(self, state: RunState, mode: str) -> RunState:
        self._mark(state, Phase.IMPACT_SPLIT, PhaseStatus.RUNNING)
        state.change_mode = mode
        phases = self._phases_for_mode(mode)
        state.phase_statuses = {phase.value: PhaseStatus.PENDING.value for phase in phases}
        state.phase_statuses[Phase.INTAKE.value] = PhaseStatus.COMPLETED.value
        state.phase_statuses[Phase.IMPACT_SPLIT.value] = PhaseStatus.COMPLETED.value
        write_json(
            self.store.artifact_path(state.run_id, "impact_split.json"),
            {"change_mode": mode, "phases": [phase.value for phase in phases]},
        )
        self._mark(state, Phase.IMPACT_SPLIT, PhaseStatus.COMPLETED)
        return state

    def _phase_skill(self, state: RunState, phase: Phase, inputs: dict[str, Any]) -> RunState:
        del inputs
        self._mark(state, phase, PhaseStatus.RUNNING)
        skill_path = SKILL_PATHS[phase]
        absolute_skill_path = self.config.project_root / skill_path
        state.artifacts[f"{phase.value}_skill_path"] = str(absolute_skill_path)

        instruction_path = self.store.artifact_path(state.run_id, f"{phase.value}_instruction.md")
        write_text(instruction_path, self._build_instruction(state, phase))
        state.artifacts[f"{phase.value}_instruction"] = str(instruction_path)

        self._mark(state, phase, PhaseStatus.BLOCKED)
        if not absolute_skill_path.exists():
            state.blocked_reason = f"缺少 {skill_path}，请先同步内嵌资源后再继续"
        elif phase == Phase.KNOWLEDGE_BASE_UPDATE:
            state.blocked_reason = f"请按 {skill_path} 先生成 KB 预览、等待确认、再写入，完成后用 complete 继续"
        else:
            state.blocked_reason = f"请按 {skill_path} 执行，完成后用 complete 继续"
        state.status = RunStatus.BLOCKED.value
        return state

    def _phase_impact_analysis(self, state: RunState) -> RunState:
        self._mark(state, Phase.IMPACT_ANALYSIS, PhaseStatus.RUNNING)
        packet = self._requirement_packet(state)
        impact_payload = self._build_impact_payload(state, packet)
        overlap_decisions = self._build_overlap_decisions(
            impact_payload["new_cases"],
            impact_payload["existing_cases"],
        )

        impact_path = self.store.artifact_path(state.run_id, "impact_candidates.json")
        overlap_path = self.store.artifact_path(state.run_id, "overlap_report.md")
        write_json(impact_path, impact_payload)
        write_text(overlap_path, self._render_overlap_report(packet, overlap_decisions))

        state.artifacts["impact_candidates"] = str(impact_path)
        state.artifacts["overlap_report"] = str(overlap_path)
        state.blocked_reason = ""
        self._mark(state, Phase.IMPACT_ANALYSIS, PhaseStatus.COMPLETED)
        return state

    def _phase_impact_verification(self, state: RunState) -> RunState:
        if (
            state.phase_statuses.get(Phase.IMPACT_VERIFICATION.value) == PhaseStatus.BLOCKED.value
            and state.artifacts.get("change_attribution_report")
        ):
            state.current_phase = Phase.IMPACT_VERIFICATION.value
            state.status = RunStatus.BLOCKED.value
            state.blocked_reason = "请先确认变更归因报告，确认后再 complete 当前阶段"
            return state

        self._mark(state, Phase.IMPACT_VERIFICATION, PhaseStatus.RUNNING)
        packet = self._requirement_packet(state)
        packet["change_mode"] = state.change_mode
        impact_payload = read_json(state.artifacts.get("impact_candidates", ""), default={}) or {}
        outcome = self.impact_verification_executor.verify(
            run_dir=self.store.run_dir(state.run_id),
            packet=packet,
            impact_payload=impact_payload,
        )

        selector_path = self.store.artifact_path(state.run_id, "impact_run_selector_plan.json")
        run_results_path = self.store.artifact_path(state.run_id, "impact_run_results.json")
        attribution_result_path = self.store.artifact_path(state.run_id, "change_attribution_result.json")
        attribution_report_path = self.store.artifact_path(state.run_id, "change_attribution_report.md")

        write_json(selector_path, outcome.selector_plan)
        write_json(run_results_path, [asdict(record) for record in outcome.records])
        write_json(attribution_result_path, [asdict(record) for record in outcome.records])
        write_text(attribution_report_path, self._render_change_attribution_report(packet, outcome.records))

        state.artifacts.update(
            {
                "impact_run_selector_plan": str(selector_path),
                "impact_run_results": str(run_results_path),
                "change_attribution_result": str(attribution_result_path),
                "change_attribution_report": str(attribution_report_path),
            }
        )
        self._mark(state, Phase.IMPACT_VERIFICATION, PhaseStatus.BLOCKED)
        state.status = RunStatus.BLOCKED.value
        state.blocked_reason = "受影响用例已执行并生成归因报告，等待你确认后再继续"
        return state

    def _confirm_impact_verification(self, state: RunState) -> RunState:
        packet = self._requirement_packet(state)
        impact_payload = read_json(state.artifacts.get("impact_candidates", ""), default={}) or {}
        attribution_records = self._load_attribution_records(state)
        tasks = self._load_seed_tasks(state) or self._build_confirmed_legacy_tasks(packet, attribution_records)
        gate = self._build_gate(tasks, round_index=0)
        selector_plan = self._build_selector_plan(packet, impact_payload, tasks)

        tasks_path = self.store.artifact_path(state.run_id, "legacy_update_tasks.json")
        gate_path = self.store.artifact_path(state.run_id, "legacy_update_gate.json")
        selector_path = self.store.artifact_path(state.run_id, "regression_selector_plan.json")
        confirmation_path = self.store.artifact_path(state.run_id, "change_attribution_confirmation.json")

        write_json(tasks_path, [asdict(task) for task in tasks])
        write_json(gate_path, asdict(gate))
        write_json(selector_path, selector_plan)
        write_json(
            confirmation_path,
            {
                "confirmed": True,
                "tasks_generated": len(tasks),
                "latest_change_cases": [
                    record.related_nodeid or record.target
                    for record in attribution_records
                    if record.category == AttributionCategory.LATEST_CHANGE.value
                ],
            },
        )

        state.artifacts.update(
            {
                "legacy_update_tasks": str(tasks_path),
                "legacy_update_gate": str(gate_path),
                "regression_selector_plan": str(selector_path),
                "change_attribution_confirmation": str(confirmation_path),
            }
        )
        return state

    def _phase_legacy_update(self, state: RunState) -> RunState:
        self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.RUNNING)
        tasks = self._load_legacy_tasks(state)
        if not tasks:
            gate = self._build_gate([], round_index=0)
            gate_path = self.store.artifact_path(state.run_id, "legacy_update_gate.json")
            write_json(gate_path, asdict(gate))
            state.artifacts["legacy_update_gate"] = str(gate_path)
            state.blocked_reason = ""
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.COMPLETED)
            return state

        current_gate = read_json(state.artifacts.get("legacy_update_gate", ""), default={}) or {}
        round_index = int(current_gate.get("round_index", 0)) + 1
        outcome = self.legacy_update_executor.run_round(
            run_dir=self.store.run_dir(state.run_id),
            tasks=tasks,
            round_index=round_index,
        )

        tasks_path = self.store.artifact_path(state.run_id, "legacy_update_tasks.json")
        gate_path = self.store.artifact_path(state.run_id, "legacy_update_gate.json")
        results_path = self.store.artifact_path(state.run_id, f"legacy_update_results_round_{round_index:02d}.json")

        write_json(tasks_path, [asdict(task) for task in outcome.tasks])
        write_json(gate_path, asdict(outcome.gate))
        write_json(results_path, outcome.results)

        state.artifacts["legacy_update_tasks"] = str(tasks_path)
        state.artifacts["legacy_update_gate"] = str(gate_path)
        state.artifacts[f"legacy_update_results_round_{round_index:02d}"] = str(results_path)
        state.artifacts["regression_selector_plan"] = str(self._refresh_selector_plan(state, outcome.tasks))

        if outcome.gate.all_completed:
            state.blocked_reason = ""
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.COMPLETED)
            return state

        if outcome.gate.has_manual_review:
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.BLOCKED)
            state.status = RunStatus.BLOCKED.value
            state.blocked_reason = (
                f"旧脚本更新第{round_index}轮后仍有 manual-review 任务，"
                "需先处理当前阶段再继续"
            )
            return state

        state.status = RunStatus.RUNNING.value
        state.blocked_reason = (
            f"旧脚本更新第{round_index}轮完成，"
            f"仍有 {outcome.gate.retry_count + outcome.gate.pending_count} 个任务待处理，"
            "继续 advance 进入下一轮"
        )
        return state

    def _phase_final_report(self, state: RunState) -> RunState:
        self._mark(state, Phase.FINAL_REPORT, PhaseStatus.RUNNING)
        lines = [
            f"# QA Agent 最终报告 - {state.run_id}",
            "",
            f"- 变更模式: {state.change_mode}",
            f"- 当前阶段: {state.current_phase}",
            "",
            "## 核心产物",
        ]
        for key in [
            "impact_candidates",
            "change_attribution_report",
            "legacy_update_gate",
            "regression_selector_plan",
        ]:
            if state.artifacts.get(key):
                lines.append(f"- {key}: {state.artifacts[key]}")
        lines.extend(["", "## 完整产物清单"])
        for key, value in sorted(state.artifacts.items()):
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## 阶段状态"])
        for phase_name, status in state.phase_statuses.items():
            lines.append(f"- {phase_name}: {status}")

        path = self.store.artifact_path(state.run_id, "final_report.md")
        write_text(path, "\n".join(lines) + "\n")
        state.artifacts["final_report"] = str(path)
        self._mark(state, Phase.FINAL_REPORT, PhaseStatus.COMPLETED)
        state.status = RunStatus.RUNNING.value
        state.blocked_reason = ""
        return state

    def _build_instruction(self, state: RunState, phase: Phase) -> str:
        skill_path = SKILL_PATHS[phase]
        packet = self._requirement_packet(state)

        if phase == Phase.SENIOR_QA_BRAIN:
            parts = [
                f"# 阶段: {phase.value}",
                "",
                f"请读取 `{skill_path}` 并按其定义的完整工作流程执行。",
                "",
                "## 输入",
            ]
            if packet.get("figma_url"):
                parts.append(f"- Figma: {packet['figma_url']}")
            for ref in packet.get("prd_refs", []):
                parts.append(f"- 需求文档: {ref}")
            parts.extend(
                [
                    "",
                    "## 要求",
                    "- 按 SKILL.md 流程逐步执行，不要跳步",
                    "- 生成分析报告后等待用户确认",
                    "- 确认后生成 Markdown 测试用例",
                ]
            )
            return "\n".join(parts)

        if phase == Phase.PLAYWRIGHT_GENERATOR:
            return "\n".join(
                [
                    f"# 阶段: {phase.value}",
                    "",
                    f"请读取 `{skill_path}` 并按其定义的 5 阶段流程执行。",
                    "",
                    "## 输入",
                    "- 测试用例文档: 阶段1(senior-qa-brain)生成的 Markdown 用例",
                    "",
                    "## 要求",
                    "- 按 SKILL.md 的 5 个阶段严格顺序执行",
                    "- 每个阶段开始前先读取 SKILL.md 指定的 references 文件",
                    "- 每批最多 5 条用例",
                    "- 生成的脚本暂不直接入库，先交由影响回归阶段验证",
                ]
            )

        if phase == Phase.OK_UI_REGRESSION:
            module = (packet.get("candidate_modules") or [""])[0]
            site = packet.get("site", "")
            desc = packet.get("change_description", "")
            selector_plan = state.artifacts.get("regression_selector_plan", "")
            parts = [
                f"# 阶段: {phase.value}",
                "",
                f"请读取 `{skill_path}` 并按其主流程执行。",
                "",
                "## 输入",
                f"- 模块: {module}",
                f"- 站点: {site}",
            ]
            if desc:
                parts.append(f"- 改动描述: {desc}")
            if selector_plan:
                parts.append(f"- selector 计划: {selector_plan}")
            parts.extend(
                [
                    "",
                    "## 要求",
                    "- 优先消费 regression_selector_plan.json",
                    "- 先 dry-run 预览，等用户确认后再真实执行",
                    "- 若 selector_plan 缺少必要信息，再退回 module-map.md 做补充",
                ]
            )
            return "\n".join(parts)

        if phase == Phase.KNOWLEDGE_BASE_UPDATE:
            return "\n".join(
                [
                    f"# 阶段: {phase.value}",
                    "",
                    f"请读取 `{skill_path}` 并按其“预览 -> 确认 -> 写入”流程执行。",
                    "",
                    "## 输入",
                    f"- 最终报告: {state.artifacts.get('final_report', '')}",
                    f"- 影响分析: {state.artifacts.get('impact_candidates', '')}",
                    f"- 归因报告: {state.artifacts.get('change_attribution_report', '')}",
                    f"- 回归 selector 计划: {state.artifacts.get('regression_selector_plan', '')}",
                    "",
                    "## 要求",
                    "- 先输出 knowledge base 更新预览，再等待确认",
                    "- 写入完成后回传 preview/result 产物路径",
                    "- 若 vendored skill 缺失或预览失败，不要跳过本阶段",
                ]
            )

        return f"# 阶段: {phase.value}\n\n请读取 `{skill_path}` 并执行。"

    def _mark(self, state: RunState, phase: Phase, status: PhaseStatus) -> None:
        state.current_phase = phase.value
        state.phase_statuses[phase.value] = status.value
        if status == PhaseStatus.RUNNING:
            state.status = RunStatus.RUNNING.value
        state.touch()

    def _requirement_packet(self, state: RunState) -> dict[str, Any]:
        return read_json(state.artifacts.get("requirement_packet", ""), default={}) or {}

    def _build_impact_payload(self, state: RunState, packet: dict[str, Any]) -> dict[str, Any]:
        module = (packet.get("candidate_modules") or [""])[0]
        site = packet.get("site", "")
        feature = packet.get("feature_name", "")
        new_cases = self._discover_new_cases(state, module, site, feature)
        existing_cases = self._discover_existing_cases(packet)
        merged_paths = sorted(
            {
                candidate.target
                for candidate in new_cases + existing_cases
                if candidate.target.endswith(".py")
            }
        )
        return {
            "module": module,
            "site": site,
            "feature_name": feature,
            "change_mode": state.change_mode,
            "new_cases": [asdict(item) for item in new_cases],
            "existing_cases": [asdict(item) for item in existing_cases],
            "merged_regression_candidates": merged_paths,
        }

    def _discover_new_cases(self, state: RunState, module: str, site: str, feature: str) -> list[ImpactCandidate]:
        candidates: list[ImpactCandidate] = []
        seen: set[str] = set()
        for key, value in state.artifacts.items():
            if not any(token in key for token in ("generated", "promoted", "script", "manifest")):
                continue
            for script_path in self._extract_script_paths(value):
                if script_path in seen:
                    continue
                seen.add(script_path)
                candidates.append(
                    ImpactCandidate(
                        source_type="new-script",
                        target=script_path,
                        module=module,
                        site=site,
                        feature_key=feature,
                        reason=f"来源于产物 {key}",
                    )
                )
        return candidates

    def _extract_script_paths(self, artifact_value: str) -> list[str]:
        target = Path(artifact_value)
        if target.suffix == ".py" and target.exists():
            return [str(target)]
        if target.suffix == ".json" and target.exists():
            payload = read_json(target, default=[]) or []
            if isinstance(payload, list):
                return [str(item) for item in payload if str(item).endswith(".py")]
        return []

    def _discover_existing_cases(self, packet: dict[str, Any]) -> list[ImpactCandidate]:
        module = (packet.get("candidate_modules") or [""])[0]
        feature = packet.get("feature_name", "")
        change_desc = packet.get("change_description", "")
        regression_root = Path(self.config.skills.get("paths", {}).get("regression_project_root", "")) / "test_cases"
        if not module or not regression_root.exists():
            return []

        keywords = self._impact_keywords(module, feature, change_desc)
        matches: list[ImpactCandidate] = []
        for script_path in sorted(regression_root.rglob("test_*.py")):
            normalized_path = normalize_text(script_path.as_posix())
            if module and module not in normalized_path:
                continue
            text = read_text(script_path)
            searchable = normalize_text(f"{script_path.as_posix()} {text}")
            if keywords and not any(keyword in searchable for keyword in keywords):
                continue
            case_refs = self._extract_case_refs(script_path, text)
            if case_refs:
                for case_ref in case_refs:
                    matches.append(
                        ImpactCandidate(
                            source_type="existing-script",
                            target=str(script_path),
                            module=module,
                            site=packet.get("site", ""),
                            feature_key=feature,
                            reason="模块与关键字命中现有自动化脚本",
                            related_case_id=case_ref["case_id"],
                            related_nodeid=case_ref["nodeid"],
                            details={"test_name": case_ref["test_name"]},
                        )
                    )
            else:
                matches.append(
                    ImpactCandidate(
                        source_type="existing-script",
                        target=str(script_path),
                        module=module,
                        site=packet.get("site", ""),
                        feature_key=feature,
                        reason="模块与关键字命中现有自动化脚本",
                    )
                )
        return matches

    def _impact_keywords(self, module: str, feature: str, change_desc: str) -> list[str]:
        raw_tokens = [module, feature, change_desc]
        tokens: set[str] = set()
        for token_group in raw_tokens:
            for token in re.split(r"[^a-zA-Z0-9\u4e00-\u9fff]+", token_group or ""):
                normalized = normalize_text(token)
                if not normalized:
                    continue
                if len(normalized) >= 3 or re.search(r"[\u4e00-\u9fff]{2,}", normalized):
                    tokens.add(normalized)
        return sorted(tokens)

    def _extract_case_refs(self, script_path: Path, text: str) -> list[dict[str, str]]:
        case_ids = re.findall(r"@pytest\.mark\.(case_id_[a-zA-Z0-9_]+)", text)
        test_names = re.findall(r"def (test_[a-zA-Z0-9_]+)\(", text)
        refs: list[dict[str, str]] = []
        for index, test_name in enumerate(test_names):
            case_id = case_ids[index] if index < len(case_ids) else ""
            refs.append(
                {
                    "case_id": case_id,
                    "test_name": test_name,
                    "nodeid": f"{script_path.as_posix()}::{test_name}",
                }
            )
        return refs

    def _build_overlap_decisions(
        self,
        new_cases: list[dict[str, Any]],
        existing_cases: list[dict[str, Any]],
    ) -> list[OverlapDecision]:
        decisions: list[OverlapDecision] = []
        for new_case in new_cases:
            new_target = new_case.get("target", "")
            new_case_id = new_case.get("related_case_id", "")
            for existing_case in existing_cases:
                existing_target = existing_case.get("target", "")
                existing_case_id = existing_case.get("related_case_id", "")
                same_case = new_case_id and existing_case_id and new_case_id == existing_case_id
                same_path = new_target and existing_target and Path(new_target).name == Path(existing_target).name
                if not (same_case or same_path):
                    continue
                decisions.append(
                    OverlapDecision(
                        new_target=new_target,
                        existing_target=existing_target,
                        decision="overlap",
                        reason="新旧脚本命中同名脚本或相同 case_id，需先执行影响回归再裁决",
                        related_case_id=existing_case_id,
                        related_nodeid=existing_case.get("related_nodeid", ""),
                    )
                )
        return decisions

    def _load_seed_tasks(self, state: RunState) -> list[LegacyUpdateTask]:
        seed_path = state.artifacts.get("legacy_update_tasks_seed", "")
        payload = read_json(seed_path, default=[]) or []
        return self._task_objects(payload)

    def _load_legacy_tasks(self, state: RunState) -> list[LegacyUpdateTask]:
        payload = read_json(state.artifacts.get("legacy_update_tasks", ""), default=[]) or []
        return self._task_objects(payload)

    def _task_objects(self, payload: list[dict[str, Any]]) -> list[LegacyUpdateTask]:
        tasks: list[LegacyUpdateTask] = []
        for item in payload:
            if isinstance(item, LegacyUpdateTask):
                tasks.append(item)
                continue
            tasks.append(LegacyUpdateTask(**item))
        return tasks

    def _load_attribution_records(self, state: RunState) -> list[ImpactVerificationRecord]:
        payload = read_json(state.artifacts.get("change_attribution_result", ""), default=[]) or []
        records: list[ImpactVerificationRecord] = []
        for item in payload:
            if isinstance(item, ImpactVerificationRecord):
                records.append(item)
            else:
                records.append(ImpactVerificationRecord(**item))
        return records

    def _build_confirmed_legacy_tasks(
        self,
        packet: dict[str, Any],
        records: list[ImpactVerificationRecord],
    ) -> list[LegacyUpdateTask]:
        tasks: list[LegacyUpdateTask] = []
        max_rounds = int(self.config.thresholds.get("gates", {}).get("max_fix_rounds", 3))
        module = (packet.get("candidate_modules") or [""])[0]
        site = packet.get("site", "")
        for record in records:
            if record.source_type == "new-script" and record.run_status == ImpactRunStatus.PASSED.value:
                promotion_task = self._build_new_script_promotion_task(packet, record, max_rounds)
                if promotion_task:
                    tasks.append(promotion_task)
                continue

            if record.source_type == "new-script" and record.category == AttributionCategory.LATEST_CHANGE.value:
                tasks.append(
                    LegacyUpdateTask(
                        task_id=make_task_id("legacy"),
                        target_script=record.target,
                        target_case_id=record.related_case_id,
                        target_nodeid=record.related_nodeid,
                        impact_type="new-script-failed",
                        recommended_action="manual-review",
                        reason="新脚本影响回归失败，需人工确认后决定重录或修正",
                        max_attempts=max_rounds,
                        details={"module": module, "site": site, "source_type": record.source_type},
                    )
                )
                continue

            if record.category != AttributionCategory.LATEST_CHANGE.value:
                continue

            tasks.append(
                LegacyUpdateTask(
                    task_id=make_task_id("legacy"),
                    target_script=record.target,
                    target_case_id=record.related_case_id,
                    target_nodeid=record.related_nodeid,
                    impact_type="change-attribution",
                    recommended_action=self._recommended_action(record),
                    reason=record.reason or "影响回归判定为本次变更引起",
                    max_attempts=max_rounds,
                    details={
                        "module": module,
                        "site": site,
                        "source_type": record.source_type,
                    },
                )
            )
        return tasks

    def _build_new_script_promotion_task(
        self,
        packet: dict[str, Any],
        record: ImpactVerificationRecord,
        max_rounds: int,
    ) -> LegacyUpdateTask | None:
        source_path = Path(record.staged_target or record.target)
        if not source_path.exists():
            return None
        regression_root = Path(self.config.skills.get("paths", {}).get("regression_project_root", ""))
        try:
            source_path.resolve().relative_to(regression_root.resolve())
            return None
        except ValueError:
            pass
        target_path = self._infer_promotion_target(packet, source_path)
        return LegacyUpdateTask(
            task_id=make_task_id("legacy"),
            target_script=str(target_path),
            target_case_id=record.related_case_id,
            target_nodeid=record.related_nodeid,
            impact_type="new-script-promotion",
            recommended_action="promote-new-script",
            reason="新脚本影响回归已通过，等待人工确认后 promotion 到正式回归目录",
            max_attempts=max_rounds,
            details={
                "module": (packet.get("candidate_modules") or [""])[0],
                "site": packet.get("site", ""),
                "replacement_source_path": str(source_path),
                "source_type": record.source_type,
            },
        )

    def _infer_promotion_target(self, packet: dict[str, Any], source_path: Path) -> Path:
        regression_root = Path(self.config.skills.get("paths", {}).get("regression_project_root", ""))
        module = (packet.get("candidate_modules") or ["misc"])[0] or "misc"
        parts = source_path.parts
        if "test_cases" in parts:
            suffix = Path(*parts[parts.index("test_cases") + 1 :])
            return regression_root / "test_cases" / suffix
        return regression_root / "test_cases" / module / source_path.name

    def _recommended_action(self, record: ImpactVerificationRecord) -> str:
        searchable = normalize_text(" ".join([record.summary, record.stdout_excerpt, record.stderr_excerpt]))
        if any(token in searchable for token in ["selector", "locator", "not found", "strict mode violation"]):
            return "update-selector"
        if any(token in searchable for token in ["assert", "expected", "actual", "mismatch"]):
            return "update-assertion"
        if "split" in searchable:
            return "split-case"
        return "re-record"

    def _build_gate(self, tasks: list[LegacyUpdateTask], round_index: int) -> LegacyUpdateGate:
        pending_count = sum(task.status == LegacyUpdateTaskStatus.PENDING.value for task in tasks)
        retry_count = sum(task.status == LegacyUpdateTaskStatus.RETRY.value for task in tasks)
        completed_count = sum(task.status == LegacyUpdateTaskStatus.COMPLETED.value for task in tasks)
        manual_review_count = sum(task.status == LegacyUpdateTaskStatus.MANUAL_REVIEW.value for task in tasks)
        total_count = len(tasks)
        return LegacyUpdateGate(
            round_index=round_index,
            total_count=total_count,
            pending_count=pending_count,
            retry_count=retry_count,
            completed_count=completed_count,
            manual_review_count=manual_review_count,
            all_completed=total_count == completed_count,
            has_manual_review=manual_review_count > 0,
        )

    def _render_overlap_report(self, packet: dict[str, Any], overlap_decisions: list[OverlapDecision]) -> str:
        module = (packet.get("candidate_modules") or [""])[0]
        lines = [
            "# 重叠裁决报告",
            "",
            f"- 模块: {module}",
            f"- 站点: {packet.get('site', '')}",
            "",
        ]
        if not overlap_decisions:
            lines.append("本轮未检测到明确重叠项，后续以影响回归结果为准。")
            return "\n".join(lines) + "\n"

        lines.extend(["| 新脚本 | 旧脚本 | 裁决 | 说明 |", "| --- | --- | --- | --- |"])
        for decision in overlap_decisions:
            lines.append(
                f"| `{decision.new_target}` | `{decision.existing_target}` | "
                f"`{decision.decision}` | {decision.reason} |"
            )
        return "\n".join(lines) + "\n"

    def _render_change_attribution_report(
        self,
        packet: dict[str, Any],
        records: list[ImpactVerificationRecord],
    ) -> str:
        counts = {
            AttributionCategory.PASSED.value: 0,
            AttributionCategory.LATEST_CHANGE.value: 0,
            AttributionCategory.PREEXISTING.value: 0,
            AttributionCategory.ENVIRONMENT.value: 0,
            AttributionCategory.UNCERTAIN.value: 0,
        }
        for record in records:
            counts[record.category] = counts.get(record.category, 0) + 1

        lines = [
            "# 变更归因报告",
            "",
            f"- 模块: {(packet.get('candidate_modules') or [''])[0]}",
            f"- 站点: {packet.get('site', '')}",
            f"- 功能: {packet.get('feature_name', '')}",
            "",
            "## 汇总",
            f"- passed: {counts[AttributionCategory.PASSED.value]}",
            f"- likely_caused_by_latest_change: {counts[AttributionCategory.LATEST_CHANGE.value]}",
            f"- likely_preexisting_or_unrelated: {counts[AttributionCategory.PREEXISTING.value]}",
            f"- environment_or_data_issue: {counts[AttributionCategory.ENVIRONMENT.value]}",
            f"- uncertain: {counts[AttributionCategory.UNCERTAIN.value]}",
            "",
            "## 明细",
        ]

        if not records:
            lines.append("- 本轮没有识别到可执行的受影响用例，等待人工确认后决定是否直接进入回归。")
            return "\n".join(lines) + "\n"

        for record in records:
            case_ref = record.related_nodeid or record.related_case_id or record.target
            lines.extend(
                [
                    f"### {case_ref}",
                    f"- 失败现象: {record.summary}",
                    f"- 判断类别: `{record.category}`",
                    f"- 判断理由: {record.reason}",
                    f"- 下一步建议: {record.next_action}",
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"

    def _build_selector_plan(
        self,
        packet: dict[str, Any],
        impact_payload: dict[str, Any],
        tasks: list[LegacyUpdateTask],
    ) -> dict[str, Any]:
        candidate_paths = set(impact_payload.get("merged_regression_candidates", []))
        for task in tasks:
            if task.status != LegacyUpdateTaskStatus.MANUAL_REVIEW.value:
                candidate_paths.add(task.target_script)
        return {
            "module": (packet.get("candidate_modules") or [""])[0],
            "site": packet.get("site", ""),
            "feature_name": packet.get("feature_name", ""),
            "candidate_paths": sorted(path for path in candidate_paths if path),
            "case_ids": sorted({task.target_case_id for task in tasks if task.target_case_id}),
            "nodeids": sorted({task.target_nodeid for task in tasks if task.target_nodeid}),
            "selectors": [{"kind": "path", "value": path} for path in sorted(path for path in candidate_paths if path)],
        }

    def _refresh_selector_plan(self, state: RunState, tasks: list[LegacyUpdateTask]) -> Path:
        packet = self._requirement_packet(state)
        impact_payload = read_json(state.artifacts.get("impact_candidates", ""), default={}) or {}
        selector_plan = self._build_selector_plan(packet, impact_payload, tasks)
        selector_path = self.store.artifact_path(state.run_id, "regression_selector_plan.json")
        write_json(selector_path, selector_plan)
        return selector_path
