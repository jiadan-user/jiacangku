from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PRIORITY_ORDER = ["p0", "p1", "p2", "p3"]
SITE_MARKERS = {"us", "sg", "ae", "au"}
PRIORITY_MARKERS = set(PRIORITY_ORDER)
BASELINE_MARKERS = {"smoke", "core_flow", "validation"}


@dataclass
class CatalogCase:
    nodeid: str
    file_path: str
    test_name: str
    case_id: str | None
    priority: str | None
    site: str | None
    markers: list[str]
    allure_feature: str | None
    allure_story: str | None
    allure_title: str | None
    severity: str | None = None
    module_id: str | None = None
    feature_id: str | None = None
    aliases: list[str] = field(default_factory=list)
    baseline_set: str | None = None
    risk_level: str | None = None
    owner: str | None = None
    governed: bool = False
    skill_excluded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CatalogCase":
        return cls(**payload)


@dataclass
class SelectionCriteria:
    module: str | None = None
    feature: str | None = None
    story: str | None = None
    priority: str | None = None
    site: str | None = None
    case_id: str | None = None
    path: str | None = None
    nodeid: str | None = None
    dry_run: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GovernanceCaseResult:
    nodeid: str
    module_id: str
    feature_id: str
    case_id: str | None
    name: str
    priority: str | None
    governed: bool
    is_baseline: bool
    executed: bool
    passed: bool
    failed: bool
    recommended: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
