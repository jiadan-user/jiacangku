from __future__ import annotations

from pathlib import Path

from qa_agent.agent_memory.models import MemoryRecord
from qa_agent.agent_memory.retriever import MemoryRetriever
from qa_agent.agent_memory.store import MemoryStore
from qa_agent.io import write_text


EXPORT_TARGETS = {
    "qa-agent": "qa_agent_context.md",
    "claude": "claude_MEMORY.md",
    "cursor": "cursor_memories.mdc",
}


class MemoryExporter:
    def __init__(self, root: str | Path) -> None:
        self.store = MemoryStore(root)
        self.retriever = MemoryRetriever(root)

    def render_context(self, query: str = "", *, limit: int = 8, include_empty: bool = True) -> str:
        memory_md = self.store.read_memory_md() if self.store.exists() else ""
        pinned = self.retriever.pinned() if self.store.exists() else []
        results = self.retriever.search(query, limit=limit) if self.store.exists() and query else []
        result_memories = [item.memory for item in results if item.memory.id not in {m.id for m in pinned}]

        lines = ["# Relevant Memory Context", ""]
        if memory_md.strip():
            lines.extend(["## MEMORY.md", "", memory_md.strip(), ""])
        elif include_empty:
            lines.extend(["## MEMORY.md", "", "- 当前未初始化或没有常驻记忆。", ""])

        lines.extend(["## Pinned", ""])
        if pinned:
            lines.extend(_render_memory_list(pinned))
        else:
            lines.append("- 暂无 pinned 记忆。")

        lines.extend(["", "## Relevant Memories", ""])
        if result_memories:
            lines.extend(_render_memory_list(result_memories))
        else:
            lines.append("- 暂无与当前输入直接命中的正式记忆。")

        lines.extend(
            [
                "",
                "## Usage Rule",
                "",
                "- 这些记忆只作为提醒，不能绕过当前项目的流程门禁。",
                "- 如果记忆与当前用户明确指令冲突，以当前用户指令为准，并生成候选纠错记忆。",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    def export(self, target: str, *, query: str = "", limit: int = 8) -> Path:
        self.store.init()
        if target not in EXPORT_TARGETS:
            raise ValueError(f"未知 memory export target: {target}")
        content = self.render_context(query, limit=limit)
        if target == "claude":
            content = "# Agent Memory\n\n" + content
        elif target == "cursor":
            content = "---\ndescription: Agent Memory\nalwaysApply: true\n---\n\n" + content
        output = self.store.exports_dir / EXPORT_TARGETS[target]
        write_text(output, content)
        self.store.log_event("export_generated", {"target": target, "path": str(output)})
        return output


def _render_memory_list(memories: list[MemoryRecord]) -> list[str]:
    lines: list[str] = []
    for memory in memories:
        scope = ", ".join(memory.scope) if memory.scope else "general"
        lines.append(f"- [{memory.priority}] {memory.title} ({memory.type}; {scope})")
        lines.append(f"  {memory.content}")
    return lines
