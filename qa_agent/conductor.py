"""
QA Agent 编排层 - 纯状态机。

只管阶段流转，不执行任何 skill 的内部逻辑。
每个阶段：标记当前该用哪个 skill / 执行编排适配器 → 提示用户 → 等待产物 → 下一步。
"""
from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from qa_agent.adapters.legacy_update import LegacyUpdateExecutor, make_task_id
from qa_agent.config import AppConfig
from qa_agent.io import read_json, read_text, write_json, write_text
from qa_agent.models import (
    ChangeMode,
    ImpactCandidate,
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
}

NEW_FEATURE_PHASES = [
    Phase.INTAKE,
    Phase.IMPACT_SPLIT,
    Phase.SENIOR_QA_BRAIN,
    Phase.PLAYWRIGHT_GENERATOR,
    Phase.IMPACT_ANALYSIS,
    Phase.LEGACY_UPDATE,
    Phase.OK_UI_REGRESSION,
    Phase.FINAL_REPORT,
]

REGRESSION_PHASES = [
    Phase.INTAKE,
    Phase.IMPACT_SPLIT,
    Phase.IMPACT_ANALYSIS,
    Phase.LEGACY_UPDATE,
    Phase.OK_UI_REGRESSION,
    Phase.FINAL_REPORT,
]

MIXED_PHASES = NEW_FEATURE_PHASES


class QAConductor:
    def __init__(self, config: AppConfig, legacy_update_executor: LegacyUpdateExecutor | None = None) -> None:
        self.config = config
        self.store = RunStore(config.qa_state_root)
        self.legacy_update_executor = legacy_update_executor or LegacyUpdateExecutor(config)

    def plan(self, inputs: dict[str, Any]) -> RunState:
        mode = self._resolve_mode(inputs)
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
        """推进到下一个待执行阶段；自动穿过已完成的编排阶段。"""
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

        self.store.save(state)
        return state

    def _execute_phase(self, state: RunState, phase: Phase, inputs: dict[str, Any]) -> RunState:
        if phase == Phase.INTAKE:
            return self._phase_intake(state, inputs)
        if phase == Phase.IMPACT_SPLIT:
            return self._phase_impact_split(state, self._resolve_mode(inputs))
        if phase in (Phase.SENIOR_QA_BRAIN, Phase.PLAYWRIGHT_GENERATOR, Phase.OK_UI_REGRESSION):
            return self._phase_skill(state, phase, inputs)
        if phase == Phase.IMPACT_ANALYSIS:
            return self._phase_impact_analysis(state)
        if phase == Phase.LEGACY_UPDATE:
            return self._phase_legacy_update(state)
        if phase == Phase.FINAL_REPORT:
            return self._phase_final_report(state)
        return state

    def _resolve_mode(self, inputs: dict[str, Any]) -> str:
        explicit = inputs.get("change_mode")
        if explicit and explicit != "auto":
            return explicit
        has_figma = bool(inputs.get("figma_url"))
        has_prd = bool(inputs.get("prd_refs"))
        has_change_desc = bool(inputs.get("change_description"))
        if (has_figma or has_prd) and has_change_desc:
            return ChangeMode.MIXED.value
        if has_figma or has_prd:
            return ChangeMode.NEW_FEATURE.value
        return ChangeMode.REGRESSION.value

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
        state.phase_statuses = {p.value: PhaseStatus.PENDING.value for p in phases}
        state.phase_statuses[Phase.INTAKE.value] = PhaseStatus.COMPLETED.value
        state.phase_statuses[Phase.IMPACT_SPLIT.value] = PhaseStatus.COMPLETED.value

        skip_in_regression = {
            Phase.SENIOR_QA_BRAIN,
            Phase.PLAYWRIGHT_GENERATOR,
            Phase.BRIDGE,
        }
        if mode == ChangeMode.REGRESSION.value:
            for phase in skip_in_regression:
                if phase.value in state.phase_statuses:
                    state.phase_statuses[phase.value] = PhaseStatus.SKIPPED.value

        write_json(
            self.store.artifact_path(state.run_id, "impact_split.json"),
            {"change_mode": mode, "phases": [phase.value for phase in phases]},
        )
        self._mark(state, Phase.IMPACT_SPLIT, PhaseStatus.COMPLETED)
        return state

    def _phase_skill(self, state: RunState, phase: Phase, inputs: dict[str, Any]) -> RunState:
        """skill 阶段：标记当前该用哪个 skill，记录 SKILL.md 路径。"""
        self._mark(state, phase, PhaseStatus.RUNNING)
        skill_path = SKILL_PATHS[phase]
        state.artifacts[f"{phase.value}_skill_path"] = str(self.config.project_root / skill_path)

        instruction = self._build_instruction(state, phase)
        instruction_path = self.store.artifact_path(state.run_id, f"{phase.value}_instruction.md")
        write_text(instruction_path, instruction)
        state.artifacts[f"{phase.value}_instruction"] = str(instruction_path)

        self._mark(state, phase, PhaseStatus.BLOCKED)
        state.blocked_reason = f"请按 {skill_path} 执行，完成后用 advance 继续"
        state.status = RunStatus.BLOCKED.value
        self.store.save(state)
        return state

    def _phase_impact_analysis(self, state: RunState) -> RunState:
        self._mark(state, Phase.IMPACT_ANALYSIS, PhaseStatus.RUNNING)
        packet = self._requirement_packet(state)
        impact_payload = self._build_impact_payload(state, packet)
        overlap_decisions = self._build_overlap_decisions(
            impact_payload["new_cases"],
            impact_payload["existing_cases"],
        )
        legacy_tasks = self._load_seed_tasks(state)
        if not legacy_tasks:
            legacy_tasks = self._build_legacy_tasks(packet, overlap_decisions)
        gate = self._build_gate(legacy_tasks, round_index=0)
        selector_plan = self._build_selector_plan(packet, impact_payload, legacy_tasks)

        impact_path = self.store.artifact_path(state.run_id, "impact_candidates.json")
        overlap_path = self.store.artifact_path(state.run_id, "overlap_report.md")
        tasks_path = self.store.artifact_path(state.run_id, "legacy_update_tasks.json")
        gate_path = self.store.artifact_path(state.run_id, "legacy_update_gate.json")
        selector_path = self.store.artifact_path(state.run_id, "regression_selector_plan.json")

        write_json(impact_path, impact_payload)
        write_text(overlap_path, self._render_overlap_report(packet, overlap_decisions))
        write_json(tasks_path, [asdict(task) for task in legacy_tasks])
        write_json(gate_path, asdict(gate))
        write_json(selector_path, selector_plan)

        state.artifacts.update(
            {
                "impact_candidates": str(impact_path),
                "overlap_report": str(overlap_path),
                "legacy_update_tasks": str(tasks_path),
                "legacy_update_gate": str(gate_path),
                "regression_selector_plan": str(selector_path),
            }
        )
        state.blocked_reason = ""
        self._mark(state, Phase.IMPACT_ANALYSIS, PhaseStatus.COMPLETED)
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
        state.artifacts["regression_selector_plan"] = str(
            self._refresh_selector_plan(state, outcome.tasks)
        )

        if outcome.gate.all_completed:
            state.blocked_reason = ""
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.COMPLETED)
            return state

        if outcome.gate.has_manual_review:
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.BLOCKED)
            state.status = RunStatus.BLOCKED.value
            state.blocked_reason = (
                f"旧脚本更新第{round_index}轮后仍有 manual-review 任务，"
                f"需先处理当前阶段再继续"
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
            "",
            "## 产物清单",
        ]
        for key, value in sorted(state.artifacts.items()):
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## 阶段状态"])
        for phase_name, status in state.phase_statuses.items():
            lines.append(f"- {phase_name}: {status}")

        path = self.store.artifact_path(state.run_id, "final_report.md")
        write_text(path, "\n".join(lines) + "\n")
        state.artifacts["final_report"] = str(path)
        self._mark(state, Phase.FINAL_REPORT, PhaseStatus.COMPLETED)
        state.status = RunStatus.COMPLETED.value
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
            parts.extend([
                "",
                "## 要求",
                "- 按 SKILL.md 流程逐步执行，不要跳步",
                "- 生成分析报告后等待用户确认",
                "- 确认后生成 Markdown 测试用例",
            ])
            return "\n".join(parts)

        if phase == Phase.PLAYWRIGHT_GENERATOR:
            parts = [
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
                "- 阶段3代码生成时读取 test-case-authoring-spec.md 及模板",
            ]
            return "\n".join(parts)

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
            parts.extend([
                "",
                "## 要求",
                "- 优先消费 regression_selector_plan.json",
                "- 先 dry-run 预览，等用户确认后再真实执行",
                "- 若 selector_plan 缺少必要信息，再退回 module-map.md 做补充",
            ])
            return "\n".join(parts)

        return f"# 阶段: {phase.value}\n\n请读取 `{skill_path}` 并执行。"

    def _mark(self, state: RunState, phase: Phase, status: PhaseStatus) -> None:
        state.current_phase = phase.value
        state.phase_statuses[phase.value] = status.value
        if status == PhaseStatus.RUNNING:
            state.status = RunStatus.RUNNING.value
        state.touch()

    def complete_phase(self, run_id: str, phase_name: str, artifacts: dict[str, str] | None = None) -> RunState:
        """手动标记某个阶段完成并附加产物，然后推进。"""
        state = self.store.load(run_id)
        if artifacts:
            state.artifacts.update(artifacts)
        state.phase_statuses[phase_name] = PhaseStatus.COMPLETED.value
        state.blocked_reason = ""
        state.status = RunStatus.RUNNING.value
        self.store.save(state)
        return self.advance(run_id)

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
                matches.extend(
                    [
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
                        for case_ref in case_refs
                    ]
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
                        reason="新旧脚本命中同名脚本或相同 case_id，需并跑裁决",
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

    def _build_legacy_tasks(
        self,
        packet: dict[str, Any],
        overlap_decisions: list[OverlapDecision],
    ) -> list[LegacyUpdateTask]:
        tasks: list[LegacyUpdateTask] = []
        default_action = "update-assertion" if packet.get("change_description") else "re-record"
        max_rounds = int(self.config.thresholds.get("gates", {}).get("max_fix_rounds", 3))
        for decision in overlap_decisions:
            tasks.append(
                LegacyUpdateTask(
                    task_id=make_task_id("legacy"),
                    target_script=decision.existing_target,
                    target_case_id=decision.related_case_id,
                    target_nodeid=decision.related_nodeid,
                    impact_type=decision.decision,
                    recommended_action=default_action,
                    reason=decision.reason,
                    max_attempts=max_rounds,
                    details={
                        "module": (packet.get("candidate_modules") or [""])[0],
                        "site": packet.get("site", ""),
                    },
                )
            )
        return tasks

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

    def _render_overlap_report(
        self,
        packet: dict[str, Any],
        overlap_decisions: list[OverlapDecision],
    ) -> str:
        module = (packet.get("candidate_modules") or [""])[0]
        lines = [
            "# 重叠裁决报告",
            "",
            f"- 模块: {module}",
            f"- 站点: {packet.get('site', '')}",
            "",
        ]
        if not overlap_decisions:
            lines.append("本轮未检测到需要自动生成旧脚本更新任务的重叠项。")
            return "\n".join(lines) + "\n"

        lines.extend(
            [
                "| 新脚本 | 旧脚本 | 裁决 | 说明 |",
                "| --- | --- | --- | --- |",
            ]
        )
        for decision in overlap_decisions:
            lines.append(
                f"| `{decision.new_target}` | `{decision.existing_target}` | "
                f"`{decision.decision}` | {decision.reason} |"
            )
        return "\n".join(lines) + "\n"

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
            "selectors": [
                {"kind": "path", "value": path}
                for path in sorted(path for path in candidate_paths if path)
            ],
        }

    def _refresh_selector_plan(self, state: RunState, tasks: list[LegacyUpdateTask]) -> Path:
        packet = self._requirement_packet(state)
        impact_payload = read_json(state.artifacts.get("impact_candidates", ""), default={}) or {}
        selector_plan = self._build_selector_plan(packet, impact_payload, tasks)
        selector_path = self.store.artifact_path(state.run_id, "regression_selector_plan.json")
        write_json(selector_path, selector_plan)
        return selector_path
