from __future__ import annotations

import re
from pathlib import Path

from qa_agent.agent_memory.models import MemoryRecord, MemorySearchResult
from qa_agent.agent_memory.store import MemoryStore


PRIORITY_SCORE = {
    "pinned": 30,
    "high": 20,
    "medium": 10,
    "low": 0,
}


class MemoryRetriever:
    def __init__(self, root: str | Path) -> None:
        self.store = MemoryStore(root)

    def search(
        self,
        query: str,
        *,
        scopes: list[str] | None = None,
        limit: int = 8,
    ) -> list[MemorySearchResult]:
        memories = self.store.list_indexed_memories() or self.store.list_memories(active_only=True)
        terms = _extract_terms(query)
        requested_scopes = set(scopes or [])
        results: list[MemorySearchResult] = []
        for memory in memories:
            score, reasons = self._score(memory, terms, requested_scopes)
            if score <= 0:
                continue
            results.append(MemorySearchResult(memory=memory, score=score, reasons=reasons))
        results.sort(
            key=lambda item: (
                item.score,
                PRIORITY_SCORE.get(item.memory.priority, 0),
                item.memory.updated_at,
                item.memory.use_count,
            ),
            reverse=True,
        )
        return results[:limit]

    def pinned(self) -> list[MemoryRecord]:
        return [
            memory
            for memory in self.store.list_memories(active_only=True)
            if memory.priority == "pinned"
        ]

    def _score(self, memory: MemoryRecord, terms: set[str], scopes: set[str]) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []
        memory_scopes = {item.lower() for item in memory.scope}
        memory_tags = {item.lower() for item in memory.tags}
        title = memory.title.lower()
        content = memory.content.lower()

        if scopes and scopes.intersection(memory_scopes):
            score += 5
            reasons.append("scope")
        elif scopes and not scopes.intersection(memory_scopes):
            score -= 1

        for term in terms:
            if term in memory_scopes:
                score += 5
                reasons.append(f"scope:{term}")
            if term in memory_tags:
                score += 4
                reasons.append(f"tag:{term}")
            if term and term in title:
                score += 3
                reasons.append(f"title:{term}")
            if term and term in content:
                score += 2
                reasons.append(f"content:{term}")

        if memory.priority == "pinned":
            score += 3
            reasons.append("priority:pinned")
        elif memory.priority == "high":
            score += 2
            reasons.append("priority:high")
        if memory.status != "active":
            score -= 2
            reasons.append("status:not-active")
        return score, _dedupe(reasons)


def _extract_terms(query: str) -> set[str]:
    lowered = (query or "").lower()
    terms: set[str] = set()
    for match in re.finditer(r"[a-z0-9_+-]+|[\u4e00-\u9fff]+", lowered):
        token = match.group(0).strip()
        if not token:
            continue
        terms.add(token)
        if _is_cjk(token):
            terms.update(_cjk_shingles(token))
    return terms


def _is_cjk(token: str) -> bool:
    return all("\u4e00" <= char <= "\u9fff" for char in token)


def _cjk_shingles(token: str) -> set[str]:
    if len(token) <= 2:
        return {token}
    return {token[index : index + 2] for index in range(len(token) - 1)}


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
