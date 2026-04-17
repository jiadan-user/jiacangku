from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from typing import Any


MEMORY_TYPES = {"correction", "decision", "preference", "lesson", "summary"}
MEMORY_PRIORITIES = {"pinned", "high", "medium", "low"}
MEMORY_STATUSES = {"pending", "active", "rejected", "archived", "superseded", "promoted"}
MEMORY_RISKS = {"low", "medium", "high"}


def local_now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def memory_id(prefix: str = "mem") -> str:
    return f"{prefix}_{datetime.now().astimezone().strftime('%Y%m%d_%H%M%S_%f')}"


@dataclass
class MemorySource:
    kind: str = "manual"
    run_id: str | None = None
    conversation_ref: str | None = None


@dataclass
class MemoryRecord:
    id: str = ""
    type: str = "correction"
    title: str = ""
    content: str = ""
    scope: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    priority: str = "medium"
    confidence: str = "confirmed"
    status: str = "active"
    source: MemorySource = field(default_factory=MemorySource)
    created_at: str = field(default_factory=local_now_iso)
    updated_at: str = field(default_factory=local_now_iso)
    last_used_at: str | None = None
    use_count: int = 0

    def __post_init__(self) -> None:
        if not self.id:
            self.id = memory_id("mem")
        if self.type not in MEMORY_TYPES:
            self.type = "correction"
        if self.priority not in MEMORY_PRIORITIES:
            self.priority = "medium"
        if self.status not in MEMORY_STATUSES:
            self.status = "active"
        if isinstance(self.source, dict):
            self.source = MemorySource(**self.source)
        self.scope = _clean_list(self.scope)
        self.tags = _clean_list(self.tags)


@dataclass
class MemoryCandidate(MemoryRecord):
    status: str = "pending"
    candidate_reason: str = ""
    suggested_action: str = "promote"
    risk: str = "medium"
    conflict_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = memory_id("cand")
        self.status = self.status or "pending"
        super().__post_init__()
        if not self.id.startswith("cand_"):
            self.id = self.id.replace("mem_", "cand_", 1) if self.id.startswith("mem_") else f"cand_{self.id}"
        if self.risk not in MEMORY_RISKS:
            self.risk = "medium"
        self.conflict_ids = _clean_list(self.conflict_ids)


@dataclass
class MemorySearchResult:
    memory: MemoryRecord
    score: int
    reasons: list[str] = field(default_factory=list)


def to_data(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [to_data(item) for item in value]
    if isinstance(value, dict):
        return {key: to_data(item) for key, item in value.items()}
    return value


def record_from_data(payload: dict[str, Any]) -> MemoryRecord:
    return MemoryRecord(**payload)


def candidate_from_data(payload: dict[str, Any]) -> MemoryCandidate:
    return MemoryCandidate(**payload)


def _clean_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw = [value]
    else:
        raw = list(value)
    seen: set[str] = set()
    cleaned: list[str] = []
    for item in raw:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned
