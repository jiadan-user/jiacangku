from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qa_agent.io import read_yaml


@dataclass
class AppConfig:
    project_root: Path
    skills: dict[str, Any]
    thresholds: dict[str, Any]
    knowledge_base_routing: dict[str, Any]

    @property
    def qa_state_root(self) -> Path:
        return self.project_root / ".qa_agent"


def _resolve_nested_paths(value: Any, project_root: Path) -> Any:
    if isinstance(value, dict):
        return {key: _resolve_nested_paths(item, project_root) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_nested_paths(item, project_root) for item in value]
    if isinstance(value, str):
        if value.startswith("/") or "://" in value:
            return value
        if "/" in value or value.startswith("."):
            return str((project_root / value).resolve())
    return value


def load_config(project_root: str | Path) -> AppConfig:
    root = Path(project_root).resolve()
    skills = read_yaml(root / "config" / "skills.yaml", default={}) or {}
    thresholds = read_yaml(root / "config" / "thresholds.yaml", default={}) or {}
    knowledge_base_routing = read_yaml(root / "config" / "knowledge_base_routing.yaml", default={}) or {}
    skills = _resolve_nested_paths(skills, root)
    knowledge_base_routing = _resolve_nested_paths(knowledge_base_routing, root)
    return AppConfig(
        project_root=root,
        skills=skills,
        thresholds=thresholds,
        knowledge_base_routing=knowledge_base_routing,
    )
