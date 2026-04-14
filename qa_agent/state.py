from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from qa_agent.io import read_json, write_json, write_text
from qa_agent.models import ConductorPhase, PhaseStatus, RunState, RunStatus, to_data


class RunStore:
    def __init__(self, state_root: Path) -> None:
        self.state_root = state_root
        self.runs_root = state_root / "runs"
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self._ensure_project_memory()

    def _ensure_project_memory(self) -> None:
        memory_path = self.state_root / "project-memory.json"
        if not memory_path.exists():
            write_json(
                memory_path,
                {
                    "模块约定": {},
                    "case_id约定": {},
                    "站点默认值": {},
                    "模板偏好": {},
                    "视觉门禁阈值": 90,
                },
            )
        notepad_path = self.state_root / "notepad.md"
        if not notepad_path.exists():
            write_text(notepad_path, "# QA Agent 工作便签\n\n")

    def create_run(self, change_mode: str) -> RunState:
        run_id = uuid4().hex[:12]
        state = RunState(
            run_id=run_id,
            status=RunStatus.PLANNED.value,
            current_phase=ConductorPhase.INTAKE.value,
            change_mode=change_mode,
            phase_statuses={phase.value: PhaseStatus.PENDING.value for phase in ConductorPhase},
        )
        self.save(state)
        self.run_dir(run_id).mkdir(parents=True, exist_ok=True)
        return state

    def load(self, run_id: str) -> RunState:
        payload = read_json(self.run_dir(run_id) / "run_state.json")
        if not payload:
            raise FileNotFoundError(f"未找到运行记录: {run_id}")
        return RunState(**payload)

    def save(self, state: RunState) -> None:
        state.touch()
        write_json(self.run_dir(state.run_id) / "run_state.json", to_data(state))

    def run_dir(self, run_id: str) -> Path:
        return self.runs_root / run_id

    def artifact_path(self, run_id: str, relative_path: str) -> Path:
        path = self.run_dir(run_id) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def set_phase(self, state: RunState, phase: ConductorPhase, status: PhaseStatus, reason: str = "") -> RunState:
        next_state = replace(state)
        next_state.current_phase = phase.value
        next_state.phase_statuses[phase.value] = status.value
        if reason:
            next_state.blocked_reason = reason
        self.save(next_state)
        return next_state
