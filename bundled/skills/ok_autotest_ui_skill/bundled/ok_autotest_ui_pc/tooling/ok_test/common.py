from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
ROOT_REPORTS_DIR = ROOT_DIR / "reports"
CATALOG_DIR = ROOT_DIR / "catalog"
REPORTS_DIR = ROOT_REPORTS_DIR / "ok_test_runs"
GENERATED_CATALOG_PATH = CATALOG_DIR / "catalog.generated.json"
OVERRIDES_PATH = CATALOG_DIR / "catalog.overrides.yaml"
SCENARIO_INVENTORY_PATH = CATALOG_DIR / "scenario_inventory.yaml"
IDENTIFIER_AUDIT_JSON_PATH = CATALOG_DIR / "identifier_audit.json"
IDENTIFIER_AUDIT_MD_PATH = CATALOG_DIR / "identifier_audit.md"
PREREQUISITES_PATH = CATALOG_DIR / "prerequisites.yaml"
ALLURE_SERVER_INFO_PATH = ROOT_REPORTS_DIR / "allure_server.json"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_skill_root() -> Path | None:
    bundled_parent = ROOT_DIR.parent
    if bundled_parent.name == "bundled":
        candidate = bundled_parent.parent
        if (candidate / "SKILL.md").exists():
            return candidate

    candidate = ROOT_DIR / "ok-ui-autotest"
    if (candidate / "SKILL.md").exists():
        return candidate
    return None


def default_coverage_dashboard_path() -> Path:
    skill_root = resolve_skill_root()
    if skill_root is not None:
        return skill_root / "references" / "coverage-dashboard.md"
    return CATALOG_DIR / "coverage-dashboard.md"


def default_dashboard_modules_dir() -> Path:
    skill_root = resolve_skill_root()
    if skill_root is not None:
        return skill_root / "references" / "dashboard-modules"
    return CATALOG_DIR / "dashboard-modules"


def utcnow_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def slugify(value: str | None) -> str:
    if not value:
        return ""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return re.sub(r"_+", "_", normalized)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping: {path}")
    return data


def save_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")


def save_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return data


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def short_hash(parts: list[str]) -> str:
    digest = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()
    return digest[:8]


def create_run_id(nodeids: list[str]) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{short_hash(nodeids or [timestamp])}"


def bool_from_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_env_value(value: str) -> Any:
    try:
        return yaml.safe_load(value)
    except yaml.YAMLError:
        return value


def resolve_pytest_command() -> tuple[list[str], str]:
    override = os.getenv("OK_TEST_PYTEST_BIN")
    if override:
        return [override], override

    local = ROOT_DIR / "venv" / "bin" / "pytest"
    if local.exists():
        return [str(local)], str(local)

    return [sys.executable, "-m", "pytest"], f"{sys.executable} -m pytest"


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)
