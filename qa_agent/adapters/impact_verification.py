from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from qa_agent.config import AppConfig
from qa_agent.models import (
    AttributionCategory,
    ChangeMode,
    ImpactCandidate,
    ImpactRunStatus,
    ImpactVerificationOutcome,
    ImpactVerificationRecord,
)
from qa_agent.utils import normalize_text, run_command

from .legacy_update import OkUISkillRuntime


class ImpactVerificationExecutor:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.runtime = OkUISkillRuntime(config)
        self.regression_root = Path(config.skills.get("paths", {}).get("regression_project_root", ""))

    def verify(
        self,
        *,
        run_dir: Path,
        packet: dict[str, Any],
        impact_payload: dict[str, Any],
    ) -> ImpactVerificationOutcome:
        staging_root = run_dir / "impact_validation_staging"
        staging_root.mkdir(parents=True, exist_ok=True)

        candidates = self._candidate_objects(impact_payload)
        records = [self._verify_candidate(candidate, packet, staging_root) for candidate in candidates]
        selector_plan = self._build_selector_plan(packet, records)
        return ImpactVerificationOutcome(selector_plan=selector_plan, records=records)

    def _candidate_objects(self, impact_payload: dict[str, Any]) -> list[ImpactCandidate]:
        raw_candidates = [*(impact_payload.get("new_cases", []) or []), *(impact_payload.get("existing_cases", []) or [])]
        candidates: list[ImpactCandidate] = []
        seen: set[tuple[str, str]] = set()
        for item in raw_candidates:
            candidate = item if isinstance(item, ImpactCandidate) else ImpactCandidate(**item)
            key = (candidate.target, candidate.related_nodeid)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(candidate)
        return candidates

    def _verify_candidate(
        self,
        candidate: ImpactCandidate,
        packet: dict[str, Any],
        staging_root: Path,
    ) -> ImpactVerificationRecord:
        target_path = Path(candidate.target) if candidate.target else Path()
        staged_path = self._stage_candidate(candidate, target_path, staging_root)
        executable_path = staged_path or target_path

        record = ImpactVerificationRecord(
            source_type=candidate.source_type,
            target=candidate.target,
            staged_target=str(staged_path) if staged_path else "",
            module=candidate.module,
            site=candidate.site,
            feature_key=candidate.feature_key,
            related_case_id=candidate.related_case_id,
            related_nodeid=candidate.related_nodeid,
            details=dict(candidate.details or {}),
        )

        if not executable_path or not executable_path.exists():
            record.summary = "候选脚本不存在，无法执行影响回归"
            record.category = AttributionCategory.UNCERTAIN.value
            record.next_action = "人工确认是否需要补齐脚本或跳过该候选"
            record.reason = "未找到可执行的 staged/original 脚本"
            return record

        command = [self.runtime.python_bin, "-m", "pytest", str(executable_path), "-q"]
        record.command = command
        env = {"PYTHONPATH": str(self.regression_root)} if self.regression_root.exists() else None
        proc = run_command(command, cwd=self.regression_root if self.regression_root.exists() else staging_root, env=env)

        record.returncode = proc.returncode
        record.stdout_excerpt = self._excerpt(proc.stdout)
        record.stderr_excerpt = self._excerpt(proc.stderr)
        record.summary = self._summary(proc.stdout, proc.stderr, proc.returncode)
        if proc.returncode == 0:
            record.run_status = ImpactRunStatus.PASSED.value
            record.category = AttributionCategory.PASSED.value
            record.reason = "受影响用例执行通过"
            if candidate.source_type == "new-script" and not self._is_under_regression_project(target_path):
                record.next_action = "人工确认后进入新脚本 promotion 流程"
            else:
                record.next_action = "人工确认后决定是否直接进入阶段3回归"
            return record

        record.run_status = ImpactRunStatus.FAILED.value
        category, reason, next_action = self._classify_failure(candidate, packet, record)
        record.category = category
        record.reason = reason
        record.next_action = next_action
        return record

    def _stage_candidate(self, candidate: ImpactCandidate, target_path: Path, staging_root: Path) -> Path | None:
        if candidate.source_type != "new-script" or not target_path.exists():
            return None
        target_dir = staging_root / (candidate.module or "misc")
        target_dir.mkdir(parents=True, exist_ok=True)
        staged_path = target_dir / target_path.name
        shutil.copy2(target_path, staged_path)
        return staged_path

    def _classify_failure(
        self,
        candidate: ImpactCandidate,
        packet: dict[str, Any],
        record: ImpactVerificationRecord,
    ) -> tuple[str, str, str]:
        searchable = normalize_text(
            " ".join(
                [
                    candidate.reason,
                    candidate.target,
                    candidate.related_nodeid,
                    record.summary,
                    record.stdout_excerpt,
                    record.stderr_excerpt,
                    packet.get("change_description", ""),
                    packet.get("feature_name", ""),
                ]
            )
        )
        environment_tokens = [
            "timeout",
            "timed out",
            "network",
            "dns",
            "connection",
            "502",
            "503",
            "504",
            "forbidden",
            "unauthorized",
            "login",
            "fixture",
            "environment",
            "data",
        ]
        preexisting_tokens = [
            "syntaxerror",
            "importerror",
            "modulenotfounderror",
            "nameerror",
            "attributeerror",
            "indentationerror",
        ]
        selector_tokens = ["selector", "locator", "not found", "detached", "strict mode violation"]
        assertion_tokens = ["assert", "expected", "actual", "mismatch"]

        if any(token in searchable for token in environment_tokens):
            return (
                AttributionCategory.ENVIRONMENT.value,
                "失败信息更像环境、账号或测试数据问题",
                "先排查环境/账号/数据，再决定是否重跑或更新脚本",
            )
        if any(token in searchable for token in preexisting_tokens):
            return (
                AttributionCategory.PREEXISTING.value,
                "失败信息更像历史脚本质量问题或无关异常",
                "记录问题，不自动改脚本，待人工确认是否纳入本次变更范围",
            )
        if candidate.source_type == "new-script" and packet.get("change_mode") in (
            ChangeMode.NEW_FEATURE.value,
            ChangeMode.MIXED.value,
        ):
            return (
                AttributionCategory.LATEST_CHANGE.value,
                "新脚本对应本次新需求/混合变更，失败大概率与最新变更相关",
                "人工确认后进入新脚本修正或重新录制流程",
            )
        if any(token in searchable for token in selector_tokens):
            return (
                AttributionCategory.LATEST_CHANGE.value,
                "失败表现为定位/入口失效，符合本次受影响范围",
                "人工确认后进入 selector 修复或重录任务",
            )
        if any(token in searchable for token in assertion_tokens):
            return (
                AttributionCategory.LATEST_CHANGE.value,
                "失败表现为断言不匹配，符合本次受影响范围",
                "人工确认后进入 assertion 更新任务",
            )
        if packet.get("change_description"):
            return (
                AttributionCategory.LATEST_CHANGE.value,
                "该用例因本次改动被纳入受影响集合，当前失败先按最新变更处理",
                "人工确认后进入旧脚本更新任务队列",
            )
        return (
            AttributionCategory.UNCERTAIN.value,
            "缺少足够信号判断是否由本次变更引起",
            "转 manual-review 候选，由人工裁决",
        )

    def _build_selector_plan(
        self,
        packet: dict[str, Any],
        records: list[ImpactVerificationRecord],
    ) -> dict[str, Any]:
        selectors: list[dict[str, str]] = []
        candidate_paths: set[str] = set()
        for record in records:
            path = record.staged_target or record.target
            if not path:
                continue
            candidate_paths.add(path)
            selectors.append({"kind": "path", "value": path})
        return {
            "module": (packet.get("candidate_modules") or [""])[0],
            "site": packet.get("site", ""),
            "feature_name": packet.get("feature_name", ""),
            "candidate_paths": sorted(candidate_paths),
            "selectors": selectors,
            "nodeids": sorted({record.related_nodeid for record in records if record.related_nodeid}),
            "case_ids": sorted({record.related_case_id for record in records if record.related_case_id}),
        }

    def _is_under_regression_project(self, target_path: Path) -> bool:
        if not target_path or not target_path.exists() or not self.regression_root.exists():
            return False
        try:
            target_path.resolve().relative_to(self.regression_root.resolve())
            return True
        except ValueError:
            return False

    def _summary(self, stdout: str, stderr: str, returncode: int) -> str:
        combined = "\n".join(part for part in [stdout.strip(), stderr.strip()] if part.strip())
        for line in combined.splitlines():
            line = line.strip()
            if line:
                return line[:240]
        return "执行通过" if returncode == 0 else "执行失败，但未捕获到有效摘要"

    def _excerpt(self, text: str, max_lines: int = 6, max_chars: int = 600) -> str:
        lines = [line.rstrip() for line in (text or "").splitlines() if line.strip()]
        excerpt = "\n".join(lines[:max_lines])
        return excerpt[:max_chars]
