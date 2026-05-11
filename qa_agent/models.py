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
    IMPACT_ANALYSIS = "影响分析与重叠裁决"
    IMPACT_VERIFICATION = "影响回归与变更归因"
    LEGACY_UPDATE = "旧脚本更新执行"
    OK_UI_REGRESSION = "ok_autotest_ui_skill"
    FINAL_REPORT = "最终报告"
    KNOWLEDGE_BASE_UPDATE = "knowledge_base_update"


class PhaseStatus(str, Enum):
    PENDING = "待执行"
    RUNNING = "执行中"
    COMPLETED = "已完成"
    BLOCKED = "已阻塞"
    SKIPPED = "已跳过"
    ERROR = "执行出错"


class RunStatus(str, Enum):
    PLANNED = "已计划"
    RUNNING = "执行中"
    BLOCKED = "已阻塞"
    COMPLETED = "已完成"
    ERROR = "执行出错"


class CaseStatus(str, Enum):
    NEW_CANDIDATE = "new-candidate"
    EXISTING_AUTOMATED = "existing-automated"
    REGEN_REQUIRED = "regen-required"
    NON_AUTOMATABLE = "non-automatable"


class ImpactRunStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AttributionCategory(str, Enum):
    PASSED = "passed"
    LATEST_CHANGE = "likely_caused_by_latest_change"
    PREEXISTING = "likely_preexisting_or_unrelated"
    ENVIRONMENT = "environment_or_data_issue"
    UNCERTAIN = "uncertain"


class LegacyUpdateTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    RETRY = "retry"
    COMPLETED = "completed"
    MANUAL_REVIEW = "manual-review"


class PlaywrightOutcomeType(str, Enum):
    SCRIPT_GENERATED = "script_generated"
    SCRIPT_BLOCKED = "script_blocked"
    BUG_RECORDED = "bug_recorded"
    MANUAL_REVIEW = "manual_review"


class PlaywrightRecordingOutcomeType(str, Enum):
    RECORDING_PASSED = "recording_passed"
    BUG_RECORDED = "bug_recorded"


class NextActionKind(str, Enum):
    RUN_SKILL = "run_skill"
    CONFIRM_PHASE = "confirm_phase"
    CONTINUE_AUTO = "continue_auto"
    MANUAL_REVIEW = "manual_review"
    FIX_ENVIRONMENT = "fix_environment"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class NextAction:
    kind: str = ""
    phase: str = ""
    summary: str = ""
    skill_path: str = ""
    instruction_path: str = ""
    required_artifacts: list[str] = field(default_factory=list)
    resume_command: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class DoctorCheck:
    name: str
    ok: bool
    severity: str = "warning"
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class DoctorResult:
    ok: bool
    has_fatal: bool = False
    checks: list[DoctorCheck] = field(default_factory=list)

    @property
    def warnings(self) -> list[DoctorCheck]:
        return [check for check in self.checks if not check.ok and check.severity == "warning"]

    @property
    def fatals(self) -> list[DoctorCheck]:
        return [check for check in self.checks if not check.ok and check.severity == "fatal"]


@dataclass
class RequirementPacket:
    change_mode: str
    figma_url: str = ""
    prd_refs: list[str] = field(default_factory=list)
    candidate_modules: list[str] = field(default_factory=list)
    site: str = ""
    requested_modules: list[str] = field(default_factory=list)
    requested_sites: list[str] = field(default_factory=list)
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
    phase_timings: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    blocked_since: str = ""
    next_action: NextAction = field(default_factory=NextAction)
    error_reason: str = ""
    version: int = 0

    def __post_init__(self) -> None:
        if not self.next_action:
            self.next_action = NextAction()
        elif isinstance(self.next_action, dict):
            self.next_action = NextAction(**self.next_action)
        if not isinstance(self.phase_timings, dict):
            self.phase_timings = {}

    def touch(self) -> None:
        self.updated_at = utc_now_iso()


@dataclass
class TextCaseManifestEntry:
    tc_id: str
    title: str
    priority: str
    test_type: str
    ui_automatable: bool
    ui_automation_label: str = ""
    preconditions: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    expected_results: list[str] = field(default_factory=list)
    source_doc: str = ""


@dataclass
class TextCaseManifest:
    module: str
    site: str
    feature_name: str
    source_doc: str
    kb_text_case_draft_path: str
    environment: dict[str, str] = field(default_factory=dict)
    cases: list[TextCaseManifestEntry] = field(default_factory=list)
    business_attributes: list[str] = field(default_factory=list)
    test_scope: list[str] = field(default_factory=list)
    rule_library_paths: list[str] = field(default_factory=list)


@dataclass
class PlaywrightCaseOutcome:
    tc_id: str
    outcome: str
    script_path: str = ""
    bug_report_path: str = ""
    script_blocker_report_path: str = ""
    manual_review_reason: str = ""
    collect_only_passed: bool = False
    pytest_passed: bool = False
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaywrightRecordingOutcome:
    tc_id: str
    outcome: str
    proof_artifact_path: str = ""
    bug_report_path: str = ""
    manual_review_reason: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseGateResult:
    phase: str
    ok: bool
    summary: str = ""
    blocking_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class UserConfirmationRecord:
    phase: str
    confirmed_at: str = field(default_factory=utc_now_iso)
    summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)


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
    source_group: str = ""
    selector_hint: str = ""
    reason: str = ""
    related_case_id: str = ""
    related_nodeid: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactVerificationRecord:
    source_type: str
    target: str
    staged_target: str = ""
    module: str = ""
    site: str = ""
    feature_key: str = ""
    related_case_id: str = ""
    related_nodeid: str = ""
    run_status: str = ImpactRunStatus.SKIPPED.value
    command: list[str] = field(default_factory=list)
    returncode: int | None = None
    summary: str = ""
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""
    category: str = AttributionCategory.UNCERTAIN.value
    reason: str = ""
    next_action: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactVerificationOutcome:
    selector_plan: dict[str, Any]
    records: list[ImpactVerificationRecord] = field(default_factory=list)


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
