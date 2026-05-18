"""
QA Agent 编排层 - 纯状态机。

只管阶段流转，不执行 skill 的内部推理流程；编排层自带的阶段只做候选识别、
影响回归验证、任务编排和产物落盘。
"""
from __future__ import annotations

import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qa_agent.adapters.impact_verification import ImpactVerificationExecutor
from qa_agent.adapters.legacy_update import (
    PATCH_ACTIONS,
    PLAYWRIGHT_REGEN_ACTIONS,
    LegacyUpdateExecutor,
    make_task_id,
)
from qa_agent.agent_memory import MemoryExporter, MemoryStore
from qa_agent.agent_memory.candidate import build_candidate_from_text
from qa_agent.agent_memory.models import to_data as memory_to_data
from qa_agent.config import AppConfig
from qa_agent.io import read_json, read_text, write_json, write_text
from qa_agent.markdown_cases import parse_markdown_document
from qa_agent.models import (
    AttributionCategory,
    ChangeMode,
    DoctorCheck,
    DoctorResult,
    ImpactCandidate,
    ImpactRunStatus,
    ImpactVerificationRecord,
    LegacyUpdateGate,
    LegacyUpdateTask,
    LegacyUpdateTaskStatus,
    NextAction,
    NextActionKind,
    OverlapDecision,
    Phase,
    PhaseGateResult,
    PhaseStatus,
    PlaywrightCaseOutcome,
    PlaywrightOutcomeType,
    PlaywrightRecordingOutcome,
    PlaywrightRecordingOutcomeType,
    RequirementPacket,
    RunState,
    RunStatus,
    TextCaseManifest,
    TextCaseManifestEntry,
    UserConfirmationRecord,
    to_data,
    utc_now_iso,
)
from qa_agent.state import RunStore
from qa_agent.utils import normalize_text, run_command

SKILL_PATHS = {
    Phase.SENIOR_QA_BRAIN: "bundled/skills/senior-qa-brain/SKILL.md",
    Phase.PLAYWRIGHT_GENERATOR: "bundled/skills/playwright-test-generator/SKILL.md",
    Phase.OK_UI_REGRESSION: "bundled/skills/ok_autotest_ui_skill/SKILL.md",
    Phase.KNOWLEDGE_BASE_UPDATE: "bundled/skills/knowledge-base-manager/SKILL.md",
}

PHASE_REQUIRED_ARTIFACTS = {
    Phase.SENIOR_QA_BRAIN: ["analysis_report", "textcases"],
    Phase.PLAYWRIGHT_GENERATOR: [
        "playwright_recording_outcomes",
        "playwright_recording_report",
        "playwright_bug_report",
    ],
    Phase.IMPACT_VERIFICATION: [],
    Phase.OK_UI_REGRESSION: ["ok_ui_dry_run_preview", "ok_ui_execution_report", "release_recommendation"],
    Phase.KNOWLEDGE_BASE_UPDATE: ["knowledge_base_update_preview", "knowledge_base_update_result"],
}

PLAYWRIGHT_PROGRESS_KEY = "playwright_generator_progress"
PLAYWRIGHT_STAGE_RECORDING = "recording"
PLAYWRIGHT_STAGE_RECORDING_COMPLETED = "recording_completed"
PLAYWRIGHT_STAGE_SCRIPT_PENDING = "script_pending"
PLAYWRIGHT_STAGE_SCRIPT_COMPLETED = "script_completed"

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
        self._attach_memory_context(state, inputs)
        if inputs.get("doctor_result"):
            self._persist_doctor_result(state, inputs["doctor_result"])
        state.status = RunStatus.PLANNED.value
        self._refresh_next_action(state)
        self.store.save(state)
        return state

    def status(self, run_id: str) -> dict[str, Any]:
        state = self.store.load(run_id)
        data = to_data(state)
        stale_warning = self._stale_blocked_warning(state)
        if stale_warning:
            data["stale_warning"] = stale_warning
        return data

    def advance(self, run_id: str, inputs: dict[str, Any] | None = None) -> RunState:
        with self.store.locked_run(run_id):
            return self._advance_unlocked(run_id, inputs)

    def _advance_unlocked(self, run_id: str, inputs: dict[str, Any] | None = None) -> RunState:
        inputs = inputs or {}
        state = self.store.load(run_id)
        phases = self._phases_for_mode(state.change_mode)

        for phase in phases:
            phase_state = state.phase_statuses.get(phase.value, PhaseStatus.PENDING.value)
            if phase_state in (PhaseStatus.COMPLETED.value, PhaseStatus.SKIPPED.value):
                continue
            try:
                state = self._execute_phase(state, phase, inputs)
            except Exception as exc:
                self._set_error_state(state, exc)
                self.store.save(state)
                raise
            phase_state = state.phase_statuses.get(phase.value, PhaseStatus.PENDING.value)
            if phase_state == PhaseStatus.COMPLETED.value:
                continue
            self._refresh_next_action(state)
            self.store.save(state)
            return state

        if all(
            state.phase_statuses.get(phase.value) in (PhaseStatus.COMPLETED.value, PhaseStatus.SKIPPED.value)
            for phase in phases
        ):
            state.status = RunStatus.COMPLETED.value
            state.blocked_reason = ""
        self._refresh_next_action(state)
        self.store.save(state)
        return state

    def complete_phase(self, run_id: str, phase_name: str, artifacts: dict[str, str] | None = None) -> RunState:
        with self.store.locked_run(run_id):
            return self._complete_phase_unlocked(run_id, phase_name, artifacts)

    def _complete_phase_unlocked(
        self,
        run_id: str,
        phase_name: str,
        artifacts: dict[str, str] | None = None,
    ) -> RunState:
        state = self.store.load(run_id)
        if artifacts:
            state.artifacts.update(artifacts)
        phase = self._phase_from_name(phase_name)
        self._phase_resumed(state, phase)
        if phase == Phase.SENIOR_QA_BRAIN:
            state = self._complete_senior_qa_brain(state)
        elif phase == Phase.PLAYWRIGHT_GENERATOR:
            state = self._complete_playwright_generator(state)
        elif phase == Phase.IMPACT_VERIFICATION:
            state = self._confirm_impact_verification(state)
        elif phase == Phase.LEGACY_UPDATE:
            state = self._complete_legacy_update(state)
        elif phase == Phase.OK_UI_REGRESSION:
            state = self._complete_ok_ui_regression(state)
        elif phase == Phase.KNOWLEDGE_BASE_UPDATE:
            state = self._complete_knowledge_base_update(state)

        if state.phase_statuses.get(phase.value) == PhaseStatus.BLOCKED.value and state.blocked_reason:
            self._refresh_next_action(state)
            self.store.save(state)
            return state

        if phase == Phase.LEGACY_UPDATE:
            self._refresh_next_action(state)
            self.store.save(state)
            return self._advance_unlocked(run_id)

        state.phase_statuses[phase.value] = PhaseStatus.COMPLETED.value
        state.current_phase = phase.value
        state.blocked_reason = ""
        state.status = RunStatus.RUNNING.value
        self._phase_completed(state, phase)
        self._refresh_next_action(state)
        self.store.save(state)
        return self._advance_unlocked(run_id)

    def drive_to_action(
        self,
        run_id: str,
        inputs: dict[str, Any] | None = None,
        max_steps: int | None = None,
    ) -> RunState:
        with self.store.locked_run(run_id):
            return self._drive_to_action_unlocked(run_id, inputs, max_steps)

    def _drive_to_action_unlocked(
        self,
        run_id: str,
        inputs: dict[str, Any] | None = None,
        max_steps: int | None = None,
    ) -> RunState:
        phases = self._phases_for_mode(self.store.load(run_id).change_mode)
        default_steps = int(self.config.thresholds.get("gates", {}).get("max_fix_rounds", 3)) + len(phases) + 5
        limit = max_steps or default_steps
        state = self.store.load(run_id)
        for _ in range(limit):
            if self._is_actionable(state):
                self._refresh_next_action(state)
                self.store.save(state)
                return state
            try:
                state = self._advance_unlocked(run_id, inputs)
            except Exception as exc:
                state = self.store.load(run_id)
                if state.status != RunStatus.ERROR.value:
                    self._set_error_state(state, exc)
                    self.store.save(state)
                return state
            if self._is_actionable(state):
                self._refresh_next_action(state)
                self.store.save(state)
                return state
        self._set_error_state(state, RuntimeError(f"drive_to_action 超过最大自动推进步数 {limit}，已停止以防死循环"))
        self.store.save(state)
        return state

    def doctor(self) -> DoctorResult:
        checks: list[DoctorCheck] = []
        project_root = self.config.project_root
        checks.append(
            DoctorCheck(
                name="project_root",
                ok=project_root.exists(),
                severity="fatal",
                message=f"项目根目录: {project_root}",
            )
        )

        for phase, skill_path in SKILL_PATHS.items():
            absolute = project_root / skill_path
            checks.append(
                DoctorCheck(
                    name=f"skill:{phase.value}",
                    ok=absolute.exists(),
                    severity="fatal",
                    message=f"{phase.value} skill: {absolute}",
                )
            )

        paths = self.config.skills.get("paths", {})
        commands = self.config.skills.get("commands", {}).get("ok_ui_skill", {})
        knowledge_base_root = Path(paths.get("knowledge_base_root", ""))
        knowledge_base_manager_root = Path(paths.get("knowledge_base_manager_root", ""))
        regression_root = Path(paths.get("regression_project_root", ""))
        venv_python = Path(commands.get("venv_python", ""))
        ok_script = Path(commands.get("script", ""))

        checks.extend(
            [
                DoctorCheck(
                    name="knowledge_base_root",
                    ok=knowledge_base_root.exists(),
                    severity="fatal",
                    message=f"知识库目录: {knowledge_base_root}",
                ),
                DoctorCheck(
                    name="knowledge_base_manager_root",
                    ok=knowledge_base_manager_root.exists(),
                    severity="fatal",
                    message=f"knowledge-base-manager: {knowledge_base_manager_root}",
                ),
                DoctorCheck(
                    name="regression_project_root",
                    ok=regression_root.exists(),
                    severity="warning",
                    message=f"回归项目目录: {regression_root}",
                ),
                DoctorCheck(
                    name="ok_ui_venv_python",
                    ok=venv_python.exists(),
                    severity="warning",
                    message=f"ok_autotest_ui Python: {venv_python}",
                ),
                DoctorCheck(
                    name="ok_ui_script",
                    ok=ok_script.exists(),
                    severity="warning",
                    message=f"ok_autotest_ui 脚本: {ok_script}",
                ),
            ]
        )

        if venv_python.exists():
            pytest_proc = run_command([str(venv_python), "-m", "pytest", "--version"])
            checks.append(
                DoctorCheck(
                    name="pytest",
                    ok=pytest_proc.returncode == 0,
                    severity="warning",
                    message=(pytest_proc.stdout or pytest_proc.stderr).strip()[:240] or "pytest 不可用",
                )
            )
            playwright_proc = run_command([str(venv_python), "-m", "playwright", "--version"])
            checks.append(
                DoctorCheck(
                    name="playwright",
                    ok=playwright_proc.returncode == 0,
                    severity="warning",
                    message=(playwright_proc.stdout or playwright_proc.stderr).strip()[:240] or "playwright 不可用",
                )
            )
            if ok_script.exists() and regression_root.exists():
                doctor_proc = run_command(
                    [str(venv_python), str(ok_script), "doctor"],
                    cwd=regression_root,
                    env={"PYTHONPATH": str(regression_root)},
                )
                checks.append(
                    DoctorCheck(
                        name="ok_ui_doctor",
                        ok=doctor_proc.returncode == 0,
                        severity="warning",
                        message=(doctor_proc.stdout or doctor_proc.stderr).strip()[:240] or "ok_ui doctor 未通过",
                    )
                )

        has_fatal = any(not check.ok and check.severity == "fatal" for check in checks)
        return DoctorResult(ok=not any(not check.ok for check in checks), has_fatal=has_fatal, checks=checks)

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

    def _phase_from_name(self, phase_name: str) -> Phase:
        try:
            return Phase(phase_name)
        except ValueError as exc:
            raise ValueError(f"未知阶段: {phase_name}") from exc

    def _phases_for_mode(self, mode: str) -> list[Phase]:
        if mode == ChangeMode.REGRESSION.value:
            return REGRESSION_PHASES
        if mode == ChangeMode.MIXED.value:
            return MIXED_PHASES
        return NEW_FEATURE_PHASES

    def _is_actionable(self, state: RunState) -> bool:
        if state.status in (RunStatus.BLOCKED.value, RunStatus.COMPLETED.value, RunStatus.ERROR.value):
            return True
        return False

    def _refresh_next_action(self, state: RunState) -> None:
        if state.status == RunStatus.BLOCKED.value:
            if not state.blocked_since:
                state.blocked_since = utc_now_iso()
        else:
            state.blocked_since = ""

        if state.status == RunStatus.COMPLETED.value:
            state.next_action = NextAction(
                kind=NextActionKind.COMPLETED.value,
                phase=state.current_phase,
                summary="运行已完成",
            )
            return

        if state.status == RunStatus.ERROR.value:
            state.next_action = NextAction(
                kind=NextActionKind.ERROR.value,
                phase=state.current_phase,
                summary=state.error_reason or "运行出错",
                details={"error_reason": state.error_reason},
            )
            return

        phase = self._phase_from_name(state.current_phase)
        if state.status == RunStatus.BLOCKED.value:
            if phase == Phase.PLAYWRIGHT_GENERATOR:
                action = self._playwright_next_action(state)
                if action:
                    state.next_action = action
                    return
            if phase in SKILL_PATHS:
                skill_path = str(self.config.project_root / SKILL_PATHS[phase])
                if not Path(skill_path).exists():
                    state.next_action = NextAction(
                        kind=NextActionKind.FIX_ENVIRONMENT.value,
                        phase=phase.value,
                        summary=state.blocked_reason or f"缺少 {phase.value} skill，请先同步内嵌资源",
                        skill_path=skill_path,
                        resume_command="python -m qa_agent.cli doctor",
                    )
                    return
                kind = NextActionKind.RUN_SKILL.value
                if phase == Phase.KNOWLEDGE_BASE_UPDATE:
                    summary = "执行 knowledge-base-manager，生成预览并确认写入"
                else:
                    summary = f"执行 {phase.value} skill 并提交产物"
                state.next_action = NextAction(
                    kind=kind,
                    phase=phase.value,
                    summary=summary,
                    skill_path=skill_path,
                    instruction_path=state.artifacts.get(f"{phase.value}_instruction", ""),
                    required_artifacts=PHASE_REQUIRED_ARTIFACTS.get(phase, []),
                    resume_command=self._complete_command(state.run_id, phase),
                    details={"memory_context": state.artifacts.get("memory_context", "")},
                )
                return
            if phase == Phase.IMPACT_VERIFICATION:
                state.next_action = NextAction(
                    kind=NextActionKind.CONFIRM_PHASE.value,
                    phase=phase.value,
                    summary="确认变更归因报告后继续",
                    required_artifacts=[],
                    resume_command=f"python -m qa_agent.cli complete --run-id {state.run_id} --phase {phase.value}",
                    details={"report": state.artifacts.get("change_attribution_report", "")},
                )
                return
            if phase == Phase.LEGACY_UPDATE:
                if self._legacy_playwright_request_active(state):
                    state.next_action = NextAction(
                        kind=NextActionKind.RUN_SKILL.value,
                        phase=phase.value,
                        summary="调用 playwright-test-generator 为旧脚本生成候选替换版本",
                        skill_path=str(self.config.project_root / SKILL_PATHS[Phase.PLAYWRIGHT_GENERATOR]),
                        instruction_path=state.artifacts.get("legacy_rerecord_instruction", ""),
                        required_artifacts=["legacy_update_candidate_manifest"],
                        resume_command=(
                            f"python -m qa_agent.cli complete --run-id {state.run_id} "
                            f"--phase {phase.value} --artifact legacy_update_candidate_manifest=<path>"
                        ),
                        details={
                            "request": state.artifacts.get("legacy_rerecord_request", ""),
                            "tasks": state.artifacts.get("legacy_update_tasks", ""),
                        },
                    )
                    return
                state.next_action = NextAction(
                    kind=NextActionKind.MANUAL_REVIEW.value,
                    phase=phase.value,
                    summary=state.blocked_reason or "旧脚本更新需要人工介入",
                    required_artifacts=[],
                    resume_command=f"python -m qa_agent.cli next --run-id {state.run_id}",
                    details={"legacy_update_tasks": state.artifacts.get("legacy_update_tasks", "")},
                )
                return

        state.next_action = NextAction(
            kind=NextActionKind.CONTINUE_AUTO.value,
            phase=state.current_phase,
            summary=state.blocked_reason or "继续推进到下一个动作点",
            resume_command=f"python -m qa_agent.cli next --run-id {state.run_id}",
        )

    def _playwright_next_action(self, state: RunState) -> NextAction | None:
        skill_path = str(self.config.project_root / SKILL_PATHS[Phase.PLAYWRIGHT_GENERATOR])
        if not Path(skill_path).exists():
            return NextAction(
                kind=NextActionKind.FIX_ENVIRONMENT.value,
                phase=Phase.PLAYWRIGHT_GENERATOR.value,
                summary=state.blocked_reason or "缺少 playwright-test-generator skill，请先同步内嵌资源",
                skill_path=skill_path,
                resume_command="python -m qa_agent.cli doctor",
            )

        progress = self._playwright_progress(state)
        stage = progress.get("stage", PLAYWRIGHT_STAGE_RECORDING)
        if stage == PLAYWRIGHT_STAGE_RECORDING_COMPLETED:
            return NextAction(
                kind=NextActionKind.CONFIRM_PHASE.value,
                phase=Phase.PLAYWRIGHT_GENERATOR.value,
                summary="确认阶段2A录制执行结果和 bug list 后继续脚本生成",
                required_artifacts=[],
                resume_command=f"python -m qa_agent.cli complete --run-id {state.run_id} --phase {Phase.PLAYWRIGHT_GENERATOR.value}",
                details={
                    "recording_report": state.artifacts.get("playwright_recording_report", ""),
                    "bug_report": state.artifacts.get("playwright_bug_report", ""),
                    "recording_outcomes": state.artifacts.get("playwright_recording_outcomes", ""),
                    "proof_artifacts_manifest": state.artifacts.get("proof_artifacts_manifest", ""),
                },
            )
        if stage == PLAYWRIGHT_STAGE_SCRIPT_PENDING:
            return NextAction(
                kind=NextActionKind.RUN_SKILL.value,
                phase=Phase.PLAYWRIGHT_GENERATOR.value,
                summary="执行 playwright-test-generator 阶段2B，生成 Python 脚本并完成自测",
                skill_path=skill_path,
                instruction_path=state.artifacts.get(f"{Phase.PLAYWRIGHT_GENERATOR.value}_instruction", ""),
                required_artifacts=["playwright_case_outcomes"],
                resume_command=(
                    f"python -m qa_agent.cli complete --run-id {state.run_id} "
                    f"--phase {Phase.PLAYWRIGHT_GENERATOR.value} --artifact playwright_case_outcomes=<path>"
                ),
                details={
                    "recording_outcomes": state.artifacts.get("playwright_recording_outcomes", ""),
                    "recording_report": state.artifacts.get("playwright_recording_report", ""),
                    "memory_context": state.artifacts.get("memory_context", ""),
                },
            )
        return None

    def _complete_command(self, run_id: str, phase: Phase) -> str:
        parts = ["python -m qa_agent.cli complete", f"--run-id {run_id}", f"--phase {phase.value}"]
        for artifact_key in PHASE_REQUIRED_ARTIFACTS.get(phase, []):
            parts.append(f"--artifact {artifact_key}=<path>")
        return " ".join(parts)

    def _set_error_state(self, state: RunState, exc: Exception) -> None:
        state.status = RunStatus.ERROR.value
        state.phase_statuses[state.current_phase] = PhaseStatus.ERROR.value
        state.error_reason = f"{type(exc).__name__}: {exc}"
        state.blocked_reason = "自动推进时发生错误，请查看 error_reason"
        try:
            self._phase_error(state, self._phase_from_name(state.current_phase))
        except ValueError:
            pass
        self._refresh_next_action(state)

    def _stale_blocked_warning(self, state: RunState) -> str:
        if state.status != RunStatus.BLOCKED.value or not state.blocked_since:
            return ""
        threshold = int(self.config.thresholds.get("gates", {}).get("blocked_warn_after_seconds", 1800))
        try:
            blocked_at = datetime.fromisoformat(state.blocked_since)
        except ValueError:
            return ""
        seconds = int((datetime.now(timezone.utc) - blocked_at).total_seconds())
        if seconds < threshold:
            return ""
        minutes = seconds // 60
        return f"已阻塞 {minutes} 分钟，建议检查 skill 是否已完成或是否缺少 artifact。"

    def _persist_doctor_result(self, state: RunState, doctor_result: dict[str, Any] | DoctorResult) -> None:
        path = self.store.artifact_path(state.run_id, "doctor_result.json")
        write_json(path, to_data(doctor_result))
        state.artifacts["doctor_result"] = str(path)

    def _attach_memory_context(self, state: RunState, inputs: dict[str, Any]) -> None:
        query = self._memory_query_from_inputs(inputs)
        memory_root = self.config.agent_memory_root
        exporter = MemoryExporter(memory_root)
        content = exporter.render_context(query, limit=8, include_empty=True)
        path = self.store.artifact_path(state.run_id, "memory_context.md")
        write_text(path, content)
        state.artifacts["memory_context"] = str(path)

    def _memory_query_from_inputs(self, inputs: dict[str, Any]) -> str:
        parts: list[str] = []
        for key in ("change_mode", "site", "module", "feature", "change_description", "figma_url"):
            value = inputs.get(key)
            if value:
                parts.extend(self._split_scope_values(value) if key in {"site", "module"} else [str(value)])
        for ref in inputs.get("prd_refs", []) or []:
            parts.append(str(ref))
        return " ".join(parts)

    def _split_scope_values(self, value: Any) -> list[str]:
        raw_values = value if isinstance(value, list) else [value]
        values: list[str] = []
        seen: set[str] = set()
        for raw in raw_values:
            if raw is None:
                continue
            for item in re.split(r"[,，]+", str(raw)):
                normalized = item.strip()
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                values.append(normalized)
        return values

    def _requested_modules(self, packet: dict[str, Any]) -> list[str]:
        return self._split_scope_values(packet.get("requested_modules") or packet.get("candidate_modules") or [])

    def _requested_sites(self, packet: dict[str, Any]) -> list[str]:
        sites = self._split_scope_values(packet.get("requested_sites") or [])
        if sites:
            return sites
        return self._split_scope_values(packet.get("site", ""))

    def _phase_intake(self, state: RunState, inputs: dict[str, Any]) -> RunState:
        if state.artifacts.get("requirement_packet"):
            self._mark(state, Phase.INTAKE, PhaseStatus.COMPLETED)
            return state
        self._mark(state, Phase.INTAKE, PhaseStatus.RUNNING)
        modules = self._split_scope_values(inputs.get("module"))
        sites = self._split_scope_values(inputs.get("site"))
        packet = RequirementPacket(
            change_mode=state.change_mode,
            figma_url=inputs.get("figma_url", ""),
            prd_refs=list(inputs.get("prd_refs", []) or []),
            candidate_modules=modules,
            site=sites[0] if sites else "",
            requested_modules=modules,
            requested_sites=sites,
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
        if (
            state.artifacts.get("impact_split")
            and state.phase_statuses.get(Phase.IMPACT_SPLIT.value) == PhaseStatus.COMPLETED.value
        ):
            return state
        self._mark(state, Phase.IMPACT_SPLIT, PhaseStatus.RUNNING)
        state.change_mode = mode
        phases = self._phases_for_mode(mode)
        state.phase_statuses = {phase.value: PhaseStatus.PENDING.value for phase in phases}
        state.phase_statuses[Phase.INTAKE.value] = PhaseStatus.COMPLETED.value
        state.phase_statuses[Phase.IMPACT_SPLIT.value] = PhaseStatus.COMPLETED.value
        split_path = self.store.artifact_path(state.run_id, "impact_split.json")
        write_json(split_path, {"change_mode": mode, "phases": [phase.value for phase in phases]})
        state.artifacts["impact_split"] = str(split_path)
        self._mark(state, Phase.IMPACT_SPLIT, PhaseStatus.COMPLETED)
        return state

    def _phase_skill(self, state: RunState, phase: Phase, inputs: dict[str, Any]) -> RunState:
        del inputs
        self._mark(state, phase, PhaseStatus.RUNNING)
        skill_path = SKILL_PATHS[phase]
        absolute_skill_path = self.config.project_root / skill_path
        state.artifacts[f"{phase.value}_skill_path"] = str(absolute_skill_path)

        self._write_phase_instruction(state, phase)

        self._mark(state, phase, PhaseStatus.BLOCKED)
        if not absolute_skill_path.exists():
            state.blocked_reason = f"缺少 {skill_path}，请先同步内嵌资源后再继续"
        elif phase == Phase.KNOWLEDGE_BASE_UPDATE:
            state.blocked_reason = f"请按 {skill_path} 先生成 KB 预览、等待确认、再写入，完成后用 complete 继续"
        else:
            state.blocked_reason = f"请按 {skill_path} 执行，完成后用 complete 继续"
        state.status = RunStatus.BLOCKED.value
        return state

    def _write_phase_instruction(self, state: RunState, phase: Phase) -> str:
        instruction_path = self.store.artifact_path(state.run_id, f"{phase.value}_instruction.md")
        write_text(instruction_path, self._build_instruction(state, phase))
        state.artifacts[f"{phase.value}_instruction"] = str(instruction_path)
        return str(instruction_path)

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
        self._append_confirmation(
            state,
            UserConfirmationRecord(
                phase=Phase.IMPACT_VERIFICATION.value,
                summary="已确认变更归因报告，可继续进入旧脚本更新与新脚本 promotion 阶段",
                details={"tasks_generated": len(tasks)},
            ),
        )
        state.blocked_reason = ""
        return state

    def _complete_senior_qa_brain(self, state: RunState) -> RunState:
        gate = self._validate_phase1_outputs(state)
        self._store_gate_result(state, "phase1_gate_result", gate)
        if not gate.ok:
            return self._block_with_gate(state, Phase.SENIOR_QA_BRAIN, gate)
        self._append_confirmation(
            state,
            UserConfirmationRecord(
                phase=Phase.SENIOR_QA_BRAIN.value,
                summary="已确认分析报告并归档文本用例草稿",
                details={"kb_text_case_draft_path": state.artifacts.get("kb_text_case_draft_path", "")},
            ),
        )
        state.blocked_reason = ""
        return state

    def _complete_playwright_generator(self, state: RunState) -> RunState:
        progress = self._playwright_progress(state)
        stage = progress.get("stage", PLAYWRIGHT_STAGE_RECORDING)
        if stage == PLAYWRIGHT_STAGE_RECORDING_COMPLETED:
            recording_payload = read_json(
                self._artifact_value(state, "playwright_recording_outcomes", "recording_outcomes"),
                default=[],
            ) or []
            recording_passed_count = sum(
                1
                for item in recording_payload
                if isinstance(item, dict) and item.get("outcome") == PlaywrightRecordingOutcomeType.RECORDING_PASSED.value
            )
            self._append_confirmation(
                state,
                UserConfirmationRecord(
                    phase=Phase.PLAYWRIGHT_GENERATOR.value,
                    summary="已确认阶段2A录制执行结果，进入阶段2B脚本生成自测",
                    details={
                        "playwright_recording_outcomes": state.artifacts.get("playwright_recording_outcomes", ""),
                        "playwright_recording_report": state.artifacts.get("playwright_recording_report", ""),
                        "playwright_bug_report": state.artifacts.get("playwright_bug_report", ""),
                    },
                ),
            )
            if recording_passed_count == 0:
                case_outcomes_path = self.store.artifact_path(state.run_id, "playwright_case_outcomes.json")
                generated_manifest_path = self.store.artifact_path(state.run_id, "generated_scripts_manifest.json")
                write_json(case_outcomes_path, [])
                write_json(generated_manifest_path, [])
                state.artifacts["playwright_case_outcomes"] = str(case_outcomes_path)
                state.artifacts["generated_scripts_manifest"] = str(generated_manifest_path)
                self._store_gate_result(
                    state,
                    "phase2_gate_result",
                    PhaseGateResult(
                        phase=Phase.PLAYWRIGHT_GENERATOR.value,
                        ok=True,
                        summary="阶段2A没有 recording_passed 用例，阶段2B脚本生成自动跳过。",
                        details={
                            "playwright_recording_outcomes": state.artifacts.get("playwright_recording_outcomes", ""),
                            "playwright_case_outcomes": str(case_outcomes_path),
                            "generated_scripts_manifest": str(generated_manifest_path),
                            "recording_passed_count": 0,
                        },
                    ),
                )
                self._write_playwright_progress(
                    state,
                    stage=PLAYWRIGHT_STAGE_SCRIPT_COMPLETED,
                    recording_confirmed=True,
                    script_completed_at=utc_now_iso(),
                    script_skipped_reason="no_recording_passed_cases",
                )
                state.blocked_reason = ""
                return state
            self._write_playwright_progress(
                state,
                stage=PLAYWRIGHT_STAGE_SCRIPT_PENDING,
                recording_confirmed=True,
                script_started_at=utc_now_iso(),
            )
            self._write_phase_instruction(state, Phase.PLAYWRIGHT_GENERATOR)
            self._mark(state, Phase.PLAYWRIGHT_GENERATOR, PhaseStatus.BLOCKED)
            state.status = RunStatus.BLOCKED.value
            state.blocked_reason = "阶段2A已确认，请执行阶段2B生成 Python 脚本并完成自测"
            return state

        if stage == PLAYWRIGHT_STAGE_SCRIPT_PENDING:
            gate = self._validate_phase2_script_outputs(state)
            self._store_gate_result(state, "phase2_gate_result", gate)
            if not gate.ok:
                self._write_playwright_progress(state, stage=PLAYWRIGHT_STAGE_SCRIPT_PENDING)
                return self._block_with_gate(state, Phase.PLAYWRIGHT_GENERATOR, gate)
            self._write_playwright_progress(state, stage=PLAYWRIGHT_STAGE_SCRIPT_COMPLETED, script_completed_at=utc_now_iso())
            self._append_confirmation(
                state,
                UserConfirmationRecord(
                    phase=Phase.PLAYWRIGHT_GENERATOR.value,
                    summary="已验收 playwright Python 脚本生成与自测结果",
                    details={
                        "playwright_case_outcomes": state.artifacts.get("playwright_case_outcomes", ""),
                        "generated_scripts_manifest": state.artifacts.get("generated_scripts_manifest", ""),
                    },
                ),
            )
            state.blocked_reason = ""
            return state

        gate = self._validate_phase2_recording_outputs(state)
        self._store_gate_result(state, "phase2_recording_gate_result", gate)
        if not gate.ok:
            return self._block_with_gate(state, Phase.PLAYWRIGHT_GENERATOR, gate)
        self._write_playwright_progress(
            state,
            stage=PLAYWRIGHT_STAGE_RECORDING_COMPLETED,
            recording_completed_at=utc_now_iso(),
        )
        self._mark(state, Phase.PLAYWRIGHT_GENERATOR, PhaseStatus.BLOCKED)
        state.status = RunStatus.BLOCKED.value
        state.blocked_reason = "阶段2A录制执行已完成，请先确认录制报告和 bug list，再进入 Python 脚本生成"
        return state

    def _complete_legacy_update(self, state: RunState) -> RunState:
        manifest_path = self._artifact_value(
            state,
            "legacy_update_candidate_manifest",
            "legacy_rerecord_candidate_manifest",
        )
        tasks = self._load_legacy_tasks(state)
        if not manifest_path or not read_json(manifest_path, default=None):
            self._write_legacy_rerecord_request(state, self._legacy_tasks_needing_playwright(tasks))
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.BLOCKED)
            state.status = RunStatus.BLOCKED.value
            state.blocked_reason = "缺少 legacy_update_candidate_manifest，无法恢复旧脚本更新循环"
            return state

        payload = read_json(manifest_path, default=[]) or []
        entries = payload.get("tasks", []) if isinstance(payload, dict) else payload
        if not isinstance(entries, list):
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.BLOCKED)
            state.status = RunStatus.BLOCKED.value
            state.blocked_reason = "legacy_update_candidate_manifest 格式错误，期望 list 或 {tasks: [...]}"
            return state

        errors = self._apply_legacy_candidate_manifest(tasks, entries, manifest_path)
        if errors:
            self._write_legacy_rerecord_request(state, self._legacy_tasks_needing_playwright(tasks))
            self._persist_legacy_tasks_and_gate(state, tasks, self._current_legacy_round_index(state))
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.BLOCKED)
            state.status = RunStatus.BLOCKED.value
            state.blocked_reason = "legacy_update_candidate_manifest 未通过校验: " + "；".join(errors[:3])
            return state

        state.artifacts["legacy_update_candidate_manifest"] = manifest_path
        self._persist_legacy_tasks_and_gate(state, tasks, self._current_legacy_round_index(state))
        self._append_confirmation(
            state,
            UserConfirmationRecord(
                phase=Phase.LEGACY_UPDATE.value,
                summary="已接收 playwright-test-generator 候选脚本，可恢复旧脚本更新循环",
                details={"legacy_update_candidate_manifest": manifest_path},
            ),
        )
        self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.RUNNING)
        state.status = RunStatus.RUNNING.value
        state.blocked_reason = ""
        return state

    def _complete_ok_ui_regression(self, state: RunState) -> RunState:
        gate = self._validate_phase3_outputs(state)
        self._store_gate_result(state, "phase3_gate_result", gate)
        if not gate.ok:
            return self._block_with_gate(state, Phase.OK_UI_REGRESSION, gate)
        self._append_confirmation(
            state,
            UserConfirmationRecord(
                phase=Phase.OK_UI_REGRESSION.value,
                summary="已确认 dry-run 与真实回归结果，可生成最终报告并继续更新知识库",
                details={
                    "ok_ui_dry_run_preview": state.artifacts.get("ok_ui_dry_run_preview", ""),
                    "ok_ui_execution_report": self._artifact_value(
                        state,
                        "ok_ui_execution_report",
                        "ok_ui_report",
                    ),
                },
            ),
        )
        state.blocked_reason = ""
        return state

    def _complete_knowledge_base_update(self, state: RunState) -> RunState:
        gate = self._validate_knowledge_base_outputs(state)
        self._store_gate_result(state, "knowledge_base_gate_result", gate)
        if not gate.ok:
            return self._block_with_gate(state, Phase.KNOWLEDGE_BASE_UPDATE, gate)
        self._append_confirmation(
            state,
            UserConfirmationRecord(
                phase=Phase.KNOWLEDGE_BASE_UPDATE.value,
                summary="已确认 knowledge base 预览并完成写入",
                details={
                    "knowledge_base_update_preview": state.artifacts.get("knowledge_base_update_preview", ""),
                    "knowledge_base_update_result": state.artifacts.get("knowledge_base_update_result", ""),
                },
            ),
        )
        state.blocked_reason = ""
        return state

    def _validate_phase1_outputs(self, state: RunState) -> PhaseGateResult:
        packet = self._requirement_packet(state)
        report_path = self._artifact_value(state, "analysis_report")
        textcases_path = self._artifact_value(state, "textcases", "testcases")
        reasons: list[str] = []
        warnings: list[str] = []

        report_text = read_text(report_path)
        textcases_text = read_text(textcases_path)
        if not report_text:
            reasons.append("缺少 analysis_report，或分析报告内容为空。")
        if not textcases_text:
            reasons.append("缺少 textcases，或测试用例文档内容为空。")

        rule_paths, invalid_rule_routes = self._knowledge_base_rule_paths(packet)
        if invalid_rule_routes:
            reasons.extend(invalid_rule_routes)
        if report_text:
            if rule_paths and "知识库依据" not in report_text:
                reasons.append("分析报告缺少“知识库依据”章节，无法确认已读取业务规则库。")
            if not rule_paths and not self._mentions_kb_miss(report_text):
                reasons.append("业务规则库未命中时，分析报告必须明确写出“规则库未命中”或“知识库未命中”。")
        if textcases_text:
            if "业务属性" not in textcases_text:
                reasons.append("测试用例文档缺少“业务属性”说明。")
            if "测试范围" not in textcases_text:
                reasons.append("测试用例文档缺少“测试范围”说明。")

        document = parse_markdown_document(textcases_path) if textcases_text else None
        environment = document.environment if document else {}
        if not environment:
            reasons.append("测试用例文档缺少“测试环境配置”表格。")

        cases = [
            TextCaseManifestEntry(
                tc_id=case.tc_id,
                title=case.title,
                priority=case.priority,
                test_type=case.test_type,
                ui_automatable=case.ui_automatable,
                ui_automation_label=case.ui_automation_label,
                preconditions=case.preconditions,
                steps=case.steps,
                expected_results=case.expected_results,
                source_doc=case.source_doc,
            )
            for case in (document.cases if document else [])
        ]
        if not cases:
            reasons.append("测试用例文档中未解析到任何用例。")

        for case in cases:
            missing = []
            if not case.tc_id:
                missing.append("TC编号")
            if not case.preconditions:
                missing.append("前置条件")
            if not case.steps:
                missing.append("执行步骤")
            if not case.expected_results:
                missing.append("预期结果")
            if not case.priority:
                missing.append("优先级")
            if not case.test_type:
                missing.append("测试类型")
            if not case.ui_automation_label:
                missing.append("UI自动化")
            if missing:
                reasons.append(f"{case.tc_id or case.title or '未命名用例'} 缺少字段: {', '.join(missing)}。")
            if case.ui_automatable:
                precondition_reason = self._executable_precondition_issue(case)
                if precondition_reason:
                    reasons.append(f"{case.tc_id or case.title or '未命名用例'} 前置条件不可执行: {precondition_reason}")

        bucket = self._knowledge_base_bucket(packet)
        if not bucket:
            reasons.append(
                f"模块 `{(packet.get('candidate_modules') or [''])[0]}` 缺少知识库文本用例路由，"
                "请先在 config/knowledge_base_routing.yaml 中补齐。"
            )
        elif not self._is_safe_relative_fragment(bucket):
            reasons.append(f"知识库文本用例 bucket 必须是相对路径片段，不能是绝对路径或包含 `..`: {bucket}")

        kb_path = ""
        if not reasons:
            target_path = self._knowledge_base_draft_path(packet, textcases_path, bucket)
            write_text(target_path, textcases_text)
            manifest = TextCaseManifest(
                module=(packet.get("candidate_modules") or [""])[0],
                site=packet.get("site", ""),
                feature_name=packet.get("feature_name", ""),
                source_doc=textcases_path,
                kb_text_case_draft_path=str(target_path),
                environment=environment,
                cases=cases,
                business_attributes=self._extract_document_section_lines(textcases_text, "业务属性"),
                test_scope=self._extract_document_section_lines(textcases_text, "测试范围"),
                rule_library_paths=[str(path) for path in rule_paths],
            )
            manifest_path = self.store.artifact_path(state.run_id, "text_case_manifest.json")
            write_json(manifest_path, to_data(manifest))
            state.artifacts["text_case_manifest"] = str(manifest_path)
            state.artifacts["kb_text_case_draft_path"] = str(target_path)
            kb_path = str(target_path)
        else:
            warnings.append("阶段1未通过门禁前，不会写入 knowledge base 文本用例草稿。")

        return PhaseGateResult(
            phase=Phase.SENIOR_QA_BRAIN.value,
            ok=not reasons,
            summary=(
                f"阶段1门禁通过，共解析 {len(cases)} 条用例，并已归档到 {kb_path}"
                if not reasons
                else "阶段1门禁未通过，需补齐分析报告/测试用例结构。"
            ),
            blocking_reasons=reasons,
            warnings=warnings,
            details={
                "analysis_report": report_path,
                "textcases": textcases_path,
                "case_count": len(cases),
                "ui_automatable_count": sum(case.ui_automatable for case in cases),
                "environment_keys": sorted(environment.keys()),
                "kb_text_case_draft_path": kb_path,
                "rule_library_paths": [str(path) for path in rule_paths],
            },
        )

    def _validate_phase2_recording_outputs(self, state: RunState) -> PhaseGateResult:
        manifest_payload = read_json(state.artifacts.get("text_case_manifest", ""), default={}) or {}
        reasons: list[str] = []
        warnings: list[str] = []
        if not manifest_payload:
            reasons.append("缺少 text_case_manifest.json，无法校验阶段2A录制闭环。")

        report_path = self._artifact_value(state, "playwright_recording_report", "recording_report")
        report_text = read_text(report_path)
        if not report_text:
            reasons.append("缺少 playwright_recording_report.md，或录制执行报告为空。")
        elif len(report_text) > 20000:
            warnings.append("playwright_recording_report.md 内容偏长；建议只保留同事可读的执行进度摘要。")

        bug_report_path = self._artifact_value(state, "playwright_bug_report", "bug_report")
        bug_report_text = read_text(bug_report_path)
        if not bug_report_text:
            reasons.append("缺少 playwright_bug_report.md，或 bug list 为空；即使无 bug 也必须写明本轮未发现 bug。")

        execution_plan_path = self._artifact_value(state, "stage2a_execution_plan", "playwright_stage2a_execution_plan")
        if not read_text(execution_plan_path):
            warnings.append("缺少 stage2a_execution_plan.json；不阻塞阶段2A交付，但建议补充批次计划用于追溯。")

        outcomes_path = self._artifact_value(state, "playwright_recording_outcomes", "recording_outcomes")
        outcome_payload = read_json(outcomes_path, default=[]) or []
        if not outcome_payload:
            reasons.append("缺少 playwright_recording_outcomes.json，无法确认每条可自动化用例的录制结局。")
        if outcome_payload and not isinstance(outcome_payload, list):
            reasons.append("playwright_recording_outcomes.json 必须是数组。")
            outcome_payload = []

        automatable_cases = [
            item["tc_id"]
            for item in manifest_payload.get("cases", [])
            if item.get("ui_automatable")
        ]
        outcomes: list[PlaywrightRecordingOutcome] = []
        for index, item in enumerate(outcome_payload):
            if not isinstance(item, dict):
                reasons.append(f"playwright_recording_outcomes.json 第 {index + 1} 项不是对象。")
                continue
            try:
                outcomes.append(PlaywrightRecordingOutcome(**item))
            except TypeError as exc:
                reasons.append(f"playwright_recording_outcomes.json 第 {index + 1} 项格式错误: {exc}")
        grouped: dict[str, list[PlaywrightRecordingOutcome]] = {}
        invalid_outcome_case_ids: set[str] = set()
        allowed_outcomes = {item.value for item in PlaywrightRecordingOutcomeType}
        for outcome in outcomes:
            grouped.setdefault(outcome.tc_id, []).append(outcome)
            if outcome.outcome == "manual_review":
                invalid_outcome_case_ids.add(outcome.tc_id)
                reasons.append(
                    f"{outcome.tc_id} 标记为 manual_review；阶段2A不再允许该状态，"
                    "不符合预期或阻塞验证请记录为 bug_recorded。"
                )
            elif outcome.outcome not in allowed_outcomes:
                invalid_outcome_case_ids.add(outcome.tc_id)
                reasons.append(f"{outcome.tc_id} 的 recording outcome `{outcome.outcome}` 不在允许集合内。")

        proof_manifest: list[dict[str, Any]] = []
        bug_count = 0
        missing_case_ids: list[str] = []
        duplicate_case_ids: list[str] = []
        for tc_id in automatable_cases:
            case_outcomes = grouped.get(tc_id, [])
            if len(case_outcomes) != 1:
                if not case_outcomes:
                    missing_case_ids.append(tc_id)
                else:
                    duplicate_case_ids.append(tc_id)
                reasons.append(f"{tc_id} 需要且只能有 1 个唯一 recording outcome，当前为 {len(case_outcomes)} 个。")
                continue
            outcome = case_outcomes[0]
            if tc_id in invalid_outcome_case_ids:
                continue
            if outcome.outcome == PlaywrightRecordingOutcomeType.RECORDING_PASSED.value:
                if not outcome.proof_artifact_path or not Path(outcome.proof_artifact_path).exists():
                    reasons.append(f"{tc_id} 标记为 recording_passed，但 proof_artifact_path 不存在。")
                else:
                    trace_path = outcome.details.get("recording_trace_path", "")
                    proof_manifest.append(
                        {
                            "tc_id": tc_id,
                            "proof_artifact_path": outcome.proof_artifact_path,
                            "recording_trace_path": trace_path,
                        }
                    )
                    if not trace_path:
                        warnings.append(f"{tc_id} 缺少 recording_trace_path；阶段2A不阻塞，但阶段2B不能凭空生成脚本。")
                    elif not Path(trace_path).exists():
                        warnings.append(f"{tc_id} 提供了 recording_trace_path，但文件不存在: {trace_path}")
            elif outcome.outcome == PlaywrightRecordingOutcomeType.BUG_RECORDED.value:
                bug_count += 1
                bug_id = str(outcome.details.get("bug_id", ""))
                has_global_record = bool(
                    bug_report_text
                    and (
                        tc_id in bug_report_text
                        or (bug_id and bug_id in bug_report_text)
                    )
                )
                if not has_global_record:
                    reasons.append(f"{tc_id} 标记为 bug_recorded，但 playwright_bug_report.md 中缺少可追溯的 bug 记录。")

        unexpected_cases = sorted(set(grouped) - set(automatable_cases))
        if unexpected_cases:
            warnings.append(
                "以下 recording outcome 未在阶段1可自动化用例清单中出现，将保留但不计入强门禁: "
                + ", ".join(unexpected_cases)
            )

        proof_manifest_path = ""
        if not reasons:
            proof_manifest_target = self.store.artifact_path(state.run_id, "proof_artifacts_manifest.json")
            write_json(proof_manifest_target, proof_manifest)
            state.artifacts["proof_artifacts_manifest"] = str(proof_manifest_target)
            proof_manifest_path = str(proof_manifest_target)

        return PhaseGateResult(
            phase=Phase.PLAYWRIGHT_GENERATOR.value,
            ok=not reasons,
            summary=(
                f"阶段2A门禁通过，{len(automatable_cases)} 条可自动化用例已完成录制执行闭环，等待确认。"
                if not reasons
                else "阶段2A门禁未通过，存在未闭环或缺少 proof/bug 报告的可自动化用例。"
            ),
            blocking_reasons=reasons,
            warnings=warnings,
            details={
                "text_case_manifest": state.artifacts.get("text_case_manifest", ""),
                "playwright_recording_outcomes": outcomes_path,
                "playwright_recording_report": report_path,
                "playwright_bug_report": bug_report_path,
                "stage2a_execution_plan": execution_plan_path,
                "proof_artifacts_manifest": proof_manifest_path,
                "automatable_case_count": len(automatable_cases),
                "recording_passed_count": len(proof_manifest),
                "bug_recorded_count": bug_count,
                "missing_case_ids": missing_case_ids,
                "duplicate_case_ids": duplicate_case_ids,
                "unexpected_case_ids": unexpected_cases,
            },
        )

    def _validate_phase2_script_outputs(self, state: RunState) -> PhaseGateResult:
        manifest_payload = read_json(state.artifacts.get("text_case_manifest", ""), default={}) or {}
        reasons: list[str] = []
        warnings: list[str] = []
        if not manifest_payload:
            reasons.append("缺少 text_case_manifest.json，无法校验阶段2B脚本生成闭环。")

        outcomes_path = self._artifact_value(state, "playwright_case_outcomes", "case_outcomes")
        outcome_payload = read_json(outcomes_path, default=[]) or []
        recording_payload = read_json(
            self._artifact_value(state, "playwright_recording_outcomes", "recording_outcomes"),
            default=[],
        ) or []
        recording_outcomes = [PlaywrightRecordingOutcome(**item) for item in recording_payload] if recording_payload else []
        automatable_cases = [
            item.tc_id
            for item in recording_outcomes
            if item.outcome == PlaywrightRecordingOutcomeType.RECORDING_PASSED.value
        ]
        if not recording_payload:
            automatable_cases = [
                item["tc_id"]
                for item in manifest_payload.get("cases", [])
                if item.get("ui_automatable")
            ]
        if automatable_cases and not outcome_payload:
            reasons.append("缺少 playwright_case_outcomes.json，无法确认每条录制通过用例的脚本生成结局。")
        outcomes = [PlaywrightCaseOutcome(**item) for item in outcome_payload] if outcome_payload else []
        grouped: dict[str, list[PlaywrightCaseOutcome]] = {}
        for outcome in outcomes:
            grouped.setdefault(outcome.tc_id, []).append(outcome)

        generated_scripts: list[str] = []
        for tc_id in automatable_cases:
            case_outcomes = grouped.get(tc_id, [])
            if len(case_outcomes) != 1:
                reasons.append(f"{tc_id} 需要且只能有 1 个唯一 outcome，当前为 {len(case_outcomes)} 个。")
                continue
            outcome = case_outcomes[0]
            if outcome.outcome not in {item.value for item in PlaywrightOutcomeType}:
                reasons.append(f"{tc_id} 的 outcome `{outcome.outcome}` 不在允许集合内。")
                continue
            if outcome.outcome == PlaywrightOutcomeType.SCRIPT_GENERATED.value:
                if not outcome.script_path or not Path(outcome.script_path).exists():
                    reasons.append(f"{tc_id} 标记为 script_generated，但 script_path 不存在。")
                if not outcome.collect_only_passed or not outcome.pytest_passed:
                    reasons.append(f"{tc_id} 的自动化脚本缺少 collect-only/pytest 通过证明。")
                if outcome.script_path:
                    generated_scripts.append(outcome.script_path)
            elif outcome.outcome == PlaywrightOutcomeType.SCRIPT_BLOCKED.value:
                if not outcome.script_blocker_report_path or not Path(outcome.script_blocker_report_path).exists():
                    reasons.append(f"{tc_id} 标记为 script_blocked，但 script_blocker_report_path 不存在。")
                reasons.append(f"{tc_id} 脚本生成仍处于阻塞状态，必须批次内修复后才能进入影响分析。")
            elif outcome.outcome == PlaywrightOutcomeType.BUG_RECORDED.value:
                reasons.append(f"{tc_id} 已在阶段2A标记为 recording_passed，阶段2B不允许改为 bug_recorded。")
            elif outcome.outcome == PlaywrightOutcomeType.MANUAL_REVIEW.value:
                if not outcome.manual_review_reason:
                    reasons.append(f"{tc_id} 标记为 manual_review，但缺少 manual_review_reason。")
                reasons.append(f"{tc_id} 脚本生成进入 manual_review，必须处理当前脚本批次后才能进入影响分析。")

        unexpected_cases = sorted(set(grouped) - set(automatable_cases))
        if unexpected_cases:
            warnings.append(
                "以下阶段2B outcome 不属于阶段2A recording_passed 清单，将保留但不计入强门禁: "
                + ", ".join(unexpected_cases)
            )

        if not reasons:
            generated_manifest_path = self.store.artifact_path(state.run_id, "generated_scripts_manifest.json")
            write_json(generated_manifest_path, sorted(set(generated_scripts)))
            state.artifacts["generated_scripts_manifest"] = str(generated_manifest_path)

        return PhaseGateResult(
            phase=Phase.PLAYWRIGHT_GENERATOR.value,
            ok=not reasons,
            summary=(
                f"阶段2B门禁通过，{len(automatable_cases)} 条录制通过用例已生成脚本并自测闭环。"
                if not reasons
                else "阶段2B门禁未通过，存在未生成脚本、未通过自测或进入人工处理的用例。"
            ),
            blocking_reasons=reasons,
            warnings=warnings,
            details={
                "text_case_manifest": state.artifacts.get("text_case_manifest", ""),
                "playwright_case_outcomes": outcomes_path,
                "automatable_case_count": len(automatable_cases),
                "generated_script_count": len(set(generated_scripts)),
            },
        )

    def _validate_phase3_outputs(self, state: RunState) -> PhaseGateResult:
        reasons: list[str] = []
        dry_run_path = self._artifact_value(state, "ok_ui_dry_run_preview")
        report_path = self._artifact_value(state, "ok_ui_execution_report", "ok_ui_report")
        recommendation_path = self._artifact_value(state, "release_recommendation", "launch_recommendation")
        if not read_text(dry_run_path):
            reasons.append("缺少 ok_ui_dry_run_preview，或 dry-run 预览内容为空。")
        if not read_text(report_path):
            reasons.append("缺少 ok_ui_execution_report/ok_ui_report，或真实回归报告内容为空。")
        if not read_text(recommendation_path):
            reasons.append("缺少 release_recommendation/launch_recommendation，或上线建议为空。")

        return PhaseGateResult(
            phase=Phase.OK_UI_REGRESSION.value,
            ok=not reasons,
            summary=(
                "阶段3门禁通过，dry-run、真实回归与上线建议均已落盘。"
                if not reasons
                else "阶段3门禁未通过，缺少 dry-run / 真实回归 / 上线建议产物。"
            ),
            blocking_reasons=reasons,
            details={
                "ok_ui_dry_run_preview": dry_run_path,
                "ok_ui_execution_report": report_path,
                "release_recommendation": recommendation_path,
            },
        )

    def _validate_knowledge_base_outputs(self, state: RunState) -> PhaseGateResult:
        reasons: list[str] = []
        preview_path = self._artifact_value(state, "knowledge_base_update_preview")
        result_path = self._artifact_value(state, "knowledge_base_update_result")
        if not read_text(preview_path):
            reasons.append("缺少 knowledge_base_update_preview，或预览内容为空。")
        if not read_text(result_path) and not read_json(result_path, default=None):
            reasons.append("缺少 knowledge_base_update_result，或写入结果为空。")

        return PhaseGateResult(
            phase=Phase.KNOWLEDGE_BASE_UPDATE.value,
            ok=not reasons,
            summary=(
                "Knowledge base 更新门禁通过，预览与写入结果均已确认。"
                if not reasons
                else "Knowledge base 更新门禁未通过，缺少预览或写入结果。"
            ),
            blocking_reasons=reasons,
            details={
                "knowledge_base_update_context": state.artifacts.get("knowledge_base_update_context", ""),
                "knowledge_base_update_preview": preview_path,
                "knowledge_base_update_result": result_path,
            },
        )

    def _store_gate_result(self, state: RunState, artifact_key: str, gate: PhaseGateResult) -> None:
        path = self.store.artifact_path(state.run_id, f"{artifact_key}.json")
        write_json(path, to_data(gate))
        state.artifacts[artifact_key] = str(path)

    def _block_with_gate(self, state: RunState, phase: Phase, gate: PhaseGateResult) -> RunState:
        self._mark(state, phase, PhaseStatus.BLOCKED)
        state.status = RunStatus.BLOCKED.value
        state.blocked_reason = gate.summary
        if gate.blocking_reasons:
            state.blocked_reason += " " + " ".join(gate.blocking_reasons)
        return state

    def _artifact_value(self, state: RunState, *keys: str) -> str:
        for key in keys:
            value = state.artifacts.get(key, "")
            if value:
                return value
        return ""

    def _playwright_progress(self, state: RunState) -> dict[str, Any]:
        return read_json(state.artifacts.get(PLAYWRIGHT_PROGRESS_KEY, ""), default={}) or {}

    def _write_playwright_progress(self, state: RunState, **updates: Any) -> dict[str, Any]:
        progress = self._playwright_progress(state)
        progress.update({key: value for key, value in updates.items() if value is not None})
        path = Path(state.artifacts.get(PLAYWRIGHT_PROGRESS_KEY, "")) if state.artifacts.get(PLAYWRIGHT_PROGRESS_KEY) else None
        if not path:
            path = self.store.artifact_path(state.run_id, f"{PLAYWRIGHT_PROGRESS_KEY}.json")
        write_json(path, progress)
        state.artifacts[PLAYWRIGHT_PROGRESS_KEY] = str(path)
        return progress

    def _append_confirmation(self, state: RunState, record: UserConfirmationRecord) -> None:
        confirmation_path = self.store.artifact_path(state.run_id, "user_confirmations.json")
        existing = read_json(confirmation_path, default=[]) or []
        existing.append(to_data(record))
        write_json(confirmation_path, existing)
        state.artifacts["user_confirmations"] = str(confirmation_path)

    def _parse_environment_config(self, text: str) -> dict[str, str]:
        match = re.search(r"##\s*测试环境配置.*?(?=\n##\s+|\Z)", text, flags=re.S)
        if not match:
            return {}
        environment: dict[str, str] = {}
        for line in match.group(0).splitlines():
            if not line.strip().startswith("|"):
                continue
            parts = [part.strip() for part in line.strip().strip("|").split("|")]
            if len(parts) < 2:
                continue
            if parts[0] in {"字段", "---", "------"} or parts[0].startswith("---"):
                continue
            environment[parts[0]] = parts[1]
        return environment

    def _parse_text_case_entries(self, text: str, source_doc: str) -> list[TextCaseManifestEntry]:
        pattern = re.compile(r"^###\s*(TC\d+)\s*:\s*(.+)$", flags=re.M)
        matches = list(pattern.finditer(text))
        entries: list[TextCaseManifestEntry] = []
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            block = text[start:end]
            entries.append(
                TextCaseManifestEntry(
                    tc_id=match.group(1).strip(),
                    title=match.group(2).strip(),
                    priority=self._extract_case_attribute(block, "优先级"),
                    test_type=self._extract_case_attribute(block, "测试类型"),
                    ui_automatable=self._extract_ui_automatable(block),
                    ui_automation_label=self._extract_case_attribute(block, "UI自动化"),
                    preconditions=self._extract_case_section(block, "前置条件"),
                    steps=self._extract_case_section(block, "执行步骤"),
                    expected_results=self._extract_case_section(block, "预期结果"),
                    source_doc=source_doc,
                )
            )
        return entries

    def _extract_case_attribute(self, block: str, name: str) -> str:
        match = re.search(rf"-\s*\*\*{re.escape(name)}\*\*:\s*(.+)", block)
        return match.group(1).strip() if match else ""

    def _extract_ui_automatable(self, block: str) -> bool:
        value = self._extract_case_attribute(block, "UI自动化")
        if not value:
            return False
        return "✅" in value or ("可自动化" in value and "❌" not in value)

    def _extract_case_section(self, block: str, section_name: str) -> list[str]:
        pattern = re.compile(
            rf"####\s*.*?{re.escape(section_name)}\s*(.*?)(?=\n####\s+|\Z)",
            flags=re.S,
        )
        match = pattern.search(block)
        if not match:
            return []
        lines: list[str] = []
        for line in match.group(1).splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            stripped = re.sub(r"^\d+\.\s*", "", stripped)
            stripped = re.sub(r"^-\s*", "", stripped)
            if stripped:
                lines.append(stripped)
        return lines

    def _mentions_kb_miss(self, text: str) -> bool:
        return any(token in text for token in ("规则库未命中", "知识库未命中", "未命中业务规则库"))

    def _extract_document_section_lines(self, text: str, section_name: str) -> list[str]:
        pattern = re.compile(
            rf"^#{{1,6}}\s*.*?{re.escape(section_name)}.*?\n(.*?)(?=^#{{1,6}}\s+|\Z)",
            flags=re.S | re.M,
        )
        match = pattern.search(text or "")
        if not match:
            return []
        lines: list[str] = []
        for line in match.group(1).splitlines():
            stripped = line.strip()
            if not stripped or stripped in {"---"}:
                continue
            stripped = re.sub(r"^\d+\.\s*", "", stripped)
            stripped = re.sub(r"^-\s*", "", stripped)
            if stripped:
                lines.append(stripped)
        return lines

    def _is_safe_relative_fragment(self, value: str) -> bool:
        if not value or Path(value).is_absolute():
            return False
        return ".." not in Path(value).parts

    def _rule_route_values(self, packet: dict[str, Any]) -> list[str]:
        module = normalize_text((packet.get("candidate_modules") or [""])[0]).replace(" ", "")
        route_map = self.config.knowledge_base_routing.get("rule_library_routes", {})
        route = route_map.get(module, [])
        if isinstance(route, str):
            return [route]
        if isinstance(route, list):
            return [str(item) for item in route if str(item).strip()]
        if isinstance(route, dict):
            for key in ("routes", "paths", "rules"):
                value = route.get(key)
                if isinstance(value, str):
                    return [value]
                if isinstance(value, list):
                    return [str(item) for item in value if str(item).strip()]
        return []

    def _knowledge_base_rule_paths(self, packet: dict[str, Any]) -> tuple[list[Path], list[str]]:
        knowledge_base_root = Path(self.config.skills.get("paths", {}).get("knowledge_base_root", ""))
        rule_root = knowledge_base_root / "业务规则库"
        paths: list[Path] = []
        errors: list[str] = []
        for route in self._rule_route_values(packet):
            if not self._is_safe_relative_fragment(route):
                errors.append(f"业务规则库 route 必须是相对路径片段，不能是绝对路径或包含 `..`: {route}")
                continue
            target = rule_root / route
            if not target.exists():
                errors.append(f"业务规则库 route 不存在: {target}")
                continue
            paths.append(target)
        return paths, errors

    def _executable_precondition_issue(self, case: TextCaseManifestEntry) -> str:
        text = " ".join(case.preconditions)
        normalized = normalize_text(text)
        checks = {
            "角色/登录态": any(
                token in text
                for token in ("访客", "游客", "未登录", "已登录", "登录态", "角色", "买家", "卖家", "buyer", "seller")
            ),
            "入口URL或导航路径": bool(re.search(r"https?://|/\w|URL|路径|打开|访问|进入|导航|首页|Browse", text, flags=re.I)),
            "账号或测试数据": any(
                token in text
                for token in ("账号", "测试数据", "无需登录", "无", "邮箱", "手机", "商品", "车辆", "帖子", "数据", "ID", "@")
            ),
            "准备动作": any(token in text for token in ("打开", "访问", "进入", "点击", "登录", "清空", "选择", "创建", "准备")),
            "就绪验证点": any(token in text for token in ("确认", "可见", "显示", "加载完成", "存在", "标题", "URL", "按钮", "输入框")),
        }
        missing = [name for name, ok in checks.items() if not ok]
        vague_tokens = ("系统准备好", "数据准备好", "已准备好", "账号正常", "页面已加载", "已进入页面", "已进入")
        vague = any(normalize_text(token) in normalized for token in vague_tokens)
        if vague and missing:
            return f"包含含糊表达，且缺少 {', '.join(missing)}。"
        if missing:
            return f"缺少 {', '.join(missing)}。"
        return ""

    def _knowledge_base_bucket(self, packet: dict[str, Any]) -> str:
        module = normalize_text((packet.get("candidate_modules") or [""])[0]).replace(" ", "")
        bucket_map = self.config.knowledge_base_routing.get("text_case_buckets", {})
        route = bucket_map.get(module, {})
        if isinstance(route, str):
            return route
        return route.get("bucket", "")

    def _knowledge_base_draft_path(self, packet: dict[str, Any], textcases_path: str, bucket: str) -> Path:
        if not self._is_safe_relative_fragment(bucket):
            raise ValueError(f"知识库文本用例 bucket 必须是相对路径片段: {bucket}")
        knowledge_base_root = Path(self.config.skills.get("paths", {}).get("knowledge_base_root", ""))
        source_name = Path(textcases_path).name
        generic_names = {"testcases.md", "textcases.md", "cases.md"}
        if not source_name or source_name in generic_names:
            source_name = self._generated_text_case_filename(packet)
        return knowledge_base_root / "文本用例" / bucket / source_name

    def _generated_text_case_filename(self, packet: dict[str, Any]) -> str:
        site = (packet.get("site", "") or "site").upper()
        module = (packet.get("candidate_modules") or ["module"])[0] or "module"
        feature = packet.get("feature_name", "") or "测试用例"
        date_token = str(packet.get("created_at", ""))[:10].replace("-", "") or "draft"
        safe_feature = re.sub(r"[\\/:*?\"<>|]+", "-", feature)
        safe_module = re.sub(r"[\\/:*?\"<>|]+", "-", module)
        return f"OK-{site}-{safe_module}-{safe_feature}-测试用例-{date_token}.md"

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
        current_round_index = int(current_gate.get("round_index", 0))
        playwright_tasks = self._legacy_tasks_needing_playwright(tasks, mutate=True)
        if playwright_tasks:
            self._persist_legacy_tasks_and_gate(state, tasks, current_round_index)
            self._write_legacy_rerecord_request(state, playwright_tasks)
            self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.BLOCKED)
            state.status = RunStatus.BLOCKED.value
            state.blocked_reason = (
                f"旧脚本更新有 {len(playwright_tasks)} 个任务需要 playwright-test-generator "
                "重新录制候选脚本，不能由 QA Agent 盲猜修改"
            )
            return state

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
            refresh_result = self.legacy_update_executor.refresh_catalog_after_script_changes(outcome.tasks)
            if refresh_result.get("needed"):
                refresh_path = self.store.artifact_path(
                    state.run_id,
                    f"catalog_refresh_after_script_changes_round_{round_index:02d}.json",
                )
                write_json(refresh_path, refresh_result)
                state.artifacts[f"catalog_refresh_after_script_changes_round_{round_index:02d}"] = str(refresh_path)
                if refresh_result.get("promotion_task_ids"):
                    state.artifacts[f"catalog_refresh_after_promotion_round_{round_index:02d}"] = str(refresh_path)
                if not refresh_result.get("ok"):
                    self._mark(state, Phase.LEGACY_UPDATE, PhaseStatus.BLOCKED)
                    state.status = RunStatus.BLOCKED.value
                    state.blocked_reason = (
                        "脚本更新已合并，但 catalog refresh/audit 失败；"
                        "请修复标识或 catalog 后再继续"
                    )
                    return state
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

    def _legacy_playwright_request_active(self, state: RunState) -> bool:
        if not state.artifacts.get("legacy_rerecord_instruction"):
            return False
        return bool(self._legacy_tasks_needing_playwright(self._load_legacy_tasks(state)))

    def _legacy_tasks_needing_playwright(
        self,
        tasks: list[LegacyUpdateTask],
        *,
        mutate: bool = False,
    ) -> list[LegacyUpdateTask]:
        needs: list[LegacyUpdateTask] = []
        for task in tasks:
            if task.status in (LegacyUpdateTaskStatus.COMPLETED.value, LegacyUpdateTaskStatus.MANUAL_REVIEW.value):
                continue
            force_regen = bool(task.details.get("needs_playwright_rerecord")) and (
                task.recommended_action in PLAYWRIGHT_REGEN_ACTIONS
            )
            if self._task_has_replacement_candidate(task) and not force_regen:
                continue

            needs_playwright = task.recommended_action in PLAYWRIGHT_REGEN_ACTIONS
            missing_patch = task.recommended_action in PATCH_ACTIONS and not task.details.get("replacements")
            if not (needs_playwright or missing_patch):
                continue

            if mutate:
                if missing_patch:
                    task.details.setdefault("original_recommended_action", task.recommended_action)
                    task.recommended_action = "re-record"
                task.details["needs_playwright_rerecord"] = True
                task.details.setdefault(
                    "rerecord_reason",
                    "缺少可自动应用的候选 patch，需要 playwright-test-generator 重新录制",
                )
                if task.status == LegacyUpdateTaskStatus.RUNNING.value:
                    task.status = LegacyUpdateTaskStatus.RETRY.value
            needs.append(task)
        return needs

    def _task_has_replacement_candidate(self, task: LegacyUpdateTask) -> bool:
        replacement_text = task.details.get("replacement_text")
        if replacement_text:
            return True
        replacement_source = task.details.get("replacement_source_path")
        if replacement_source and Path(replacement_source).exists():
            return True
        return False

    def _current_legacy_round_index(self, state: RunState) -> int:
        current_gate = read_json(state.artifacts.get("legacy_update_gate", ""), default={}) or {}
        return int(current_gate.get("round_index", 0))

    def _persist_legacy_tasks_and_gate(
        self,
        state: RunState,
        tasks: list[LegacyUpdateTask],
        round_index: int,
    ) -> None:
        tasks_path = self.store.artifact_path(state.run_id, "legacy_update_tasks.json")
        gate_path = self.store.artifact_path(state.run_id, "legacy_update_gate.json")
        write_json(tasks_path, [asdict(task) for task in tasks])
        write_json(gate_path, asdict(self._build_gate(tasks, round_index=round_index)))
        state.artifacts["legacy_update_tasks"] = str(tasks_path)
        state.artifacts["legacy_update_gate"] = str(gate_path)
        state.artifacts["regression_selector_plan"] = str(self._refresh_selector_plan(state, tasks))

    def _write_legacy_rerecord_request(
        self,
        state: RunState,
        tasks: list[LegacyUpdateTask],
    ) -> None:
        packet = self._requirement_packet(state)
        request_path = self.store.artifact_path(state.run_id, "legacy_rerecord_request.json")
        instruction_path = self.store.artifact_path(state.run_id, "legacy_rerecord_instruction.md")
        request = {
            "run_id": state.run_id,
            "phase": Phase.LEGACY_UPDATE.value,
            "skill": SKILL_PATHS[Phase.PLAYWRIGHT_GENERATOR],
            "module": (packet.get("candidate_modules") or [""])[0],
            "site": packet.get("site", ""),
            "feature_name": packet.get("feature_name", ""),
            "change_description": packet.get("change_description", ""),
            "tasks": [self._legacy_rerecord_task_payload(task) for task in tasks],
            "output_manifest": {
                "artifact_key": "legacy_update_candidate_manifest",
                "schema": [
                    {
                        "task_id": "<legacy task id>",
                        "replacement_source_path": "<generated candidate .py path>",
                        "proof_artifact_path": "<playwright-test-generator proof/report path>",
                        "recommended_action": "re-record",
                    }
                ],
            },
        }
        write_json(request_path, request)
        write_text(instruction_path, self._render_legacy_rerecord_instruction(request))
        state.artifacts["legacy_rerecord_request"] = str(request_path)
        state.artifacts["legacy_rerecord_instruction"] = str(instruction_path)

    def _legacy_rerecord_task_payload(self, task: LegacyUpdateTask) -> dict[str, Any]:
        return {
            "task_id": task.task_id,
            "target_script": task.target_script,
            "target_case_id": task.target_case_id,
            "target_nodeid": task.target_nodeid,
            "recommended_action": task.recommended_action,
            "reason": task.reason,
            "module": task.details.get("module", ""),
            "site": task.details.get("site", ""),
            "rerecord_reason": task.details.get("rerecord_reason", ""),
            "matched_nodeids": list(task.details.get("matched_nodeids", []) or []),
            "executed_nodeids": list(task.details.get("executed_nodeids", []) or []),
        }

    def _render_legacy_rerecord_instruction(self, request: dict[str, Any]) -> str:
        lines = [
            "# 旧脚本重录子任务",
            "",
            f"请读取 `{request['skill']}`，只针对下面列出的旧脚本更新任务生成候选替换版本。",
            "",
            "## 关键规则",
            "- 不允许直接修改正式回归仓库中的旧脚本。",
            "- 候选脚本必须先生成到 run 目录或临时产物目录。",
            "- 每个任务都必须有 proof artifact，证明已按 playwright-test-generator 流程录制/生成/自测。",
            "- 完成后输出 `legacy_update_candidate_manifest.json`，再用 resume command 回到 QA Agent。",
            "",
            "## 输出 manifest 格式",
            "```json",
            "[",
            "  {",
            '    "task_id": "legacy-xxxx",',
            '    "replacement_source_path": "/path/to/candidate.py",',
            '    "proof_artifact_path": "/path/to/proof.md",',
            '    "recommended_action": "re-record"',
            "  }",
            "]",
            "```",
            "",
            "## 任务列表",
        ]
        for task in request.get("tasks", []):
            lines.extend(
                [
                    f"### {task.get('task_id', '')}",
                    f"- target_script: {task.get('target_script', '')}",
                    f"- target_case_id: {task.get('target_case_id', '')}",
                    f"- target_nodeid: {task.get('target_nodeid', '')}",
                    f"- module/site: {task.get('module', '')}/{task.get('site', '')}",
                    f"- recommended_action: {task.get('recommended_action', '')}",
                    f"- reason: {task.get('reason', '')}",
                    f"- rerecord_reason: {task.get('rerecord_reason', '')}",
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"

    def _apply_legacy_candidate_manifest(
        self,
        tasks: list[LegacyUpdateTask],
        entries: list[Any],
        manifest_path: str,
    ) -> list[str]:
        errors: list[str] = []
        for raw_entry in entries:
            if not isinstance(raw_entry, dict):
                errors.append("manifest entry 必须是 object")
                continue
            task = self._find_legacy_task_for_candidate(tasks, raw_entry)
            if not task:
                errors.append(f"未找到匹配任务: {raw_entry.get('task_id') or raw_entry.get('target_nodeid')}")
                continue

            replacement_source = raw_entry.get("replacement_source_path") or raw_entry.get("candidate_path") or ""
            replacement_text = raw_entry.get("replacement_text", "")
            proof_artifact = raw_entry.get("proof_artifact_path") or raw_entry.get("proof_path") or ""
            if not replacement_source and not replacement_text:
                errors.append(f"{task.task_id} 缺少 replacement_source_path/replacement_text")
                continue
            if replacement_source and not Path(str(replacement_source)).exists():
                errors.append(f"{task.task_id} replacement_source_path 不存在: {replacement_source}")
                continue
            if not proof_artifact or not Path(str(proof_artifact)).exists():
                errors.append(f"{task.task_id} 缺少有效 proof_artifact_path")
                continue

            if raw_entry.get("recommended_action") in PLAYWRIGHT_REGEN_ACTIONS:
                task.recommended_action = str(raw_entry["recommended_action"])
            elif task.recommended_action not in PLAYWRIGHT_REGEN_ACTIONS:
                task.recommended_action = "re-record"
            task.details["replacement_source_path"] = str(replacement_source)
            if replacement_text:
                task.details["replacement_text"] = str(replacement_text)
            task.details["proof_artifact_path"] = str(proof_artifact)
            task.details["needs_playwright_rerecord"] = False
            task.details["legacy_update_candidate_manifest"] = manifest_path
            task.details["playwright_rerecord_completed_at"] = utc_now_iso()
            task.status = LegacyUpdateTaskStatus.RETRY.value
        return errors

    def _find_legacy_task_for_candidate(
        self,
        tasks: list[LegacyUpdateTask],
        entry: dict[str, Any],
    ) -> LegacyUpdateTask | None:
        for key in ("task_id", "target_nodeid", "target_case_id", "target_script"):
            value = entry.get(key)
            if not value:
                continue
            for task in tasks:
                if getattr(task, key, "") == value:
                    return task
        return None

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
            "playwright_recording_report",
            "playwright_bug_report",
            "playwright_case_outcomes",
            "impact_candidates",
            "change_attribution_report",
            "legacy_update_gate",
            "regression_selector_plan",
        ]:
            if state.artifacts.get(key):
                lines.append(f"- {key}: {state.artifacts[key]}")
        run_state_path = self.store.run_dir(state.run_id) / "run_state.json"
        lines.extend(["", "## 完整产物清单"])
        lines.append(f"- 完整 artifact 清单见: {run_state_path}")
        lines.extend(["", "## 阶段状态"])
        for phase_name, status in state.phase_statuses.items():
            lines.append(f"- {phase_name}: {status}")
        if state.phase_timings:
            lines.extend(["", "## 阶段耗时"])
            for phase_name, timing in state.phase_timings.items():
                if not isinstance(timing, dict):
                    continue
                lines.append(
                    f"- {phase_name}: active={timing.get('active_seconds', 0)}s, "
                    f"blocked={timing.get('blocked_seconds', 0)}s, "
                    f"wall={timing.get('wall_seconds', 0)}s, "
                    f"status={timing.get('last_status', '')}"
                )

        path = self.store.artifact_path(state.run_id, "final_report.md")
        write_text(path, "\n".join(lines) + "\n")
        state.artifacts["final_report"] = str(path)
        context_path = self.store.artifact_path(state.run_id, "knowledge_base_update_context.md")
        write_text(context_path, self._render_knowledge_base_update_context(state))
        state.artifacts["knowledge_base_update_context"] = str(context_path)
        self._mark(state, Phase.FINAL_REPORT, PhaseStatus.COMPLETED)
        state.status = RunStatus.RUNNING.value
        state.blocked_reason = ""
        return state

    def _write_memory_candidates(self, state: RunState) -> Path | None:
        final_report = state.artifacts.get("final_report", "")
        if not final_report:
            return None
        content = (
            f"QA Agent run {state.run_id} 已完成最终报告。"
            f"变更模式：{state.change_mode}；"
            f"最终报告：{final_report}。"
            "如本次过程包含可复用的用户纠错、流程决策或踩坑经验，请在任务结束时批量确认后写入正式记忆。"
        )
        candidate = build_candidate_from_text(
            content,
            memory_type="summary",
            scope=["qa_agent", "run_summary"],
            tags=["qa-agent", "summary"],
            priority="low",
            risk="low",
            candidate_reason="QA Agent 最终报告阶段自动生成的候选摘要",
            source_kind="run_summary",
            run_id=state.run_id,
        )
        memory_root = self.config.agent_memory_root
        try:
            stored = MemoryStore(memory_root).append_candidate(candidate)
            payload = [memory_to_data(stored)]
        except Exception as exc:
            payload = [
                {
                    "candidate": memory_to_data(candidate),
                    "not_stored_reason": f"{type(exc).__name__}: {exc}",
                }
            ]
            state.notes.append(f"memory candidate skipped: {type(exc).__name__}: {exc}")
        path = self.store.artifact_path(state.run_id, "memory_candidates.json")
        write_json(path, payload)
        return path

    def _build_instruction(self, state: RunState, phase: Phase) -> str:
        skill_path = SKILL_PATHS[phase]
        packet = self._requirement_packet(state)

        if phase == Phase.SENIOR_QA_BRAIN:
            rule_paths, rule_route_errors = self._knowledge_base_rule_paths(packet)
            knowledge_base_root = Path(self.config.skills.get("paths", {}).get("knowledge_base_root", ""))
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
                    f"- 业务规则库根目录: {knowledge_base_root / '业务规则库'}",
                    "",
                    "## 业务规则库读取要求",
                ]
            )
            if rule_paths:
                parts.append("- 必须先读取以下业务规则库路径，再生成分析报告和文本用例：")
                parts.extend(f"  - {path}" for path in rule_paths)
            else:
                parts.append("- 规则库未命中：当前 module 未配置可用业务规则库路径。")
                parts.append("- 不要编造业务规则；请在分析报告中写明“规则库未命中”，并把缺失规则列为待确认问题。")
            if rule_route_errors:
                parts.append("- 规则库路由配置异常：")
                parts.extend(f"  - {item}" for item in rule_route_errors)
            parts.extend(
                [
                    "",
                    "## 要求",
                    "- 按 SKILL.md 流程逐步执行，不要跳步",
                    "- 分析报告必须包含“知识库依据”章节，列出实际读取的业务规则库文件路径；若规则库未命中，必须明确写“规则库未命中”或“知识库未命中”",
                    "- 生成分析报告后等待用户确认",
                    "- 确认后生成 Markdown 测试用例",
                    "- complete 当前阶段时必须回传 analysis_report 和 textcases 两个产物路径",
                    "- 文本用例必须包含测试环境配置表格、TC编号、前置条件、步骤、预期、优先级、测试类型、UI自动化",
                    "- 文本用例必须包含“业务属性”和“测试范围”",
                    "- 每条 UI自动化=✅ 的用例，前置条件必须写成可执行准备：角色/登录态、入口 URL 或导航路径、账号/测试数据、准备动作、就绪验证点",
                    "- 不要只写“系统准备好”“已进入页面”“数据已准备好”“账号正常”等含糊前置条件",
                ]
            )
            self._append_memory_instruction(parts, state)
            return "\n".join(parts)

        if phase == Phase.PLAYWRIGHT_GENERATOR:
            progress = self._playwright_progress(state)
            if progress.get("stage") == PLAYWRIGHT_STAGE_SCRIPT_PENDING:
                recording_outcomes = state.artifacts.get("playwright_recording_outcomes", "")
                proof_manifest = state.artifacts.get("proof_artifacts_manifest", "")
                parts = [
                    f"# 阶段: {phase.value} 阶段2B - Python脚本生成与自测",
                    "",
                    f"请读取 `{skill_path}`，只执行阶段2B脚本生成、自测和批次内调试闭环。",
                    "",
                    "## 输入",
                    f"- 测试用例文档: {state.artifacts.get('kb_text_case_draft_path') or state.artifacts.get('textcases', '')}",
                    f"- 阶段1清单: {state.artifacts.get('text_case_manifest', '')}",
                    f"- 阶段2A录制结局: {recording_outcomes}",
                    f"- proof manifest: {proof_manifest}",
                    f"- 阶段2A录制报告: {state.artifacts.get('playwright_recording_report', '')}",
                    "",
                    "## 要求",
                    "- 只处理阶段2A outcome 为 recording_passed 的用例",
                    "- 有 bug_recorded 的用例不生成脚本",
                    "- 先从 proof/recording_trace 生成最小 replay 脚本，验证 JS 到 Python 转换",
                    "- replay 通过后再整理成 OK UI 规范脚本，补齐 _CONFIG、pytest.mark、allure、fixture/POM 复用",
                    "- 每批最多 5 条，当前批次 collect-only 和 pytest 都通过后再进入下一批",
                    "- 3 轮仍失败时输出 script_blocker_report.md，并在 playwright_case_outcomes.json 中标记 script_blocked；QA Agent 会阻塞在当前阶段",
                    "- complete 当前阶段时必须回传 playwright_case_outcomes.json",
                    "- 每条 recording_passed 用例必须最终为 script_generated，并附带 script_path、collect_only_passed=true、pytest_passed=true",
                ]
                self._append_memory_instruction(parts, state)
                return "\n".join(parts)

            parts = [
                f"# 阶段: {phase.value} 阶段2A - 录制执行与验证",
                "",
                f"请读取 `{skill_path}`，先执行阶段2A录制执行与验证，不要在本轮生成 Python 脚本。",
                "",
                "## 输入",
                f"- 测试用例文档: {state.artifacts.get('kb_text_case_draft_path') or state.artifacts.get('textcases', '')}",
                f"- 阶段1清单: {state.artifacts.get('text_case_manifest', '')}",
                "",
                "## 要求",
                "- 按 SKILL.md 的阶段2A流程执行真实浏览器录制和每步预期验证",
                "- 每个阶段开始前先读取 SKILL.md 指定的 references 文件",
                "- 每批最多 5 条用例",
                "- 本轮只生成 proof、截图、录制执行报告和 bug list，不生成 Python 脚本",
                "- complete 当前阶段时必须回传 playwright_recording_outcomes.json、playwright_recording_report.md 和 playwright_bug_report.md",
                "- 建议额外回传 stage2a_execution_plan=<path>；缺失只记 warning，但执行计划仍应生成用于追溯",
                "- 对每条 UI自动化=✅ 的用例，必须给出唯一 recording outcome: recording_passed / bug_recorded",
                "- 阶段2A不允许 manual_review；实际结果不符合预期、页面缺失、流程阻塞、配置异常、接口异常都记录为 bug_recorded",
                "- 报告里可以展示失败/阻塞；JSON 中统一用 bug_recorded，并可用 details.progress_status=failed|blocked 区分",
                "- recording_passed 必须附带 proof_artifact_path；bug_recorded 必须能在 bug report 中通过 TC编号或 BUG编号追溯",
                "- playwright_bug_report.md 必须始终生成；没有 bug 时写明本轮未发现 bug",
                "- recording_trace_path 缺失不会阻塞阶段2A，但阶段2B不能凭空生成脚本",
            ]
            self._append_memory_instruction(parts, state)
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
            parts.extend(
                [
                    "",
                    "## 要求",
                    "- 优先消费 regression_selector_plan.json",
                    "- 若 selector 计划包含 execution_tasks，请按列表顺序逐个子任务 dry-run，汇总预览后等待确认，再按同一顺序真实执行",
                    "- execution_tasks 中 selected_count=0 的子任务只写入 dry-run 预览和 warning，不进入真实执行",
                    "- 若 selector 计划中的 catalog_status.stale=true，请先刷新 catalog 并审计标识，再继续 dry-run",
                    "- 先 dry-run 预览，等用户确认后再真实执行",
                    "- 真实执行默认由 OK UI runner 对 failed/error 用例自动重跑 1 次；报告需展示初跑失败与重跑恢复统计",
                    "- 若 selector_plan 缺少必要信息，再退回 module-map.md 做补充",
                    "- complete 当前阶段时必须回传 dry-run 预览、真实回归报告、上线建议",
                ]
            )
            self._append_memory_instruction(parts, state)
            return "\n".join(parts)

        if phase == Phase.KNOWLEDGE_BASE_UPDATE:
            kb_context = state.artifacts.get("knowledge_base_update_context", "")
            kb_draft = state.artifacts.get("kb_text_case_draft_path", "")
            parts = [
                f"# 阶段: {phase.value}",
                "",
                f"请读取 `{skill_path}` 并按其“预览 -> 确认 -> 写入”流程执行。",
                "",
                "## 输入",
                f"- 更新上下文: {kb_context}",
                f"- 最终报告: {state.artifacts.get('final_report', '')}",
                f"- 影响分析: {state.artifacts.get('impact_candidates', '')}",
                f"- 归因报告: {state.artifacts.get('change_attribution_report', '')}",
                f"- 回归 selector 计划: {state.artifacts.get('regression_selector_plan', '')}",
                f"- 文本用例主输入: {kb_draft}",
                "",
                "## 要求",
                "- 若存在 kb_text_case_draft_path，必须优先读取并回写该路径，不要另起第二份文本用例文档",
                "- 先输出 knowledge base 更新预览，再等待确认",
                "- 写入完成后回传 preview/result 产物路径",
                "- 若 vendored skill 缺失或预览失败，不要跳过本阶段",
                "- complete 当前阶段时必须回传 knowledge_base_update_preview 和 knowledge_base_update_result",
            ]
            self._append_memory_instruction(parts, state)
            return "\n".join(parts)

        return f"# 阶段: {phase.value}\n\n请读取 `{skill_path}` 并执行。"

    def _append_memory_instruction(self, parts: list[str], state: RunState) -> None:
        memory_context = state.artifacts.get("memory_context", "")
        if not memory_context:
            return
        parts.extend(
            [
                "",
                "## 相关记忆提醒",
                f"- 先读取 memory_context: {memory_context}",
                "- memory 只作为协作提醒，不能绕过本阶段 SKILL.md、门禁或人工确认。",
            ]
        )

    def _mark(self, state: RunState, phase: Phase, status: PhaseStatus) -> None:
        state.current_phase = phase.value
        state.phase_statuses[phase.value] = status.value
        if status == PhaseStatus.RUNNING:
            state.status = RunStatus.RUNNING.value
            self._phase_started(state, phase)
        elif status == PhaseStatus.BLOCKED:
            self._phase_blocked(state, phase)
        elif status in (PhaseStatus.COMPLETED, PhaseStatus.SKIPPED):
            self._phase_completed(state, phase)
        elif status == PhaseStatus.ERROR:
            self._phase_error(state, phase)
        state.touch()

    def _phase_timing(self, state: RunState, phase: Phase) -> dict[str, Any]:
        if not isinstance(state.phase_timings, dict):
            state.phase_timings = {}
        timing = state.phase_timings.setdefault(phase.value, {})
        if not isinstance(timing, dict):
            timing = {}
            state.phase_timings[phase.value] = timing
        timing.setdefault("active_seconds", 0.0)
        timing.setdefault("blocked_seconds", 0.0)
        timing.setdefault("wall_seconds", 0.0)
        timing.setdefault("attempts_count", 0)
        timing.setdefault("events", [])
        return timing

    def _phase_started(self, state: RunState, phase: Phase) -> None:
        now = utc_now_iso()
        timing = self._phase_timing(state, phase)
        if not timing.get("started_at"):
            timing["started_at"] = now
        if timing.get("blocked_at"):
            timing["blocked_seconds"] = round(
                float(timing.get("blocked_seconds", 0.0)) + self._seconds_between(timing["blocked_at"], now),
                3,
            )
            timing["blocked_at"] = ""
        if timing.get("last_status") != "running":
            timing["attempts_count"] = int(timing.get("attempts_count", 0)) + 1
        timing["active_started_at"] = now
        timing["last_status"] = "running"
        self._append_timing_event(timing, "running", now)
        self._refresh_wall_seconds(timing, now)

    def _phase_resumed(self, state: RunState, phase: Phase) -> None:
        timing = self._phase_timing(state, phase)
        if timing.get("last_status") == "blocked" or timing.get("blocked_at"):
            self._phase_started(state, phase)

    def _phase_blocked(self, state: RunState, phase: Phase) -> None:
        now = utc_now_iso()
        timing = self._phase_timing(state, phase)
        self._accumulate_active_seconds(timing, now)
        if not timing.get("started_at"):
            timing["started_at"] = now
        timing["blocked_at"] = now
        timing["last_status"] = "blocked"
        self._append_timing_event(timing, "blocked", now)
        self._refresh_wall_seconds(timing, now)

    def _phase_completed(self, state: RunState, phase: Phase) -> None:
        now = utc_now_iso()
        timing = self._phase_timing(state, phase)
        self._accumulate_active_seconds(timing, now)
        if timing.get("blocked_at"):
            timing["blocked_seconds"] = round(
                float(timing.get("blocked_seconds", 0.0)) + self._seconds_between(timing["blocked_at"], now),
                3,
            )
            timing["blocked_at"] = ""
        if not timing.get("started_at"):
            timing["started_at"] = now
        timing["completed_at"] = now
        timing["last_status"] = "completed"
        self._append_timing_event(timing, "completed", now)
        self._refresh_wall_seconds(timing, now)

    def _phase_error(self, state: RunState, phase: Phase) -> None:
        now = utc_now_iso()
        timing = self._phase_timing(state, phase)
        self._accumulate_active_seconds(timing, now)
        if timing.get("blocked_at"):
            timing["blocked_seconds"] = round(
                float(timing.get("blocked_seconds", 0.0)) + self._seconds_between(timing["blocked_at"], now),
                3,
            )
            timing["blocked_at"] = ""
        if not timing.get("started_at"):
            timing["started_at"] = now
        timing["completed_at"] = now
        timing["last_status"] = "error"
        self._append_timing_event(timing, "error", now)
        self._refresh_wall_seconds(timing, now)

    def _accumulate_active_seconds(self, timing: dict[str, Any], now: str) -> None:
        active_started_at = timing.get("active_started_at")
        if not active_started_at:
            return
        timing["active_seconds"] = round(
            float(timing.get("active_seconds", 0.0)) + self._seconds_between(active_started_at, now),
            3,
        )
        timing["active_started_at"] = ""

    def _refresh_wall_seconds(self, timing: dict[str, Any], now: str) -> None:
        started_at = timing.get("started_at")
        if started_at:
            timing["wall_seconds"] = round(self._seconds_between(started_at, now), 3)

    def _append_timing_event(self, timing: dict[str, Any], status: str, timestamp: str) -> None:
        events = timing.setdefault("events", [])
        if not isinstance(events, list):
            events = []
            timing["events"] = events
        if events and events[-1].get("status") == status and events[-1].get("at") == timestamp:
            return
        events.append({"status": status, "at": timestamp})
        if len(events) > 50:
            del events[:-50]

    def _seconds_between(self, start: str, end: str) -> float:
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, (end_dt - start_dt).total_seconds())

    def _requirement_packet(self, state: RunState) -> dict[str, Any]:
        return read_json(state.artifacts.get("requirement_packet", ""), default={}) or {}

    def _build_impact_payload(self, state: RunState, packet: dict[str, Any]) -> dict[str, Any]:
        requested_modules = self._requested_modules(packet)
        requested_sites = self._requested_sites(packet)
        module = (packet.get("candidate_modules") or requested_modules or [""])[0]
        site = packet.get("site", "")
        feature = packet.get("feature_name", "")
        new_cases = self._discover_new_cases(state, module, site, feature)
        existing_cases = self._discover_existing_cases(packet)
        self._mark_overlapping_source_groups(new_cases, existing_cases)
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
            "requested_modules": requested_modules,
            "requested_sites": requested_sites,
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
                        source_group="new_feature",
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
            return self._find_script_paths(payload)
        return []

    def _find_script_paths(self, value: Any) -> list[str]:
        if isinstance(value, str):
            return [value] if value.endswith(".py") else []
        if isinstance(value, list):
            paths: list[str] = []
            for item in value:
                paths.extend(self._find_script_paths(item))
            return paths
        if isinstance(value, dict):
            paths: list[str] = []
            for item in value.values():
                paths.extend(self._find_script_paths(item))
            return paths
        return []

    def _discover_existing_cases(self, packet: dict[str, Any]) -> list[ImpactCandidate]:
        modules = self._requested_modules(packet)
        primary_module = (packet.get("candidate_modules") or modules or [""])[0]
        requested_sites = [normalize_text(site) for site in self._requested_sites(packet)]
        feature = packet.get("feature_name", "")
        change_desc = packet.get("change_description", "")
        regression_root = Path(self.config.skills.get("paths", {}).get("regression_project_root", "")) / "test_cases"
        if not modules or not regression_root.exists():
            return []

        all_module_terms = {term for module in modules for term in self._tokenize_impact_text(module)}
        keywords_by_module = {
            module: [keyword for keyword in self._impact_keywords(module, feature, change_desc) if keyword not in all_module_terms]
            for module in modules
        }
        matches: list[ImpactCandidate] = []
        for script_path in sorted(regression_root.rglob("test_*.py")):
            text = read_text(script_path)
            searchable = normalize_text(f"{script_path.as_posix()} {text}")
            detected_sites = self._detect_script_sites(script_path, text)
            if requested_sites and detected_sites and not (set(requested_sites) & detected_sites):
                continue

            matched_modules: list[str] = []
            all_reasons: list[str] = []
            for module in modules:
                reasons = self._script_impact_reasons(
                    script_path=script_path,
                    text=text,
                    searchable=searchable,
                    module=module,
                    site=packet.get("site", ""),
                    feature=feature,
                    keywords=keywords_by_module[module],
                )
                if reasons:
                    matched_modules.append(module)
                    all_reasons.extend(reasons)
            if not all_reasons:
                continue
            reasons = sorted(dict.fromkeys(all_reasons))
            case_refs = self._extract_case_refs(script_path, text)
            related_case_id = case_refs[0]["case_id"] if len(case_refs) == 1 else ""
            related_nodeid = case_refs[0]["nodeid"] if len(case_refs) == 1 else ""
            nodeid_case_ids = {
                case_ref["nodeid"]: case_ref["case_id"]
                for case_ref in case_refs
                if case_ref.get("nodeid") and case_ref.get("case_id")
            }
            details = {
                "impact_reasons": reasons,
                "matched_modules": matched_modules,
                "matched_sites": sorted(detected_sites),
                "matched_nodeids": [case_ref["nodeid"] for case_ref in case_refs if case_ref.get("nodeid")],
                "matched_case_ids": [case_ref["case_id"] for case_ref in case_refs if case_ref.get("case_id")],
                "test_names": [case_ref["test_name"] for case_ref in case_refs if case_ref.get("test_name")],
                "allure_titles": [case_ref.get("allure_title", "") for case_ref in case_refs if case_ref.get("allure_title")],
                "nodeid_case_ids": nodeid_case_ids,
                "match_count": len(case_refs),
            }
            if case_refs:
                if len(case_refs) == 1:
                    details["test_name"] = case_refs[0]["test_name"]
                    details["allure_title"] = case_refs[0].get("allure_title", "")
                matches.append(
                    ImpactCandidate(
                        source_type="existing-script",
                        target=str(script_path),
                        module=matched_modules[0] if matched_modules else primary_module,
                        site=packet.get("site", ""),
                        feature_key=feature,
                        source_group="regression",
                        reason="; ".join(reasons),
                        related_case_id=related_case_id,
                        related_nodeid=related_nodeid,
                        details=details,
                    )
                )
            else:
                matches.append(
                    ImpactCandidate(
                        source_type="existing-script",
                        target=str(script_path),
                        module=matched_modules[0] if matched_modules else primary_module,
                        site=packet.get("site", ""),
                        feature_key=feature,
                        source_group="regression",
                        reason="; ".join(reasons),
                        details=details,
                    )
                )
        return matches

    def _mark_overlapping_source_groups(
        self,
        new_cases: list[ImpactCandidate],
        existing_cases: list[ImpactCandidate],
    ) -> None:
        new_names = {Path(candidate.target).name for candidate in new_cases if candidate.target}
        existing_names = {Path(candidate.target).name for candidate in existing_cases if candidate.target}
        overlap_names = new_names & existing_names
        for candidate in [*new_cases, *existing_cases]:
            if Path(candidate.target).name in overlap_names:
                candidate.source_group = "both"

    def _script_impact_reasons(
        self,
        *,
        script_path: Path,
        text: str,
        searchable: str,
        module: str,
        site: str,
        feature: str,
        keywords: list[str],
    ) -> list[str]:
        primary_reasons: list[str] = []
        secondary_reasons: list[str] = []
        metadata_reasons: list[str] = []
        if self._module_matches_path(script_path, module):
            primary_reasons.append("路径命中 module")
        if site and re.search(rf"@pytest\.mark\.{re.escape(site)}\b", text):
            secondary_reasons.append("pytest marker 命中 site")
        if module and self._has_module_marker(text, module):
            primary_reasons.append("pytest marker 命中 module")
        if feature and normalize_text(feature) in searchable:
            primary_reasons.append("allure/title/text 命中 feature")
        if re.search(r"@pytest\.mark\.case_id_[a-zA-Z0-9_]+", text):
            metadata_reasons.append("存在 case_id 元数据")
        if "::test_" in searchable or re.search(r"def test_[a-zA-Z0-9_]+\(", text):
            metadata_reasons.append("存在 nodeid/test 函数元数据")
        keyword_hits = [keyword for keyword in keywords if keyword in searchable]
        if keyword_hits:
            primary_reasons.append("关键字命中: " + ", ".join(keyword_hits[:5]))
        if not primary_reasons:
            return []
        return primary_reasons + secondary_reasons + metadata_reasons

    def _detect_script_sites(self, script_path: Path, text: str) -> set[str]:
        detected = {
            normalize_text(item)
            for item in re.findall(r"@pytest\.mark\.([a-zA-Z][a-zA-Z0-9_]*)\b", text or "")
            if normalize_text(item) in {"ae", "us", "sg", "au"}
        }
        config_match = re.search(r'["\']site["\']\s*:\s*["\']([^"\']+)["\']', text or "")
        if config_match:
            detected.add(normalize_text(config_match.group(1)))
        path_text = normalize_text(script_path.as_posix())
        for site in ("ae", "us", "sg", "au"):
            if re.search(rf"(?<![a-z0-9]){site}(?![a-z0-9])", path_text):
                detected.add(site)
        return {site for site in detected if site}

    def _impact_keywords(self, module: str, feature: str, change_desc: str) -> list[str]:
        module_terms = set(self._tokenize_impact_text(module))
        stopwords = {"纯回归", "回归", "regression", "pure", "测试", "test", "module", "site"}
        tokens: set[str] = set()
        for token_group in [feature, self._strip_module_aliases(change_desc, module)]:
            for normalized in self._tokenize_impact_text(token_group):
                if normalized in module_terms or normalized in stopwords:
                    continue
                if self._is_meaningful_impact_keyword(normalized):
                    tokens.add(normalized)
        return sorted(tokens)

    def _module_matches_path(self, script_path: Path, module: str) -> bool:
        pattern = self._module_scope_pattern(module)
        return bool(pattern and re.search(pattern, normalize_text(script_path.as_posix())))

    def _has_module_marker(self, text: str, module: str) -> bool:
        marker = re.sub(r"[^a-zA-Z0-9]+", "_", normalize_text(module)).strip("_")
        return bool(marker and re.search(rf"@pytest\.mark\.{re.escape(marker)}\b", text, re.IGNORECASE))

    def _module_scope_pattern(self, module: str) -> str:
        parts = self._tokenize_impact_text(module)
        if not parts:
            return ""
        body = r"[_\-\s/]+".join(re.escape(part) for part in parts)
        return rf"(?<![a-z0-9]){body}(?![a-z0-9])"

    def _strip_module_aliases(self, text: str, module: str) -> str:
        stripped = text or ""
        parts = self._tokenize_impact_text(module)
        aliases = {module or "", "_".join(parts), "-".join(parts), " ".join(parts), "/".join(parts)}
        for alias in sorted((item for item in aliases if item), key=len, reverse=True):
            stripped = re.sub(re.escape(alias), " ", stripped, flags=re.IGNORECASE)
        return stripped

    def _tokenize_impact_text(self, value: str) -> list[str]:
        return [
            normalized
            for token in re.split(r"[^a-zA-Z0-9\u4e00-\u9fff]+", value or "")
            if (normalized := normalize_text(token))
        ]

    def _is_meaningful_impact_keyword(self, value: str) -> bool:
        return len(value) >= 3 or bool(re.search(r"[\u4e00-\u9fff]{2,}", value))

    def _extract_case_refs(self, script_path: Path, text: str) -> list[dict[str, str]]:
        case_ids = re.findall(r"@pytest\.mark\.(case_id_[a-zA-Z0-9_]+)", text)
        allure_titles = re.findall(r'@allure\.title\("([^"]+)"\)', text)
        test_names = re.findall(r"def (test_[a-zA-Z0-9_]+)\(", text)
        refs: list[dict[str, str]] = []
        for index, test_name in enumerate(test_names):
            case_id = case_ids[index] if index < len(case_ids) else ""
            refs.append(
                {
                    "case_id": case_id,
                    "test_name": test_name,
                    "nodeid": f"{script_path.as_posix()}::{test_name}",
                    "allure_title": allure_titles[index] if index < len(allure_titles) else "",
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
            new_case_ids = set(filter(None, [new_case.get("related_case_id", "")]))
            new_case_ids.update(new_case.get("details", {}).get("matched_case_ids", []) or [])
            for existing_case in existing_cases:
                existing_target = existing_case.get("target", "")
                existing_case_ids = set(filter(None, [existing_case.get("related_case_id", "")]))
                existing_case_ids.update(existing_case.get("details", {}).get("matched_case_ids", []) or [])
                overlapping_case_ids = sorted(new_case_ids & existing_case_ids)
                same_case = bool(overlapping_case_ids)
                same_path = new_target and existing_target and Path(new_target).name == Path(existing_target).name
                if not (same_case or same_path):
                    continue
                decisions.append(
                    OverlapDecision(
                        new_target=new_target,
                        existing_target=existing_target,
                        decision="overlap",
                        reason="新旧脚本命中同名脚本或相同 case_id，需先执行影响回归再裁决",
                        related_case_id=overlapping_case_ids[0] if overlapping_case_ids else existing_case.get("related_case_id", ""),
                        related_nodeid=existing_case.get("related_nodeid", "")
                        or (existing_case.get("details", {}).get("matched_nodeids", []) or [""])[0],
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
        promotion_tasks: list[LegacyUpdateTask] = []
        legacy_tasks: list[LegacyUpdateTask] = []
        max_rounds = int(self.config.thresholds.get("gates", {}).get("max_fix_rounds", 3))
        module = (packet.get("candidate_modules") or [""])[0]
        site = packet.get("site", "")
        for record in records:
            if record.source_type == "new-script" and record.run_status == ImpactRunStatus.PASSED.value:
                promotion_task = self._build_new_script_promotion_task(packet, record, max_rounds)
                if promotion_task:
                    promotion_tasks.append(promotion_task)
                continue

            if record.source_type == "new-script" and record.category == AttributionCategory.LATEST_CHANGE.value:
                promotion_tasks.append(
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

            failed_nodeids = self._record_failed_nodeids(record)
            if failed_nodeids:
                nodeid_case_ids = dict(record.details.get("nodeid_case_ids", {}) or {})
                for nodeid in failed_nodeids:
                    legacy_tasks.append(
                        LegacyUpdateTask(
                            task_id=make_task_id("legacy"),
                            target_script=self._script_from_nodeid(nodeid) or record.target,
                            target_case_id=nodeid_case_ids.get(nodeid, record.related_case_id),
                            target_nodeid=nodeid,
                            impact_type="change-attribution",
                            recommended_action=self._recommended_action(record),
                            reason=record.reason or "影响回归判定为本次变更引起",
                            max_attempts=max_rounds,
                            details={
                                "module": record.module or module,
                                "site": record.site or site,
                                "source_type": record.source_type,
                                "executed_nodeids": list(record.details.get("executed_nodeids", []) or []),
                                "matched_nodeids": list(record.details.get("matched_nodeids", []) or []),
                            },
                        )
                    )
                continue

            legacy_tasks.append(
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
                        "module": record.module or module,
                        "site": record.site or site,
                        "source_type": record.source_type,
                        "matched_nodeids": list(record.details.get("matched_nodeids", []) or []),
                    },
                )
            )
        tasks.extend(promotion_tasks)
        tasks.extend(legacy_tasks)
        return tasks

    def _record_failed_nodeids(self, record: ImpactVerificationRecord) -> list[str]:
        failed = list(record.details.get("failed_nodeids", []) or [])
        if failed:
            return sorted(dict.fromkeys(str(item) for item in failed if item))
        if record.related_nodeid:
            return [record.related_nodeid]
        return []

    def _script_from_nodeid(self, nodeid: str) -> str:
        return nodeid.split("::", 1)[0] if nodeid else ""

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

    def _render_knowledge_base_update_context(self, state: RunState) -> str:
        packet = self._requirement_packet(state)
        module = (packet.get("candidate_modules") or [""])[0]
        lines = [
            "# Knowledge Base Update Context",
            "",
            f"- run_id: {state.run_id}",
            f"- change_mode: {state.change_mode}",
            f"- module: {module}",
            f"- site: {packet.get('site', '')}",
            f"- feature: {packet.get('feature_name', '')}",
            "",
            "## Primary Inputs",
            f"- final_report: {state.artifacts.get('final_report', '')}",
            f"- impact_candidates: {state.artifacts.get('impact_candidates', '')}",
            f"- change_attribution_report: {state.artifacts.get('change_attribution_report', '')}",
            f"- regression_selector_plan: {state.artifacts.get('regression_selector_plan', '')}",
            f"- text_case_manifest: {state.artifacts.get('text_case_manifest', '')}",
            f"- playwright_recording_outcomes: {state.artifacts.get('playwright_recording_outcomes', '')}",
            f"- playwright_recording_report: {state.artifacts.get('playwright_recording_report', '')}",
            f"- playwright_bug_report: {state.artifacts.get('playwright_bug_report', '')}",
            f"- playwright_case_outcomes: {state.artifacts.get('playwright_case_outcomes', '')}",
            "",
            "## Text Case Binding",
        ]
        kb_draft = state.artifacts.get("kb_text_case_draft_path", "")
        if kb_draft:
            lines.extend(
                [
                    f"- kb_text_case_draft_path: {kb_draft}",
                    "- 该路径是本次 run 的文本用例主输入。",
                    "- 若需要更新文本用例，请优先回写这个文件，不要新建第二份重复文档。",
                ]
            )
        else:
            lines.extend(
                [
                    "- 本次 run 没有阶段1文本用例草稿。",
                    "- 请基于 final_report / impact_candidates / change_attribution_report 更新三层结构化知识库。",
                ]
            )
        lines.extend(
            [
                "",
                "## Artifacts",
            ]
        )
        for key in [
            "final_report",
            "impact_candidates",
            "change_attribution_report",
            "regression_selector_plan",
            "text_case_manifest",
            "playwright_recording_outcomes",
            "playwright_recording_report",
            "playwright_bug_report",
            "playwright_case_outcomes",
        ]:
            value = state.artifacts.get(key, "")
            if value:
                lines.append(f"- {key}: {value}")
        lines.append(f"- 完整 artifact 清单见: {self.store.run_dir(state.run_id) / 'run_state.json'}")
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
        candidate_paths = {self._script_from_nodeid(path) or path for path in candidate_paths if path}
        requested_modules = self._requested_modules(packet)
        requested_sites = self._requested_sites(packet)
        nodeids = self._selector_nodeids(impact_payload, tasks)
        case_ids = self._selector_case_ids(impact_payload, tasks)
        execution_tasks = self._build_execution_tasks(packet, impact_payload, tasks, sorted(candidate_paths))
        task_limit = int(self.config.thresholds.get("execution", {}).get("max_execution_tasks", 50))
        nodeid_limit = int(self.config.thresholds.get("execution", {}).get("max_resolved_nodeids", 500))
        warnings: list[str] = []
        if len(execution_tasks) > task_limit:
            warnings.append(f"execution_tasks 数量 {len(execution_tasks)} 超过建议上限 {task_limit}，建议拆分执行")
        resolved_nodeid_count = len({nodeid for task in execution_tasks for nodeid in task.get("resolved_nodeids", [])})
        if resolved_nodeid_count > nodeid_limit:
            warnings.append(f"resolved_nodeids 数量 {resolved_nodeid_count} 超过建议上限 {nodeid_limit}，建议拆分执行")
        return {
            "module": (packet.get("candidate_modules") or [""])[0],
            "site": packet.get("site", ""),
            "requested_modules": requested_modules,
            "requested_sites": requested_sites,
            "feature_name": packet.get("feature_name", ""),
            "candidate_paths": sorted(path for path in candidate_paths if path),
            "case_ids": case_ids,
            "nodeids": nodeids,
            "selectors": [{"kind": "path", "value": path} for path in sorted(path for path in candidate_paths if path)],
            "execution_tasks": execution_tasks,
            "catalog_status": self._catalog_status(sorted(candidate_paths)),
            "warnings": warnings,
            "sources": self._selector_sources(impact_payload, tasks),
        }

    def _selector_nodeids(self, impact_payload: dict[str, Any], tasks: list[LegacyUpdateTask]) -> list[str]:
        values: list[str] = []
        for item in [*(impact_payload.get("new_cases", []) or []), *(impact_payload.get("existing_cases", []) or [])]:
            values.extend(item.get("details", {}).get("matched_nodeids", []) or [])
            if item.get("related_nodeid"):
                values.append(item["related_nodeid"])
        for task in tasks:
            if task.target_nodeid:
                values.append(task.target_nodeid)
            values.extend(task.details.get("matched_nodeids", []) or [])
        return sorted(dict.fromkeys(value for value in values if value))

    def _selector_case_ids(self, impact_payload: dict[str, Any], tasks: list[LegacyUpdateTask]) -> list[str]:
        values: list[str] = []
        for item in [*(impact_payload.get("new_cases", []) or []), *(impact_payload.get("existing_cases", []) or [])]:
            values.extend(item.get("details", {}).get("matched_case_ids", []) or [])
            if item.get("related_case_id"):
                values.append(item["related_case_id"])
        for task in tasks:
            if task.target_case_id:
                values.append(task.target_case_id)
        return sorted(dict.fromkeys(value for value in values if value))

    def _build_execution_tasks(
        self,
        packet: dict[str, Any],
        impact_payload: dict[str, Any],
        tasks: list[LegacyUpdateTask],
        candidate_paths: list[str],
    ) -> list[dict[str, Any]]:
        modules = self._requested_modules(packet) or [((packet.get("candidate_modules") or [""])[0])]
        sites = self._requested_sites(packet) or [""]
        metadata = self._selector_metadata_by_path(impact_payload, tasks)
        seen_nodeids: set[str] = set()
        seen_paths: set[str] = set()
        execution_tasks: list[dict[str, Any]] = []
        for module in [item for item in modules if item]:
            for site in sites:
                selected_paths: list[str] = []
                selected_nodeids: list[str] = []
                selected_case_ids: list[str] = []
                for path in candidate_paths:
                    item_metadata = metadata.get(path, {})
                    if not self._path_matches_execution_scope(path, item_metadata, module, site):
                        continue
                    path_nodeids = [nodeid for nodeid in item_metadata.get("nodeids", []) if nodeid not in seen_nodeids]
                    if path_nodeids:
                        selected_nodeids.extend(path_nodeids)
                        seen_nodeids.update(path_nodeids)
                    elif path not in seen_paths:
                        selected_paths.append(path)
                        seen_paths.add(path)
                    selected_case_ids.extend(item_metadata.get("case_ids", []))
                selected_paths = sorted(dict.fromkeys(selected_paths))
                selected_nodeids = sorted(dict.fromkeys(selected_nodeids))
                selected_case_ids = sorted(dict.fromkeys(selected_case_ids))
                selectors = [{"kind": "path", "value": path} for path in selected_paths]
                selectors.extend({"kind": "nodeid", "value": nodeid} for nodeid in selected_nodeids)
                execution_tasks.append(
                    {
                        "module": module,
                        "site": site,
                        "candidate_paths": selected_paths,
                        "resolved_nodeids": selected_nodeids,
                        "case_ids": selected_case_ids,
                        "selectors": selectors,
                        "selected_count": len(selected_paths) + len(selected_nodeids),
                        "warning": "" if selectors else "当前 module/site 组合没有解析到候选用例，dry-run 时应展示但跳过真实执行",
                    }
                )
        return execution_tasks

    def _selector_metadata_by_path(
        self,
        impact_payload: dict[str, Any],
        tasks: list[LegacyUpdateTask],
    ) -> dict[str, dict[str, Any]]:
        metadata: dict[str, dict[str, Any]] = {}
        for item in [*(impact_payload.get("new_cases", []) or []), *(impact_payload.get("existing_cases", []) or [])]:
            path = item.get("target", "")
            if not path:
                continue
            entry = metadata.setdefault(path, {"modules": set(), "sites": set(), "nodeids": set(), "case_ids": set()})
            entry["modules"].update(item.get("details", {}).get("matched_modules", []) or [])
            if item.get("module"):
                entry["modules"].add(item["module"])
            matched_sites = item.get("details", {}).get("matched_sites", []) or []
            entry["sites"].update(matched_sites)
            if item.get("site") and not matched_sites:
                entry["sites"].add(item["site"])
            entry["nodeids"].update(item.get("details", {}).get("matched_nodeids", []) or [])
            if item.get("related_nodeid"):
                entry["nodeids"].add(item["related_nodeid"])
            entry["case_ids"].update(item.get("details", {}).get("matched_case_ids", []) or [])
            if item.get("related_case_id"):
                entry["case_ids"].add(item["related_case_id"])
        for task in tasks:
            path = self._script_from_nodeid(task.target_script) or task.target_script
            if not path:
                continue
            entry = metadata.setdefault(path, {"modules": set(), "sites": set(), "nodeids": set(), "case_ids": set()})
            if task.details.get("module"):
                entry["modules"].add(task.details["module"])
            if task.details.get("site"):
                entry["sites"].add(task.details["site"])
            if task.target_nodeid:
                entry["nodeids"].add(task.target_nodeid)
            entry["nodeids"].update(task.details.get("matched_nodeids", []) or [])
            if task.target_case_id:
                entry["case_ids"].add(task.target_case_id)
        return {
            path: {
                "modules": sorted(values["modules"]),
                "sites": sorted(values["sites"]),
                "nodeids": sorted(values["nodeids"]),
                "case_ids": sorted(values["case_ids"]),
            }
            for path, values in metadata.items()
        }

    def _path_matches_execution_scope(self, path: str, metadata: dict[str, Any], module: str, site: str) -> bool:
        modules = set(metadata.get("modules", []) or [])
        if module and module not in modules and not self._module_matches_path(Path(path), module):
            return False
        sites = {normalize_text(item) for item in metadata.get("sites", []) or [] if item}
        if site and sites and normalize_text(site) not in sites:
            return False
        return True

    def _catalog_status(self, candidate_paths: list[str]) -> dict[str, Any]:
        regression_root = Path(self.config.skills.get("paths", {}).get("regression_project_root", ""))
        catalog_path = regression_root / "catalog" / "catalog.generated.json"
        if not catalog_path.exists():
            return {"path": str(catalog_path), "exists": False, "stale": True, "reason": "catalog.generated.json 不存在"}
        try:
            catalog_mtime = catalog_path.stat().st_mtime
            stale_paths = [
                path
                for path in candidate_paths
                if Path(path).exists() and Path(path).stat().st_mtime > catalog_mtime
            ]
        except OSError as exc:
            return {"path": str(catalog_path), "exists": True, "stale": True, "reason": f"catalog 检查失败: {exc}"}
        return {
            "path": str(catalog_path),
            "exists": True,
            "stale": bool(stale_paths),
            "reason": "候选脚本晚于 catalog.generated.json" if stale_paths else "",
            "stale_paths": stale_paths,
        }

    def _selector_sources(self, impact_payload: dict[str, Any], tasks: list[LegacyUpdateTask]) -> list[dict[str, str]]:
        sources: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for item in [*(impact_payload.get("new_cases", []) or []), *(impact_payload.get("existing_cases", []) or [])]:
            target = item.get("target", "")
            source_group = item.get("source_group", "") or item.get("source_type", "")
            key = (target, source_group)
            if not target or key in seen:
                continue
            seen.add(key)
            sources.append({"target": target, "source_group": source_group, "reason": item.get("reason", "")})
        for task in tasks:
            source_group = str(task.details.get("source_type") or task.impact_type)
            key = (task.target_script, source_group)
            if task.target_script and key not in seen:
                seen.add(key)
                sources.append({"target": task.target_script, "source_group": source_group, "reason": task.reason})
        return sources

    def _refresh_selector_plan(self, state: RunState, tasks: list[LegacyUpdateTask]) -> Path:
        packet = self._requirement_packet(state)
        impact_payload = read_json(state.artifacts.get("impact_candidates", ""), default={}) or {}
        selector_plan = self._build_selector_plan(packet, impact_payload, tasks)
        selector_path = self.store.artifact_path(state.run_id, "regression_selector_plan.json")
        write_json(selector_path, selector_plan)
        return selector_path
