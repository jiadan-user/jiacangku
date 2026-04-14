from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_text(path: str | Path) -> str:
    if not path or str(path).strip() == "":
        return ""
    target = Path(path)
    if not target.exists() or target.is_dir():
        return ""
    return target.read_text(encoding="utf-8")


def write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    ensure_parent(target)
    target.write_text(content, encoding="utf-8")


def read_json(path: str | Path, default: Any | None = None) -> Any:
    if not path or str(path).strip() == "":
        return default
    target = Path(path)
    if not target.exists() or target.is_dir():
        return default
    return json.loads(target.read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    ensure_parent(target)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_yaml(path: str | Path, default: Any | None = None) -> Any:
    target = Path(path)
    if not target.exists():
        return default
    with target.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    return default if loaded is None else loaded


def write_yaml(path: str | Path, data: Any) -> None:
    target = Path(path)
    ensure_parent(target)
    with target.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, allow_unicode=True, sort_keys=False)
