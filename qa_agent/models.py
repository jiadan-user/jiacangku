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
