from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChangeMode(str, Enum):
    NEW_FEATURE = "新需求"
    REGRESSION = "纯回归"
    MIXED = "混合"


class Phase(str, Enum):
    INTAKE = "需求接入"
    IMPACT_SPLIT = "影响拆分"
    SENIOR_QA_BRAIN = "senior-qa-brain"
    PLAYWRIGHT_GENERATOR = "playwright-test-generator"
    BRIDGE = "衔接（查重+守卫+入库）"
    IMPACT_ANALYSIS = "影响分析与重叠裁决"
    LEGACY_UPDATE = "旧脚本更新执行"
    OK_UI_REGRESSION = "ok_autotest_ui_skill"
    FINAL_REPORT = "最终报告"


class PhaseStatus(str, Enum):
    PENDING = "待执行"
    RUNNING = "执行中"
    COMPLETED = "已完成"
    BLOCKED = "已阻塞"
    SKIPPED = "已跳过"


class RunStatus(str, Enum):
    PLANNED = "已计划"
    RUNNING = "执行中"
    BLOCKED = "已阻塞"
    COMPLETED = "已完成"


class CaseStatus(str, Enum):
    NEW_CANDIDATE = "new-candidate"
    EXISTING_AUTOMATED = "existing-automated"
    REGEN_REQUIRED = "regen-required"
    NON_AUTOMATABLE = "non-automatable"


class LegacyUpdateTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    RETRY = "retry"
    COMPLETED = "completed"
    MANUAL_REVIEW = "manual-review"


@dataclass
class RequirementPacket:
    change_mode: str
    figma_url: str = ""
    prd_refs: list[str] = field(default_factory=list)
    candidate_modules: list[str] = field(default_factory=list)
    site: str = ""
    feature_name: str = ""
    change_description: str = ""
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class RunState:
    run_id: str
    status: str
    current_phase: str
    change_mode: str = ChangeMode.NEW_FEATURE.value
    blocked_reason: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    phase_statuses: dict[str, str] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def touch(self) -> None:
        self.updated_at = utc_now_iso()


@dataclass
class CaseManifestEntry:
    tc_id: str
    title: str
    module: str
    site: str
    feature_key: str
    source_doc: str
    priority: str
    test_type: str
    ui_automatable: bool
    generated_case_id: str
    status: str
    group: str = ""
    target_script_path: str = ""
    duplicate_of: str = ""
    rationale: str = ""


@dataclass
class ValidationResult:
    ok: bool
    name: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactCandidate:
    source_type: str
    target: str
    module: str = ""
    site: str = ""
    feature_key: str = ""
    selector_hint: str = ""
    reason: str = ""
    related_case_id: str = ""
    related_nodeid: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class OverlapDecision:
    new_target: str
    existing_target: str
    decision: str
    reason: str = ""
    related_case_id: str = ""
    related_nodeid: str = ""


@dataclass
class LegacyUpdateTask:
    task_id: str
    target_script: str
    target_case_id: str = ""
    target_nodeid: str = ""
    impact_type: str = "coverage_overlap"
    recommended_action: str = "manual-review"
    status: str = LegacyUpdateTaskStatus.PENDING.value
    reason: str = ""
    blocking: bool = True
    attempts: int = 0
    max_attempts: int = 3
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class LegacyUpdateGate:
    round_index: int = 0
    total_count: int = 0
    pending_count: int = 0
    retry_count: int = 0
    completed_count: int = 0
    manual_review_count: int = 0
    all_completed: bool = False
    has_manual_review: bool = False


@dataclass
class LegacyUpdateRoundOutcome:
    tasks: list[LegacyUpdateTask]
    gate: LegacyUpdateGate
    results: list[dict[str, Any]] = field(default_factory=list)


def to_data(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [to_data(item) for item in value]
    if isinstance(value, dict):
        return {key: to_data(item) for key, item in value.items()}
    return value
