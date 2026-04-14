from __future__ import annotations

import argparse
import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

import pytest

from .common import GENERATED_CATALOG_PATH, OVERRIDES_PATH, ROOT_DIR, load_yaml, save_json, slugify, utcnow_iso
from .governance import case_is_governed
from .models import CatalogCase, PRIORITY_MARKERS, SITE_MARKERS

SPECIAL_MODULE_NAMES = {
    " SEO": "seo",
    "seo": "seo",
    "test_car": "car",
    "chat-ai": "chat_ai",
    "体验": "tiyan",
    "test_tiyan": "tiyan",
}

ROOT_FILE_MODULES = {
    "test_job_basics.py": "publish_job",
    "test_post_marketplace.py": "marketplace_post",
    "test_post_explore.py": "explore",
}


def _first_marker(markers: list[str], candidates: set[str]) -> str | None:
    for marker in markers:
        if marker in candidates:
            return marker
    return None


def _extract_allure_label(item: pytest.Item, label_type: str) -> str | None:
    for marker in item.iter_markers(name="allure_label"):
        if marker.kwargs.get("label_type") != label_type or not marker.args:
            continue
        value = marker.args[0]
        if hasattr(value, "value"):
            value = value.value
        return str(value)
    return None


def _relative_file_path(item: pytest.Item) -> str:
    return Path(item.fspath).resolve().relative_to(ROOT_DIR).as_posix()


def _load_overrides() -> dict[str, Any]:
    overrides = load_yaml(OVERRIDES_PATH)
    overrides.setdefault("directories", {})
    overrides.setdefault("paths", {})
    overrides.setdefault("cases", {})
    return overrides


def _story_feature_slug(case: CatalogCase) -> str | None:
    if case.allure_story:
        story_slug = slugify(case.allure_story)
        if case.module_id:
            return f"{slugify(case.module_id)}_{story_slug}"
        return story_slug
    if case.allure_title:
        return slugify(case.allure_title)
    return None


def _extract_config_value(item: pytest.Item, key: str) -> str | None:
    module_config = getattr(item.module, "_CONFIG", None)
    if isinstance(module_config, dict):
        value = module_config.get(key)
        if value is not None:
            return str(value)
    return None


def _directory_override(file_path: str, overrides: dict[str, Any]) -> dict[str, Any]:
    matched: tuple[int, dict[str, Any]] | None = None
    for prefix, payload in overrides.get("directories", {}).items():
        if file_path.startswith(prefix):
            candidate = (len(prefix), payload)
            if matched is None or candidate[0] > matched[0]:
                matched = candidate
    return matched[1] if matched else {}


def _normalize_module_name(value: str | None) -> str | None:
    if not value:
        return None
    if value in SPECIAL_MODULE_NAMES:
        return SPECIAL_MODULE_NAMES[value]
    normalized = slugify(value)
    return normalized or None


def _infer_module_id(case: CatalogCase, file_override: dict[str, Any]) -> str | None:
    if file_override.get("module_id"):
        return file_override["module_id"]
    file_path = Path(case.file_path)
    parts = file_path.parts
    marker_set = set(case.markers)
    marker_to_module = {
        "job_publish": "publish_job",
        "explore_list": "car_list",
        "property_detail": "property_detail",
        "property_rent": "property_basics",
        "property_buy": "property_basics",
        "property_map": "property_map",
        "wallet": "wallet",
        "zhaopin": "zhaopin",
        "news": "seo",
        "settings": "seo",
        "ai": "ai",
        "ai_publish": "ai",
        "ai_chat": "ai",
        "marketplace": "marketplace_post",
        "kyc": "kyc",
        "search": "search_input",
        "location_panel": "tiyan",
    }
    for marker, module_id in marker_to_module.items():
        if marker in marker_set:
            return module_id

    if len(parts) >= 3:
        return _normalize_module_name(parts[1])

    if len(parts) >= 2:
        return ROOT_FILE_MODULES.get(parts[-1]) or _normalize_module_name(parts[-1].replace("test_", "").replace(".py", ""))
    return None


def _infer_feature_id(case: CatalogCase, file_override: dict[str, Any]) -> str | None:
    file_path = case.file_path
    if file_override.get("feature_id"):
        return file_override["feature_id"]
    marker_set = set(case.markers)
    if file_path.startswith("test_cases/car_list/"):
        suffix = Path(file_path).stem.replace("test_explore_list_", "")
        return f"car_list_{slugify(suffix)}"
    if file_path == "test_cases/test_car/test_ae_car_publish.py":
        return "car_publish"
    if file_path.startswith("test_cases/publish_job/"):
        if "smoke" in marker_set:
            return "publish_job_smoke"
        if "core_flow" in marker_set:
            return "publish_job_core_flow"
        if "step1" in marker_set and "validation" in marker_set:
            return "publish_job_step1_validation"
        if Path(file_path).stem.endswith("step1_extended"):
            return "publish_job_step1_extended"
        if "step2" in marker_set and "validation" in marker_set:
            return "publish_job_step2_validation"
        if "step3" in marker_set:
            return "publish_job_step3_navigation"
        if "security" in marker_set or "xss" in marker_set or "sql_injection" in marker_set:
            return "publish_job_security_ui"
        if "i18n" in marker_set or "compatibility" in marker_set:
            return "publish_job_i18n_compatibility"
        if Path(file_path).stem.endswith("supplemental"):
            return "publish_job_supplemental"
    story_slug = _story_feature_slug(case)
    if story_slug:
        return story_slug
    file_slug = slugify(Path(file_path).stem.replace("test_", ""))
    if case.module_id:
        return f"{slugify(case.module_id)}_{file_slug}"
    return file_slug or None


def _case_aliases(case: CatalogCase, extra_aliases: list[str]) -> list[str]:
    aliases = {alias for alias in extra_aliases if alias}
    aliases.update(filter(None, [case.module_id, case.feature_id, slugify(case.allure_story), slugify(case.allure_title)]))
    return sorted(aliases)


def _is_skill_excluded(item: pytest.Item, markers: list[str], merged_override: dict[str, Any], case: CatalogCase) -> bool:
    if bool(merged_override.get("skill_excluded")):
        return True
    title = (case.allure_title or "").lower()
    name = (item.name or "").lower()
    if "helper" in name:
        return True
    if "辅助工具" in title:
        return True
    if "已迁移至测试类" in title:
        return True
    if "helper" in markers:
        return True
    return False


def _build_case(item: pytest.Item, overrides: dict[str, Any]) -> CatalogCase:
    markers = []
    case_id = None
    for marker in item.iter_markers():
        if marker.name == "allure_label":
            continue
        markers.append(marker.name)
        if marker.name.startswith("case_id_") and case_id is None:
            case_id = marker.name

    file_path = _relative_file_path(item)
    directory_override = _directory_override(file_path, overrides)
    path_override = overrides["paths"].get(file_path, {})
    case_override = overrides["cases"].get(item.nodeid, {})
    merged_override = {**directory_override, **path_override, **case_override}

    case = CatalogCase(
        nodeid=item.nodeid,
        file_path=file_path,
        test_name=item.name,
        case_id=case_id,
        priority=merged_override.get("priority") or _first_marker(markers, PRIORITY_MARKERS),
        site=merged_override.get("site") or _first_marker(markers, SITE_MARKERS) or _extract_config_value(item, "site"),
        markers=sorted(set(markers)),
        allure_feature=_extract_allure_label(item, "feature"),
        allure_story=_extract_allure_label(item, "story"),
        allure_title=getattr(getattr(item, "obj", None), "__allure_display_name__", None),
        severity=_extract_allure_label(item, "severity"),
    )

    case.module_id = _infer_module_id(case, merged_override)
    case.feature_id = _infer_feature_id(case, merged_override)
    case.baseline_set = merged_override.get("baseline_set")
    case.risk_level = merged_override.get("risk_level")
    case.owner = merged_override.get("owner")
    case.skill_excluded = _is_skill_excluded(item, markers, merged_override, case)
    case.aliases = _case_aliases(case, merged_override.get("aliases", []))
    case.governed = case_is_governed(case)
    return case


class _CollectPlugin:
    def __init__(self, overrides: dict[str, Any]) -> None:
        self.cases: list[CatalogCase] = []
        self.overrides = overrides

    def pytest_collection_modifyitems(self, session: pytest.Session, config: pytest.Config, items: list[pytest.Item]) -> None:
        self.cases = [_build_case(item, self.overrides) for item in items]


def collect_catalog() -> list[CatalogCase]:
    overrides = _load_overrides()
    plugin = _CollectPlugin(overrides)
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        exit_code = pytest.main(["--collect-only", "-q", "-p", "no:rerunfailures", "-o", "addopts="], plugins=[plugin])
    if exit_code not in {0, 5}:
        if stderr_buffer.getvalue():
            print(stderr_buffer.getvalue())
        raise SystemExit(exit_code)
    return plugin.cases


def build_catalog(output_path: Path = GENERATED_CATALOG_PATH) -> dict[str, Any]:
    cases = sorted(collect_catalog(), key=lambda item: item.nodeid)
    payload = {
        "generated_at": utcnow_iso(),
        "root_dir": str(ROOT_DIR),
        "case_count": len(cases),
        "governed_case_count": sum(1 for case in cases if case.governed),
        "cases": [case.to_dict() for case in cases],
    }
    save_json(output_path, payload)
    return payload


def load_catalog(path: Path = GENERATED_CATALOG_PATH) -> list[CatalogCase]:
    if not path.exists():
        build_catalog(path)
    from .common import load_json

    payload = load_json(path)
    return [CatalogCase.from_dict(item) for item in payload.get("cases", [])]


def handle_catalog_build(args: argparse.Namespace) -> int:
    payload = build_catalog(Path(args.output) if args.output else GENERATED_CATALOG_PATH)
    print(f"catalog built: {payload['case_count']} cases ({payload['governed_case_count']} governed)")
    print(f"output: {Path(args.output) if args.output else GENERATED_CATALOG_PATH}")
    return 0
