from __future__ import annotations

import re
import shutil
from pathlib import Path

from qa_agent.io import read_text, write_text
from qa_agent.models import ValidationResult


class PromotionGuard:
    def __init__(
        self,
        ok_ui_skill,
        max_wait_ms: int = 300,
        require_runtime_checks: bool = True,
        keep_staging_files: bool = False,
    ) -> None:
        self.ok_ui_skill = ok_ui_skill
        self.max_wait_ms = max_wait_ms
        self.require_runtime_checks = require_runtime_checks
        self.keep_staging_files = keep_staging_files

    def evaluate(self, script_paths: list[str], module: str) -> dict[str, list[ValidationResult]]:
        results: dict[str, list[ValidationResult]] = {}
        for script_path in script_paths:
            results[script_path] = self._evaluate_one(Path(script_path), module)
        return results

    def promote(self, script_paths: list[str], module: str) -> list[str]:
        promoted_paths: list[str] = []
        target_root = self.ok_ui_skill.project_root / "test_cases" / module
        target_root.mkdir(parents=True, exist_ok=True)
        for source in script_paths:
            source_path = Path(source)
            target = target_root / source_path.name
            shutil.copy2(source_path, target)
            promoted_paths.append(str(target))
        return promoted_paths

    def _evaluate_one(self, script_path: Path, module: str) -> list[ValidationResult]:
        text = read_text(script_path)
        checks = [
            self._check_filename(script_path),
            self._check_config(text),
            self._check_markers(text),
            self._check_waits(text),
            self._check_allure(text),
        ]
        if self.require_runtime_checks:
            staging_path = self._stage(script_path, module)
            try:
                checks.extend(self._runtime_checks(staging_path, module))
            finally:
                if staging_path.exists() and not self.keep_staging_files:
                    staging_path.unlink()
                    try:
                        staging_path.parent.rmdir()
                    except OSError:
                        pass
        return checks

    def _check_filename(self, script_path: Path) -> ValidationResult:
        ok = script_path.name.startswith("test_") and script_path.suffix == ".py"
        return ValidationResult(ok=ok, name="文件命名", message="文件命名合法" if ok else "文件名必须以 test_ 开头并以 .py 结尾")

    def _check_config(self, text: str) -> ValidationResult:
        ok = "_CONFIG = " in text
        return ValidationResult(ok=ok, name="_CONFIG 配置", message="包含 _CONFIG" if ok else "缺少 _CONFIG")

    def _check_markers(self, text: str) -> ValidationResult:
        has_priority = bool(re.search(r"@pytest\.mark\.p[0-3]", text))
        has_case_id = bool(re.search(r"@pytest\.mark\.case_id_[a-z0-9_]+", text))
        has_module_mark = len(re.findall(r"@pytest\.mark\.[a-zA-Z_][a-zA-Z0-9_]*", text)) >= 3
        ok = has_priority and has_case_id and has_module_mark
        return ValidationResult(
            ok=ok,
            name="Pytest 标记",
            message="标记齐全" if ok else "缺少 priority/case_id/模块或站点标记",
            details={"has_priority": has_priority, "has_case_id": has_case_id, "has_module_mark": has_module_mark},
        )

    def _check_allure(self, text: str) -> ValidationResult:
        ok = all(token in text for token in ["@allure.feature(", "@allure.story(", "@allure.title("])
        return ValidationResult(ok=ok, name="Allure 装饰器", message="Allure 装饰器齐全" if ok else "缺少 allure.feature/story/title")

    def _check_waits(self, text: str) -> ValidationResult:
        values = [int(value) for value in re.findall(r"page\.wait_for_timeout\((\d+)\)", text)]
        offenders = [value for value in values if value > self.max_wait_ms]
        ok = not offenders
        return ValidationResult(
            ok=ok,
            name="等待时长",
            message="未发现超长 wait_for_timeout" if ok else f"发现超长 wait_for_timeout: {offenders}",
            details={"offenders": offenders},
        )

    def _stage(self, script_path: Path, module: str) -> Path:
        staging_dir = self.ok_ui_skill.project_root / "test_cases" / module / "__qa_agent_staging__"
        staging_dir.mkdir(parents=True, exist_ok=True)
        target = staging_dir / script_path.name
        write_text(target, script_path.read_text(encoding="utf-8"))
        return target

    def _runtime_checks(self, staged_path: Path, module: str) -> list[ValidationResult]:
        relative_path = staged_path.relative_to(self.ok_ui_skill.project_root).as_posix()
        doctor = self.ok_ui_skill.doctor()
        collect = self._collect_only(staged_path)
        dry_run = self.ok_ui_skill.dry_run(module, relative_path)
        return [
            ValidationResult(ok=doctor.returncode == 0, name="Doctor 检查", message=doctor.stdout or doctor.stderr),
            ValidationResult(ok=collect.returncode == 0, name="收集校验", message=collect.stdout or collect.stderr),
            ValidationResult(ok=dry_run.returncode == 0, name="回归预演", message=dry_run.stdout or dry_run.stderr),
        ]

    def _collect_only(self, staged_path: Path):
        command = [
            self.ok_ui_skill.python_bin,
            "-m",
            "pytest",
            "--collect-only",
            str(staged_path),
        ]
        env = {
            "PYTHONPATH": str(self.ok_ui_skill.project_root),
        }
        from qa_agent.utils import run_command

        return run_command(command, cwd=self.ok_ui_skill.project_root, env=env)
