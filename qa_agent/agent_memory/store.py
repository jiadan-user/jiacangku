from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qa_agent.agent_memory.models import (
    MEMORY_TYPES,
    MemoryCandidate,
    MemoryRecord,
    candidate_from_data,
    local_now_iso,
    record_from_data,
    to_data,
)
from qa_agent.agent_memory.redactor import redact_text
from qa_agent.io import read_text, write_text, write_yaml


MEMORY_FILES = {
    "correction": "corrections.jsonl",
    "decision": "decisions.jsonl",
    "preference": "preferences.jsonl",
    "lesson": "lessons.jsonl",
    "summary": "summaries.jsonl",
}

DEFAULT_MEMORY_MD = """# Agent Memory

本文件只放最高优先级、长期稳定的协作提醒。

- 记忆只作为提醒，不能绕过当前项目的流程门禁。
- 正式写入长期记忆前，需要用户明确确认或批量确认。
"""

DEFAULT_CONFIG = {
    "version": 1,
    "read_limit": 8,
    "write_policy": "candidate_then_confirm",
    "redaction": {
        "enabled": True,
        "hide_url_query": True,
        "hide_secret_values": True,
    },
}


class MemoryStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.memories_dir = self.root / "memories"
        self.pending_dir = self.root / "pending"
        self.exports_dir = self.root / "exports"
        self.logs_dir = self.root / "logs"

    @property
    def memory_md_path(self) -> Path:
        return self.root / "MEMORY.md"

    @property
    def config_path(self) -> Path:
        return self.root / "config.yaml"

    @property
    def index_path(self) -> Path:
        return self.root / "index.jsonl"

    @property
    def candidates_path(self) -> Path:
        return self.pending_dir / "candidates.jsonl"

    @property
    def events_path(self) -> Path:
        return self.logs_dir / "memory_events.jsonl"

    def exists(self) -> bool:
        return self.root.exists()

    def init(self) -> None:
        self.memories_dir.mkdir(parents=True, exist_ok=True)
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        created_any = False
        if not self.memory_md_path.exists():
            write_text(self.memory_md_path, DEFAULT_MEMORY_MD)
            created_any = True
        if not self.config_path.exists():
            write_yaml(self.config_path, DEFAULT_CONFIG)
            created_any = True
        for file_name in MEMORY_FILES.values():
            target = self.memories_dir / file_name
            if not target.exists():
                target.touch()
                created_any = True
        for target in (self.candidates_path, self.index_path, self.events_path):
            if not target.exists():
                target.touch()
                created_any = True
        if created_any:
            self._append_event("init", {"root": str(self.root)})

    def read_memory_md(self) -> str:
        return read_text(self.memory_md_path)

    def append_candidate(self, candidate: MemoryCandidate | dict[str, Any]) -> MemoryCandidate:
        self.init()
        if isinstance(candidate, dict):
            candidate = MemoryCandidate(**candidate)
        candidate.content = redact_text(candidate.content)
        candidate.title = redact_text(candidate.title)
        candidate.updated_at = local_now_iso()
        self._mark_conflicts(candidate)
        self._append_jsonl(self.candidates_path, to_data(candidate))
        self._append_event("candidate_created", {"id": candidate.id, "type": candidate.type})
        return candidate

    def promote(self, candidate_id: str) -> MemoryRecord:
        self.init()
        candidates = self.list_candidates(include_non_pending=True)
        target: MemoryCandidate | None = None
        for candidate in candidates:
            if candidate.id == candidate_id:
                target = candidate
                break
        if target is None:
            raise ValueError(f"未找到候选记忆: {candidate_id}")
        if target.status == "rejected":
            raise ValueError(f"候选记忆已拒绝，不能 promote: {candidate_id}")

        now = local_now_iso()
        record = MemoryRecord(
            id=target.id.replace("cand_", "mem_", 1),
            type=target.type,
            title=target.title,
            content=redact_text(target.content),
            scope=target.scope,
            tags=target.tags,
            priority=target.priority,
            confidence="confirmed",
            status="active",
            source=target.source,
            created_at=target.created_at,
            updated_at=now,
        )
        self._append_jsonl(self._memory_file(record.type), to_data(record))
        self._update_candidate_status(candidate_id, "promoted")
        self.rebuild_index()
        self._append_event("candidate_promoted", {"candidate_id": candidate_id, "memory_id": record.id})
        return record

    def reject(self, candidate_id: str) -> MemoryCandidate:
        self.init()
        candidate = self._update_candidate_status(candidate_id, "rejected")
        self._append_event("candidate_rejected", {"candidate_id": candidate_id})
        return candidate

    def list_candidates(self, *, include_non_pending: bool = False) -> list[MemoryCandidate]:
        candidates = [candidate_from_data(item) for item in self._read_jsonl(self.candidates_path)]
        if include_non_pending:
            return candidates
        return [candidate for candidate in candidates if candidate.status == "pending"]

    def list_memories(self, *, active_only: bool = True) -> list[MemoryRecord]:
        memories: list[MemoryRecord] = []
        for memory_type in sorted(MEMORY_TYPES):
            for item in self._read_jsonl(self._memory_file(memory_type)):
                record = record_from_data(item)
                if active_only and record.status != "active":
                    continue
                memories.append(record)
        return memories

    def list_indexed_memories(self) -> list[MemoryRecord]:
        records = [record_from_data(item) for item in self._read_jsonl(self.index_path)]
        return [record for record in records if record.status == "active"]

    def rebuild_index(self) -> None:
        self.init()
        records = [to_data(record) for record in self.list_memories(active_only=True)]
        write_text(self.index_path, "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records))

    def log_event(self, event_type: str, details: dict[str, Any]) -> None:
        self._append_event(event_type, details)

    def _memory_file(self, memory_type: str) -> Path:
        file_name = MEMORY_FILES.get(memory_type, MEMORY_FILES["correction"])
        return self.memories_dir / file_name

    def _update_candidate_status(self, candidate_id: str, status: str) -> MemoryCandidate:
        candidates = self.list_candidates(include_non_pending=True)
        updated: MemoryCandidate | None = None
        for candidate in candidates:
            if candidate.id == candidate_id:
                candidate.status = status
                candidate.updated_at = local_now_iso()
                updated = candidate
                break
        if updated is None:
            raise ValueError(f"未找到候选记忆: {candidate_id}")
        write_text(
            self.candidates_path,
            "".join(json.dumps(to_data(candidate), ensure_ascii=False) + "\n" for candidate in candidates),
        )
        return updated

    def _mark_conflicts(self, candidate: MemoryCandidate) -> None:
        conflict_ids: list[str] = []
        candidate_terms = _polarity_terms(candidate.content)
        if not candidate_terms:
            return
        candidate_scope = set(candidate.scope)
        for memory in self.list_memories(active_only=True):
            if candidate_scope and memory.scope and not candidate_scope.intersection(memory.scope):
                continue
            memory_terms = _polarity_terms(memory.content)
            if _looks_conflicting(candidate_terms, memory_terms):
                conflict_ids.append(memory.id)
        if conflict_ids:
            candidate.conflict_ids = conflict_ids
            candidate.risk = "high"
            candidate.suggested_action = "review"

    def _append_event(self, event_type: str, details: dict[str, Any]) -> None:
        if not self.logs_dir.exists():
            return
        payload = {"event": event_type, "created_at": local_now_iso(), "details": details}
        self._append_jsonl(self.events_path, payload)

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                rows.append(item)
        return rows

    def _append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _polarity_terms(content: str) -> set[str]:
    text = content.lower()
    terms: set[str] = set()
    if "自动判断" in text or "auto" in text:
        terms.add("auto_decision")
    if any(token in text for token in ["不要", "不应", "不能", "禁止", "必须用户选择", "用户选择"]):
        terms.add("negative")
    if any(token in text for token in ["可以", "允许", "自动", "直接"]):
        terms.add("positive")
    return terms


def _looks_conflicting(left: set[str], right: set[str]) -> bool:
    if "auto_decision" not in left or "auto_decision" not in right:
        return False
    return ("negative" in left and "positive" in right) or ("positive" in left and "negative" in right)
