from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChangeMode(str, Enum):
    REGRESSION_ONLY = "仅回归"
    NEW_FEATURE_ONLY = "仅新需求"
    MIXED = "混合"


class PhaseStatus(str, Enum):
    PENDING = "待执行"
    RUNNING = "执行中"
    COMPLETED = "已完成"
    BLOCKED = "已阻塞"
    FAILED = "失败"
    SKIPPED = "已跳过"


class RunStatus(str, Enum):
    PLANNED = "已计划"
    RUNNING = "执行中"
    BLOCKED = "已阻塞"
    FAILED = "失败"
    COMPLETED = "已完成"


class CaseStatus(str, Enum):
    EXISTING_AUTOMATED = "已有自动化"
    NEW_CANDIDATE = "新增候选"
    REGEN_REQUIRED = "需要重生成"
    NON_AUTOMATABLE = "不可自动化"
    BLOCKED_BY_BUG = "阻塞于缺陷"
    GENERATED_VERIFIED = "已生成并验证"
    PROMOTED = "已提升"


class ConductorPhase(str, Enum):
    INTAKE = "需求接入"
    IMPACT_SPLIT = "影响拆分"
    ANALYSIS_BUNDLE = "分析资料包"
    ANALYSIS_REVIEW = "分析确认"
    TESTCASE_GEN = "原始用例生成"
    UI_PROBE_ENRICH = "UI探测增强"
    DEDUPE_MAP = "查重映射"
    BATCH_PLAN = "批次规划"
    READINESS_GATE = "录制准备检查"
    PROOF_INGEST = "证明产物导入"
    CODEGEN = "脚本草稿生成"
    NORMALIZE = "脚本规范化"
    PROMOTION_GUARD = "提升守卫"
    PROMOTE = "回归池提升"
    REGRESSION_PLAN = "回归计划"
    REGRESSION_DRY_RUN = "回归预演"
    REGRESSION_RUN = "回归执行"
    VISUAL_GATE = "视觉门禁"
    UI_GATE = "UI门禁"
    API_GATE = "API门禁"
    FINAL_REPORT = "最终报告"


@dataclass
class RequirementPacket:
    change_mode: str
    figma_url: str
    prd_refs: list[str] = field(default_factory=list)
    git_diff_summary: str = ""
    candidate_modules: list[str] = field(default_factory=list)
    site: str = ""
    feature_name: str = ""
    risk_hints: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class MarkdownCase:
    tc_id: str
    title: str
    priority: str = "P1"
    test_type: str = ""
    ui_automatable: bool = True
    group: str = ""
    preconditions: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    expected: list[str] = field(default_factory=list)


@dataclass
class MarkdownDocument:
    title: str
    env_config: dict[str, Any]
    cases: list[MarkdownCase]
    raw_text: str
    path: str = ""


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
class ProofArtifact:
    tc_id: str
    batch_id: str
    refs: list[str] = field(default_factory=list)
    cli_js_code: list[str] = field(default_factory=list)
    dynamic_discoveries: list[str] = field(default_factory=list)
    verification_points: list[str] = field(default_factory=list)
    cli_stats: dict[str, int] = field(default_factory=dict)
    screenshots: list[str] = field(default_factory=list)
    source_path: str = ""


@dataclass
class ValidationResult:
    ok: bool
    name: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class GateReport:
    visual_scores: list[dict[str, Any]] = field(default_factory=list)
    ui_pass_rate: float | None = None
    api_pass_rate: float | None = None
    failed_checks: list[str] = field(default_factory=list)
    bug_report_paths: list[str] = field(default_factory=list)
    release_recommendation: str = "暂缓上线"


@dataclass
class RunState:
    run_id: str
    status: str
    current_phase: str
    change_mode: str = ChangeMode.NEW_FEATURE_ONLY.value
    blocked_reason: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    phase_statuses: dict[str, str] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def touch(self) -> None:
        self.updated_at = utc_now_iso()


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
