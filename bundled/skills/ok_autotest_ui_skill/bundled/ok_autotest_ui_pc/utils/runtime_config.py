from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OVERRIDES_PATH = PROJECT_ROOT / "config" / "runtime_overrides.yaml"


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def module_key_from_path(module_file: str | os.PathLike[str]) -> str:
    path = Path(module_file).resolve()
    relative = path.relative_to(PROJECT_ROOT).as_posix()
    if relative.startswith("test_cases/publish_job/"):
        return "publish_job"
    if relative.startswith("test_cases/car_list/"):
        return "car_list"
    if relative == "test_cases/test_car/test_ae_car_publish.py":
        return "car_publish"
    if relative.startswith("test_cases/"):
        parts = relative.split("/")
        if len(parts) >= 2:
            return parts[1]
    return path.stem


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Runtime config must be a mapping: {path}")
    return data


def _parse_env_value(raw: str) -> Any:
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError:
        return raw


def _env_overrides(module_key: str) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    prefix = "OK_UI__"
    module_prefix = f"{prefix}{module_key.upper()}__"
    for key, value in os.environ.items():
        target = None
        if key.startswith(module_prefix):
            target = key[len(module_prefix):]
        elif key.startswith(prefix) and key.count("__") >= 1 and key[len(prefix):].split("__", 1)[0] not in {"PUBLISH_JOB", "CAR_LIST", "CAR_PUBLISH"}:
            target = key[len(prefix):]
        if not target:
            continue
        cursor = overrides
        parts = [part.lower() for part in target.split("__") if part]
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = _parse_env_value(value)
    if os.getenv("HEADLESS") is not None:
        overrides.setdefault("browser", {})["headless"] = os.getenv("HEADLESS", "").lower() in {"1", "true", "yes", "y"}
    return overrides


def load_runtime_config(module_file: str | os.PathLike[str], base_config: dict[str, Any] | None = None, overrides_path: Path | None = None) -> dict[str, Any]:
    module_key = module_key_from_path(module_file)
    runtime = _load_yaml(overrides_path or DEFAULT_OVERRIDES_PATH)
    merged = deepcopy(base_config or {})
    merged = _deep_merge(merged, runtime.get("defaults", {}))
    merged = _deep_merge(merged, runtime.get("modules", {}).get(module_key, {}))
    merged = _deep_merge(merged, _env_overrides(module_key))
    return merged
