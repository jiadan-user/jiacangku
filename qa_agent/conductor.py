"""
QA Agent 编排层 - 纯状态机。

只管阶段流转，不执行任何 skill 的内部逻辑。
每个阶段：标记当前该用哪个 skill → 提示用户 → 等待产物 → 下一步。
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from qa_agent.config import AppConfig
from qa_agent.io import read_json, write_json, write_text
from qa_agent.models import (
    ChangeMode,
    Phase,
    PhaseStatus,
    RequirementPacket,
    RunState,
    RunStatus,
    to_data,
)
from qa_agent.state import RunStore

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
    Phase.BRIDGE,
    Phase.OK_UI_REGRESSION,
    Phase.FINAL_REPORT,
]

REGRESSION_PHASES = [
    Phase.INTAKE,
    Phase.IMPACT_SPLIT,
    Phase.OK_UI_REGRESSION,
    Phase.FINAL_REPORT,
]

MIXED_PHASES = NEW_FEATURE_PHASES


class QAConductor:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.store = RunStore(config.qa_state_root)

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
        """推进到下一个待执行阶段。"""
        inputs = inputs or {}
        state = self.store.load(run_id)
        phases = self._phases_for_mode(state.change_mode)

        for phase in phases:
            ps = state.phase_statuses.get(phase.value, PhaseStatus.PENDING.value)
            if ps in (PhaseStatus.COMPLETED.value, PhaseStatus.SKIPPED.value):
                continue
            state = self._execute_phase(state, phase, inputs)
            break

        self.store.save(state)
        return state

    def _execute_phase(self, state: RunState, phase: Phase, inputs: dict[str, Any]) -> RunState:
        if phase == Phase.INTAKE:
            return self._phase_intake(state, inputs)
        if phase == Phase.IMPACT_SPLIT:
            return self._phase_impact_split(state, self._resolve_mode(inputs))
        if phase in (Phase.SENIOR_QA_BRAIN, Phase.PLAYWRIGHT_GENERATOR, Phase.OK_UI_REGRESSION):
            return self._phase_skill(state, phase, inputs)
        if phase == Phase.BRIDGE:
            return self._phase_bridge(state, inputs)
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

        skip_in_regression = {Phase.SENIOR_QA_BRAIN, Phase.PLAYWRIGHT_GENERATOR, Phase.BRIDGE}
        if mode == ChangeMode.REGRESSION.value:
            for p in skip_in_regression:
                if p.value in state.phase_statuses:
                    state.phase_statuses[p.value] = PhaseStatus.SKIPPED.value

        write_json(
            self.store.artifact_path(state.run_id, "impact_split.json"),
            {"change_mode": mode, "phases": [p.value for p in phases]},
        )
        self._mark(state, Phase.IMPACT_SPLIT, PhaseStatus.COMPLETED)
        return state

    def _phase_skill(self, state: RunState, phase: Phase, inputs: dict[str, Any]) -> RunState:
        """skill 阶段：标记当前该用哪个 skill，记录 SKILL.md 路径。不执行 skill 内部逻辑。"""
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

    def _phase_bridge(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        """衔接步骤：查重映射 + 提升守卫 + 入库。"""
        self._mark(state, Phase.BRIDGE, PhaseStatus.RUNNING)

        instruction = (
            "## 衔接步骤\n\n"
            "playwright-test-generator 已完成脚本生成。现在需要：\n\n"
            "1. **查重映射**：将生成的脚本和 `ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/` 下已有脚本对比去重\n"
            "2. **提升守卫**：对照 `test-case-authoring-spec.md` 和 `test-case-review-checklist.md` 检查脚本合规性\n"
            "3. **脚本入库**：将通过守卫的脚本复制到 `test_cases/<module>/`\n"
        )
        path = self.store.artifact_path(state.run_id, "bridge_instruction.md")
        write_text(path, instruction)
        state.artifacts["bridge_instruction"] = str(path)

        self._mark(state, Phase.BRIDGE, PhaseStatus.BLOCKED)
        state.blocked_reason = "请完成查重映射、提升守卫和脚本入库，完成后用 advance 继续"
        state.status = RunStatus.BLOCKED.value
        self.store.save(state)
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
        packet = read_json(state.artifacts.get("requirement_packet", ""), default={}) or {}

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
                f"- 测试用例文档: 阶段1(senior-qa-brain)生成的 Markdown 用例",
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
            parts.extend([
                "",
                "## 要求",
                "- 先看 module-map.md 确定 run 参数",
                "- 先 dry-run 预览，等用户确认后再真实执行",
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
