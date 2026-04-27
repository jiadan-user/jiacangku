from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

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
        by_key: dict[tuple[str, str], ImpactCandidate] = {}
        for item in raw_candidates:
            candidate = item if isinstance(item, ImpactCandidate) else ImpactCandidate(**item)
            key = (candidate.source_type, candidate.target)
            existing = by_key.get(key)
            if existing:
                self._merge_candidate_details(existing, candidate)
                continue
            by_key[key] = candidate
            candidates.append(candidate)
        return candidates

    def _merge_candidate_details(self, target: ImpactCandidate, source: ImpactCandidate) -> None:
        details = target.details
        matched_nodeids = list(details.get("matched_nodeids", []) or [])
        matched_case_ids = list(details.get("matched_case_ids", []) or [])
        if source.related_nodeid:
            matched_nodeids.append(source.related_nodeid)
        if source.related_case_id:
            matched_case_ids.append(source.related_case_id)
        matched_nodeids.extend(source.details.get("matched_nodeids", []) or [])
        matched_case_ids.extend(source.details.get("matched_case_ids", []) or [])
        details["matched_nodeids"] = sorted(dict.fromkeys(nodeid for nodeid in matched_nodeids if nodeid))
        details["matched_case_ids"] = sorted(dict.fromkeys(case_id for case_id in matched_case_ids if case_id))
        nodeid_case_ids = dict(details.get("nodeid_case_ids", {}) or {})
        nodeid_case_ids.update(source.details.get("nodeid_case_ids", {}) or {})
        if source.related_nodeid and source.related_case_id:
            nodeid_case_ids[source.related_nodeid] = source.related_case_id
        details["nodeid_case_ids"] = nodeid_case_ids

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
            details={**dict(candidate.details or {}), "source_group": candidate.source_group},
        )

        if not executable_path or not executable_path.exists():
            record.summary = "候选脚本不存在，无法执行影响回归"
            record.category = AttributionCategory.UNCERTAIN.value
            record.next_action = "人工确认是否需要补齐脚本或跳过该候选"
            record.reason = "未找到可执行的 staged/original 脚本"
            return record

        candidate_nodeids = self._candidate_nodeids(candidate)
        executable_nodeids = self._nodeids_for_executable(candidate_nodeids, target_path, executable_path)
        junit_path = self._junit_path(staging_root, candidate)
        command_targets = executable_nodeids or [str(executable_path)]
        command = [self.runtime.python_bin, "-m", "pytest", *command_targets, "-q", "--junitxml", str(junit_path)]
        record.command = command
        env = {"PYTHONPATH": str(self.regression_root)} if self.regression_root.exists() else None
        proc = run_command(command, cwd=self.regression_root if self.regression_root.exists() else staging_root, env=env)

        record.returncode = proc.returncode
        record.stdout_excerpt = self._excerpt(proc.stdout)
        record.stderr_excerpt = self._excerpt(proc.stderr)
        record.summary = self._summary(proc.stdout, proc.stderr, proc.returncode)
        failed_nodeids = self._failed_nodeids(junit_path, executable_nodeids or candidate_nodeids, target_path, executable_path)
        executed_nodeids = candidate_nodeids or executable_nodeids
        passed_nodeids = [nodeid for nodeid in executed_nodeids if nodeid not in set(failed_nodeids)]
        nodeid_case_ids = dict(candidate.details.get("nodeid_case_ids", {}) or {})
        record.details.update(
            {
                "executed_nodeids": executed_nodeids,
                "failed_nodeids": failed_nodeids,
                "passed_nodeids": passed_nodeids,
                "junit_path": str(junit_path),
                "nodeid_case_ids": nodeid_case_ids,
            }
        )
        if len(failed_nodeids) == 1:
            record.related_nodeid = failed_nodeids[0]
            record.related_case_id = nodeid_case_ids.get(failed_nodeids[0], record.related_case_id)
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

    def _candidate_nodeids(self, candidate: ImpactCandidate) -> list[str]:
        nodeids = list(candidate.details.get("matched_nodeids", []) or [])
        if candidate.related_nodeid:
            nodeids.append(candidate.related_nodeid)
        return sorted(dict.fromkeys(str(nodeid) for nodeid in nodeids if nodeid))

    def _nodeids_for_executable(self, nodeids: list[str], original_path: Path, executable_path: Path) -> list[str]:
        if not nodeids:
            return []
        if original_path == executable_path:
            return nodeids
        converted: list[str] = []
        for nodeid in nodeids:
            suffix = nodeid.split("::", 1)[1] if "::" in nodeid else ""
            converted.append(f"{executable_path}::{suffix}" if suffix else str(executable_path))
        return converted

    def _junit_path(self, staging_root: Path, candidate: ImpactCandidate) -> Path:
        junit_root = staging_root / "junit"
        junit_root.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-zA-Z0-9_.-]+", "_", f"{candidate.source_type}_{Path(candidate.target).name}")[:120]
        return junit_root / f"{slug or 'impact'}.xml"

    def _failed_nodeids(
        self,
        junit_path: Path,
        requested_nodeids: list[str],
        original_path: Path,
        executable_path: Path,
    ) -> list[str]:
        if not junit_path.exists():
            return []
        try:
            root = ET.parse(junit_path).getroot()
        except ET.ParseError:
            return []
        failed_names = {
            testcase.attrib.get("name", "")
            for testcase in root.iter("testcase")
            if testcase.find("failure") is not None or testcase.find("error") is not None
        }
        if not failed_names:
            return []
        failed: list[str] = []
        for nodeid in requested_nodeids:
            test_name = nodeid.split("::")[-1]
            base_name = test_name.split("[", 1)[0]
            if test_name in failed_names or base_name in failed_names:
                failed.append(nodeid)
        if executable_path != original_path:
            failed = [
                self._nodeids_for_executable([nodeid], executable_path, original_path)[0]
                for nodeid in failed
            ]
        return sorted(dict.fromkeys(failed))

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
        nodeids: set[str] = set()
        case_ids: set[str] = set()
        execution_units: list[dict[str, Any]] = []
        for record in records:
            path = record.staged_target or record.target
            if not path:
                continue
            candidate_paths.add(path)
            selectors.append({"kind": "path", "value": path})
            record_nodeids = list(record.details.get("executed_nodeids", []) or [])
            nodeids.update(record_nodeids)
            if record.related_nodeid:
                nodeids.add(record.related_nodeid)
            if record.related_case_id:
                case_ids.add(record.related_case_id)
            case_ids.update(record.details.get("nodeid_case_ids", {}).values())
            execution_units.append(
                {
                    "target": record.target,
                    "staged_target": record.staged_target,
                    "source_type": record.source_type,
                    "module": record.module,
                    "site": record.site,
                    "executed_nodeids": record_nodeids,
                    "failed_nodeids": list(record.details.get("failed_nodeids", []) or []),
                    "run_status": record.run_status,
                    "junit_path": record.details.get("junit_path", ""),
                }
            )
        return {
            "module": (packet.get("candidate_modules") or [""])[0],
            "site": packet.get("site", ""),
            "requested_modules": packet.get("requested_modules", packet.get("candidate_modules", [])),
            "requested_sites": packet.get("requested_sites", [packet.get("site", "")] if packet.get("site") else []),
            "feature_name": packet.get("feature_name", ""),
            "candidate_paths": sorted(candidate_paths),
            "selectors": selectors,
            "execution_units": execution_units,
            "nodeids": sorted(nodeid for nodeid in nodeids if nodeid),
            "case_ids": sorted(case_id for case_id in case_ids if case_id),
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
