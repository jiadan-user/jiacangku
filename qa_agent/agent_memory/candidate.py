from __future__ import annotations

import re

from qa_agent.agent_memory.models import MemoryCandidate, MemorySource


def build_candidate_from_text(
    text: str,
    *,
    memory_type: str = "correction",
    scope: list[str] | None = None,
    tags: list[str] | None = None,
    priority: str = "high",
    risk: str = "medium",
    candidate_reason: str = "由用户输入提炼的候选记忆",
    source_kind: str = "user_correction",
    run_id: str | None = None,
) -> MemoryCandidate:
    clean_text = " ".join((text or "").split())
    inferred_scope = scope or infer_scope(clean_text)
    inferred_tags = tags or infer_tags(clean_text, inferred_scope)
    return MemoryCandidate(
        type=memory_type,
        title=_make_title(clean_text),
        content=clean_text,
        scope=inferred_scope,
        tags=inferred_tags,
        priority=priority,
        confidence="candidate",
        status="pending",
        source=MemorySource(kind=source_kind, run_id=run_id),
        candidate_reason=candidate_reason,
        suggested_action="promote",
        risk=risk,
    )


def infer_scope(text: str) -> list[str]:
    lowered = text.lower()
    scopes: list[str] = []
    patterns = {
        "qa_agent": ["qa agent", "qa_agent", "qa-agent"],
        "legacy_update": ["旧脚本", "legacy", "update"],
        "mode_selection": ["模式", "change_mode", "变更模式"],
        "skill": ["skill", "creator-skill"],
        "knowledge_base": ["knowledge", "知识库"],
        "ok_autotest_ui": ["ok_autotest", "ok skill", "回归"],
    }
    for scope, keywords in patterns.items():
        if any(keyword in lowered for keyword in keywords):
            scopes.append(scope)
    return scopes or ["general"]


def infer_tags(text: str, scopes: list[str]) -> list[str]:
    tags = list(scopes)
    lowered = text.lower()
    if any(token in lowered for token in ["不要", "不能", "不应", "必须", "纠正"]):
        tags.append("user-correction")
    if "流程" in lowered or "workflow" in lowered:
        tags.append("workflow")
    if "偏好" in lowered or "风格" in lowered:
        tags.append("preference")
    return tags


def _make_title(text: str) -> str:
    if not text:
        return "未命名候选记忆"
    sentence = re.split(r"[。.!！?\n]", text, maxsplit=1)[0].strip()
    if len(sentence) <= 36:
        return sentence
    return sentence[:34].rstrip() + "..."
