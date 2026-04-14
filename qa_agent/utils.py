from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Sequence


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", lowered)
    slug = slug.strip("_")
    if not slug:
        return "unnamed"
    if not re.search(r"[a-z0-9]", slug):
        ascii_fallback = re.sub(r"[^a-z0-9]+", "_", _cjk_to_ascii(lowered)).strip("_")
        return ascii_fallback or slug
    return slug


def _cjk_to_ascii(text: str) -> str:
    """Best-effort CJK to ascii: keep existing ascii, map common chars, drop the rest."""
    _COMMON = {
        "填": "fill", "写": "write", "完": "done", "整": "full", "偏": "pref",
        "好": "ok", "保": "save", "存": "save", "成": "ok", "功": "ok",
        "修": "edit", "改": "edit", "已": "exist", "有": "has",
        "薪": "salary", "资": "salary", "最": "limit", "低": "min", "高": "max",
        "大": "gt", "于": "than", "时": "when", "提": "submit", "交": "submit",
        "报": "error", "错": "error", "必": "required", "字": "field", "段": "field",
        "空": "empty", "为": "is", "输": "input", "入": "input",
        "边": "boundary", "界": "boundary", "值": "value", "负": "neg", "数": "num",
        "被": "be", "拒": "reject", "绝": "reject",
        "未": "un", "登": "login", "录": "login", "用": "user", "户": "user",
        "访": "visit", "问": "visit", "页": "page", "面": "page",
        "重": "re", "定": "direct", "向": "direct",
    }
    parts: list[str] = []
    for char in text:
        if re.match(r"[a-z0-9]", char):
            parts.append(char)
        elif char in _COMMON:
            parts.append(_COMMON[char])
        else:
            parts.append("_")
    return "_".join(parts)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def run_command(
    command: Sequence[str],
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        env=env,
        check=check,
        text=True,
        capture_output=True,
    )


def read_if_exists(path: str | Path) -> str:
    if not path or str(path).strip() == "":
        return ""
    target = Path(path)
    if not target.exists() or target.is_dir():
        return ""
    return target.read_text(encoding="utf-8")
