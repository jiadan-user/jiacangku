from __future__ import annotations

import os
import sys
from pathlib import Path

from qa_agent.io import read_text
from qa_agent.utils import run_command


class OkUISkillIntegration:
    def __init__(self, script_path: str | Path, project_root: str | Path, venv_python: str | Path) -> None:
        self.script_path = Path(script_path).resolve()
        self.project_root = Path(project_root).resolve()
        self.venv_python = Path(venv_python).resolve()

    def doctor(self):
        return self._run([self.python_bin, str(self.script_path), "doctor"])

    def dry_run(self, module: str, relative_path: str):
        return self._run(
            [
                self.python_bin,
                str(self.script_path),
                "run",
                "--module",
                module,
                "--path",
                relative_path,
                "--dry-run",
            ]
        )

    def real_run(self, selectors: list[str]):
        return self._run([self.python_bin, str(self.script_path), "run", *selectors])

    def module_map_text(self) -> str:
        return read_text(self.script_path.parents[1] / "references" / "module-map.md")

    @property
    def python_bin(self) -> str:
        return str(self.venv_python) if self.venv_python.exists() else sys.executable

    def _run(self, command: list[str]):
        env = os.environ.copy()
        pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(self.project_root) + (os.pathsep + pythonpath if pythonpath else "")
        return run_command(command, cwd=self.project_root, env=env)
