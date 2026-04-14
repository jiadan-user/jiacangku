#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    project_root = skill_root / "bundled" / "ok_autotest_ui_pc"
    venv_python = project_root / "venv" / "bin" / "python"
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    python_bin = str(venv_python) if venv_python.exists() else sys.executable
    command = [python_bin, "-m", "tooling.ok_test", *sys.argv[1:]]
    result = subprocess.run(command, cwd=project_root, env=env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
