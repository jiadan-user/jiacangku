from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from qa_agent.io import read_json, write_json, write_text
from qa_agent.models import Phase, PhaseStatus, RunState, RunStatus, to_data


class RunStateConflictError(RuntimeError):
    pass


class RunLockTimeoutError(RuntimeError):
    pass


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
                    "module_conventions": {},
                    "case_id_conventions": {},
                    "site_defaults": {},
                    "template_preferences": {},
                    "visual_threshold": 90,
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
            current_phase=Phase.INTAKE.value,
            change_mode=change_mode,
            phase_statuses={phase.value: PhaseStatus.PENDING.value for phase in Phase},
        )
        self.save(state)
        self.run_dir(run_id).mkdir(parents=True, exist_ok=True)
        return state

    def load(self, run_id: str) -> RunState:
        payload = read_json(self.run_dir(run_id) / "run_state.json")
        if not payload:
            raise FileNotFoundError(f"未找到运行记录: {run_id}")
        return RunState(**payload)

    def save(self, state: RunState, *, expected_version: int | None = None) -> None:
        state_path = self.run_dir(state.run_id) / "run_state.json"
        current = read_json(state_path, default={}) or {}
        current_version = int(current.get("version", 0))
        if expected_version is not None and current and current_version != expected_version:
            raise RunStateConflictError(
                f"运行 {state.run_id} 状态版本已变化，请重新 status/next 后再操作"
            )
        state.version = current_version + 1
        state.touch()
        write_json(state_path, to_data(state))

    def run_dir(self, run_id: str) -> Path:
        return self.runs_root / run_id

    def artifact_path(self, run_id: str, relative_path: str) -> Path:
        path = self.run_dir(run_id) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @contextmanager
    def locked_run(self, run_id: str, timeout_seconds: float = 10.0):
        lock_path = self.run_dir(run_id) / ".run.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        start = time.monotonic()
        fd: int | None = None
        while True:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode("utf-8"))
                break
            except FileExistsError:
                if time.monotonic() - start >= timeout_seconds:
                    raise RunLockTimeoutError(f"运行 {run_id} 正在被其他进程操作，请稍后重试")
                time.sleep(0.05)
        try:
            yield
        finally:
            if fd is not None:
                os.close(fd)
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass
