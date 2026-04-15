from __future__ import annotations

import ast
import shutil
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from qa_agent.config import AppConfig
from qa_agent.io import read_text, write_text
from qa_agent.models import (
    LegacyUpdateGate,
    LegacyUpdateRoundOutcome,
    LegacyUpdateTask,
    LegacyUpdateTaskStatus,
    ValidationResult,
)
from qa_agent.utils import run_command

from .promotion_guard import PromotionGuard


class OkUISkillRuntime:
    def __init__(self, config: AppConfig) -> None:
        commands = config.skills.get("commands", {}).get("ok_ui_skill", {})
        paths = config.skills.get("paths", {})
        self.script = Path(commands.get("script", ""))
        self.python_bin = str(Path(commands.get("venv_python", "")))
        self.project_root = Path(paths.get("regression_project_root", ""))

    def doctor(self):
        return run_command(
            [self.python_bin, str(self.script), "doctor"],
            cwd=self.project_root,
            env={"PYTHONPATH": str(self.project_root)},
        )

    def dry_run(self, module: str, relative_path: str):
        return run_command(
            [
                self.python_bin,
                str(self.script),
                "run",
                "--module",
                module,
                "--path",
                relative_path,
                "--dry-run",
            ],
            cwd=self.project_root,
            env={"PYTHONPATH": str(self.project_root)},
        )


class LegacyUpdateValidator:
    def validate(self, candidate_path: Path, task: LegacyUpdateTask) -> list[ValidationResult]:
        raise NotImplementedError


class DefaultLegacyUpdateValidator(LegacyUpdateValidator):
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.runtime = OkUISkillRuntime(config)
        self.regression_root = Path(config.skills.get("paths", {}).get("regression_project_root", ""))
        self.guard = PromotionGuard(
            self.runtime,
            max_wait_ms=int(config.thresholds.get("gates", {}).get("max_wait_timeout_ms", 300)),
            require_runtime_checks=bool(config.thresholds.get("promotion", {}).get("require_dry_run", True)),
        )

    def validate(self, candidate_path: Path, task: LegacyUpdateTask) -> list[ValidationResult]:
        results = [self._check_syntax(candidate_path)]
        module = task.details.get("module") or self._infer_module(task.target_script)
        if module and self.regression_root.exists():
            try:
                results.extend(self.guard.evaluate([str(candidate_path)], module)[str(candidate_path)])
            except Exception as exc:  # pragma: no cover - best effort runtime validation
                results.append(
                    ValidationResult(
                        ok=False,
                        name="运行时校验",
                        message=f"PromotionGuard 执行失败: {exc}",
                    )
                )
        return results

    def _infer_module(self, target_script: str) -> str:
        target = Path(target_script)
        parts = target.parts
        if "test_cases" in parts:
            index = parts.index("test_cases")
            if index + 1 < len(parts):
                return parts[index + 1]
        return target.parent.name

    def _check_syntax(self, candidate_path: Path) -> ValidationResult:
        try:
            ast.parse(read_text(candidate_path))
            return ValidationResult(ok=True, name="语法校验", message="Python 语法有效")
        except SyntaxError as exc:
            return ValidationResult(ok=False, name="语法校验", message=f"Python 语法错误: {exc}")


class LegacyUpdateExecutor:
    def __init__(self, config: AppConfig, validator: LegacyUpdateValidator | None = None) -> None:
        self.config = config
        self.validator = validator or DefaultLegacyUpdateValidator(config)

    def run_round(
        self,
        *,
        run_dir: Path,
        tasks: list[LegacyUpdateTask],
        round_index: int,
    ) -> LegacyUpdateRoundOutcome:
        results: list[dict[str, Any]] = []
        updated_tasks: list[LegacyUpdateTask] = []
        for task in tasks:
            if task.status in (LegacyUpdateTaskStatus.COMPLETED.value, LegacyUpdateTaskStatus.MANUAL_REVIEW.value):
                updated_tasks.append(task)
                continue
            updated_tasks.append(self._run_task(run_dir, task, results))

        gate = self._build_gate(updated_tasks, round_index)
        return LegacyUpdateRoundOutcome(tasks=updated_tasks, gate=gate, results=results)

    def _run_task(
        self,
        run_dir: Path,
        task: LegacyUpdateTask,
        results: list[dict[str, Any]],
    ) -> LegacyUpdateTask:
        task.status = LegacyUpdateTaskStatus.RUNNING.value
        task.attempts += 1
        task.max_attempts = task.max_attempts or int(self.config.thresholds.get("gates", {}).get("max_fix_rounds", 3))

        workspace = run_dir / "legacy_updates" / task.task_id
        backup_dir = workspace / "backup"
        candidate_path = workspace / "candidate.py"
        backup_dir.mkdir(parents=True, exist_ok=True)

        target_path = Path(task.target_script)
        if target_path.exists():
            shutil.copy2(target_path, backup_dir / target_path.name)

        if task.recommended_action == "manual-review":
            task.status = LegacyUpdateTaskStatus.MANUAL_REVIEW.value
            results.append(self._result(task, False, candidate_path, "任务要求人工审阅，未进入自动循环"))
            return task

        ok, message = self._materialize_candidate(task, target_path, candidate_path, workspace)
        if not ok:
            return self._fail_or_retry(task, results, candidate_path, message)

        validations = [asdict(item) for item in self.validator.validate(candidate_path, task)]
        validation_ok = all(item["ok"] for item in validations) if validations else True
        if validation_ok:
            shutil.copy2(candidate_path, target_path)
            task.status = LegacyUpdateTaskStatus.COMPLETED.value
            results.append(self._result(task, True, candidate_path, "候选版本通过验收并已自动合并", validations))
            return task

        message = "; ".join(item["message"] for item in validations if not item["ok"]) or "候选版本未通过验收"
        return self._fail_or_retry(task, results, candidate_path, message, validations)

    def _materialize_candidate(
        self,
        task: LegacyUpdateTask,
        target_path: Path,
        candidate_path: Path,
        workspace: Path,
    ) -> tuple[bool, str]:
        if task.recommended_action in {"update-assertion", "update-selector"}:
            return self._patch_candidate(task, target_path, candidate_path)
        if task.recommended_action in {"re-record", "split-case"}:
            return self._replace_candidate(task, target_path, candidate_path, workspace)
        return False, f"不支持的更新动作: {task.recommended_action}"

    def _patch_candidate(self, task: LegacyUpdateTask, target_path: Path, candidate_path: Path) -> tuple[bool, str]:
        if not target_path.exists():
            return False, f"目标脚本不存在: {target_path}"
        text = read_text(target_path)
        replacements = list(task.details.get("replacements", []) or [])
        if not replacements:
            task.recommended_action = "re-record"
            return False, "未提供可应用 patch，已升级为 re-record"

        updated = text
        applied = 0
        for replacement in replacements:
            old = str(replacement.get("old", ""))
            new = str(replacement.get("new", ""))
            count = replacement.get("count")
            if not old or old not in updated:
                continue
            updated = updated.replace(old, new, int(count)) if count else updated.replace(old, new)
            applied += 1

        if applied == 0:
            task.recommended_action = "re-record"
            return False, "未命中任何 patch 片段，已升级为 re-record"

        append_lines = task.details.get("append_lines", []) or []
        if append_lines:
            suffix = "\n".join(str(line) for line in append_lines)
            updated = updated.rstrip() + "\n" + suffix + "\n"

        write_text(candidate_path, updated)
        return True, f"已应用 {applied} 处 patch"

    def _replace_candidate(
        self,
        task: LegacyUpdateTask,
        target_path: Path,
        candidate_path: Path,
        workspace: Path,
    ) -> tuple[bool, str]:
        replacement_source = task.details.get("replacement_source_path")
        replacement_text = task.details.get("replacement_text")
        proof_artifact = task.details.get("proof_artifact_path")

        if proof_artifact and Path(proof_artifact).exists():
            proof_target = workspace / Path(proof_artifact).name
            if not proof_target.exists():
                shutil.copy2(proof_artifact, proof_target)

        if replacement_source and Path(replacement_source).exists():
            shutil.copy2(replacement_source, candidate_path)
            return True, f"已使用候选替换文件: {replacement_source}"
        if replacement_text:
            write_text(candidate_path, str(replacement_text))
            return True, "已写入候选替换文本"
        if target_path.exists():
            shutil.copy2(target_path, candidate_path)
            return False, "缺少替换内容，无法完成 re-record/split-case"
        return False, "缺少替换内容且目标脚本不存在"

    def _fail_or_retry(
        self,
        task: LegacyUpdateTask,
        results: list[dict[str, Any]],
        candidate_path: Path,
        message: str,
        validations: list[dict[str, Any]] | None = None,
    ) -> LegacyUpdateTask:
        if task.attempts >= task.max_attempts:
            task.status = LegacyUpdateTaskStatus.MANUAL_REVIEW.value
            final_message = f"{message}；超过最大轮次，升级为 manual-review"
        else:
            task.status = LegacyUpdateTaskStatus.RETRY.value
            final_message = message
        results.append(self._result(task, False, candidate_path, final_message, validations or []))
        return task

    def _result(
        self,
        task: LegacyUpdateTask,
        ok: bool,
        candidate_path: Path,
        message: str,
        validations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return {
            "task_id": task.task_id,
            "target_script": task.target_script,
            "target_case_id": task.target_case_id,
            "target_nodeid": task.target_nodeid,
            "recommended_action": task.recommended_action,
            "status": task.status,
            "ok": ok,
            "attempts": task.attempts,
            "candidate_path": str(candidate_path),
            "message": message,
            "validations": validations or [],
        }

    def _build_gate(self, tasks: list[LegacyUpdateTask], round_index: int) -> LegacyUpdateGate:
        pending_count = sum(task.status == LegacyUpdateTaskStatus.PENDING.value for task in tasks)
        retry_count = sum(task.status == LegacyUpdateTaskStatus.RETRY.value for task in tasks)
        completed_count = sum(task.status == LegacyUpdateTaskStatus.COMPLETED.value for task in tasks)
        manual_review_count = sum(task.status == LegacyUpdateTaskStatus.MANUAL_REVIEW.value for task in tasks)
        total_count = len(tasks)
        all_completed = total_count == completed_count
        return LegacyUpdateGate(
            round_index=round_index,
            total_count=total_count,
            pending_count=pending_count,
            retry_count=retry_count,
            completed_count=completed_count,
            manual_review_count=manual_review_count,
            all_completed=all_completed,
            has_manual_review=manual_review_count > 0,
        )


def make_task_id(prefix: str = "legacy") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"
