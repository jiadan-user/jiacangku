from __future__ import annotations

import os
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

import allure

from utils.browser_manager import BrowserManager
from utils.runtime_config import load_runtime_config

DEFAULT_RUNTIME_CONFIG: dict[str, Any] = {
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
    },
}

REQUIRED_CONFIG_PATHS = (
    "base_url",
    "browser.type",
    "browser.headless",
    "browser.viewport",
    "timeout.default",
)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def resolve_headless_for_current_env(headless: bool) -> bool:
    if sys.platform.startswith("linux") and not _has_display():
        return True
    return headless


def _missing_config_paths(config: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for path in REQUIRED_CONFIG_PATHS:
        cursor: Any = config
        for part in path.split("."):
            if not isinstance(cursor, dict) or part not in cursor:
                missing.append(path)
                break
            cursor = cursor[part]
    return missing


def build_runtime_config(
    module: Any,
    *,
    default_config: dict[str, Any] | None = None,
    require_module_config: bool = True,
) -> dict[str, Any]:
    if hasattr(module, "_CONFIG"):
        base_config = deepcopy(module._CONFIG)
    elif default_config is not None:
        base_config = deepcopy(default_config)
    elif require_module_config:
        raise ValueError(
            f"测试模块 {module.__name__} 缺少 _CONFIG 配置。\n"
            "请确保脚本声明 _CONFIG，或在目录级 conftest 中提供 default_config。"
        )
    else:
        base_config = {}

    merged = _deep_merge(DEFAULT_RUNTIME_CONFIG, base_config)
    merged = load_runtime_config(module.__file__, merged)

    if os.getenv("HEADLESS") is None:
        merged.setdefault("browser", {})["headless"] = resolve_headless_for_current_env(
            merged["browser"]["headless"]
        )

    missing = _missing_config_paths(merged)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"测试模块 {module.__name__} 缺少必要配置项: {joined}")

    return merged


def start_managed_page(
    config: dict[str, Any],
    *,
    force_headless: bool | None = None,
    use_global_instance: bool = True,
) -> tuple[BrowserManager, Any]:
    browser_manager = BrowserManager(use_global_instance=use_global_instance)
    headless = config["browser"]["headless"] if force_headless is None else force_headless
    page = browser_manager.start_browser(
        browser_type=config["browser"]["type"],
        headless=headless,
        base_url=config["base_url"],
        viewport=config["browser"]["viewport"],
    )
    browser_manager.mark_in_use()

    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            page.pause()
        except Exception:
            pass

    return browser_manager, page


def finish_managed_page(browser_manager: BrowserManager, page: Any) -> None:
    browser_manager.mark_released()
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(page)


def attach_failure_screenshot(item: Any, logger: Any, *, attachment_name: str = "失败截图") -> Path | None:
    page = item.funcargs.get("page")
    if not page:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_name = f"FAILED_{item.name}_{timestamp}.png"
    screenshot_dir = Path("reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = screenshot_dir / screenshot_name

    page.screenshot(path=str(screenshot_path), full_page=True, timeout=60000)

    with screenshot_path.open("rb") as handle:
        allure.attach(
            handle.read(),
            name=attachment_name,
            attachment_type=allure.attachment_type.PNG,
        )

    logger.error(f"测试失败 URL: {page.url}")
    return screenshot_path
