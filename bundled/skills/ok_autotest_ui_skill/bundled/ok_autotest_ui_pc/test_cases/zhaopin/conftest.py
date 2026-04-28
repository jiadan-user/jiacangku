# test_cases/zhaopin/conftest.py
"""
招聘模块（zhaopin）专用配置

- 保留 SITE 等环境变量（与 ConfigLoader / 历史脚本一致）
- 覆盖 ``page`` fixture：在默认「每文件一个 BrowserManager」基础上，增加可选的
  **session 级单例 Chromium + 按站点（sg/ae/es）复用 BrowserContext**，
  减少重复 launch 与跨文件丢失 Cookie 时的重复登录。

关闭共享（回退为 test_cases/conftest 行为）::

    ZHAOPIN_SHARED_CONTEXT=0 pytest test_cases/zhaopin/ ...
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

# 招聘模块历史默认（部分工具链仍可能读取）
os.environ.setdefault("SITE", "sg")
os.environ.setdefault("ROLE", "seller")
os.environ.setdefault("USER_NAME", "dc_seller_sg")

from utils.logger import setup_logger

logger = setup_logger()

# session 级共享：1 = 开启（默认），0 = 每模块独立 BrowserManager（与全局 conftest 一致）
_USE_SHARED = os.environ.get("ZHAOPIN_SHARED_CONTEXT", "1").strip().lower() not in (
    "0",
    "false",
    "no",
    "off",
)


@pytest.fixture(scope="session", autouse=True)
def _zhaopin_session_playwright_keepalive(request):
    """
    使用共享 Chromium 时未走 BrowserManager.start_browser，全局 _active_instances 可能为空，
    跨模块首个用例前的 cleanup 会误触发 cleanup_asyncio_if_needed 并 stop 全局 Playwright。
    会话期内占住一个 in_use 的 BrowserManager，避免后续模块 new_page 失败。
    """
    if not _USE_SHARED:
        yield
        return
    from utils.browser_manager import BrowserManager

    holder = BrowserManager()
    holder.mark_in_use()
    request.addfinalizer(holder.mark_released)
    yield


def _site_key(config: dict) -> str:
    s = (config.get("site") or "").strip().lower()
    if s in ("sg", "ae", "es"):
        return s
    base = (config.get("base_url") or "").lower()
    if "sg.58" in base or "sgpub" in base:
        return "sg"
    if "ae.58" in base or "aepub" in base:
        return "ae"
    if "es.58" in base or "espub" in base:
        return "es"
    return "default"


def _effective_headless(config: dict) -> bool:
    env_h = os.environ.get("HEADLESS", "").lower() in ("true", "1", "yes")
    env_ci = os.environ.get("CI", "").lower() in ("true", "1", "yes")
    if env_h or env_ci:
        return True
    return bool(config.get("browser", {}).get("headless", False))


def _optional_storage_state(request) -> str | None:
    storage_path = os.environ.get("MARKETPLACE_STORAGE_STATE", "").strip()
    if storage_path and Path(storage_path).is_file():
        logger.info("[AUTH] MARKETPLACE_STORAGE_STATE=%s", storage_path)
        return storage_path
    module_dir = Path(request.module.__file__).resolve().parent
    default_auth = module_dir / "auth_state.json"
    if default_auth.is_file():
        logger.info("[AUTH] 使用模块旁默认 auth_state.json: %s", default_auth)
        return str(default_auth)
    return None


def _legacy_module_page(config, request):
    """与 test_cases/conftest ``page`` 一致：每模块独立 BrowserManager。"""
    from utils.browser_manager import BrowserManager

    browser_manager = BrowserManager()
    storage_kw = {}
    sp = _optional_storage_state(request)
    if sp:
        storage_kw["storage_state"] = sp
    page = browser_manager.start_browser(
        browser_type=config["browser"]["type"],
        headless=config["browser"]["headless"],
        base_url=config["base_url"],
        viewport=config["browser"]["viewport"],
        **storage_kw,
    )
    browser_manager.mark_in_use()
    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            page.pause()
        except Exception:
            pass
    yield page
    browser_manager.mark_released()
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(page)


class _ZhaopinSiteContextPool:
    """按站点缓存 BrowserContext（session 内跨模块复用）。"""

    def __init__(self, browser):
        self.browser = browser
        self._contexts: dict[str, object] = {}

    def get_context(self, site_key: str, config: dict, request):
        if site_key not in self._contexts:
            from utils.browser_manager import new_stealth_browser_context

            headless = _effective_headless(config)
            viewport = config.get("browser", {}).get("viewport")
            base_url = config.get("base_url")
            storage = _optional_storage_state(request)
            ctx = new_stealth_browser_context(
                self.browser,
                headless=headless,
                viewport=viewport,
                base_url=base_url,
                storage_state=storage,
            )
            self._contexts[site_key] = ctx
            logger.info(
                "[zhaopin] 已创建共享 BrowserContext: site=%s headless=%s",
                site_key,
                headless,
            )
        return self._contexts[site_key]

    def close_all(self):
        for ctx in self._contexts.values():
            try:
                ctx.close()
            except Exception:
                pass
        self._contexts.clear()


@pytest.fixture(scope="session")
def _zhaopin_shared_chromium(request):
    if not _USE_SHARED:
        yield None
        return
    from utils.browser_manager import launch_shared_chromium_browser

    browser = launch_shared_chromium_browser()

    def _fin():
        try:
            browser.close()
        except Exception as e:
            logger.warning("[zhaopin] 关闭共享 Chromium 时: %s", e)

    request.addfinalizer(_fin)
    yield browser


@pytest.fixture(scope="session")
def _zhaopin_context_pool(_zhaopin_shared_chromium, request):
    if not _USE_SHARED or _zhaopin_shared_chromium is None:
        yield None
        return
    pool = _ZhaopinSiteContextPool(_zhaopin_shared_chromium)

    def _fin():
        pool.close_all()

    request.addfinalizer(_fin)
    yield pool


@pytest.fixture(scope="module")
def page(config, request, _zhaopin_context_pool):
    """
    zhaopin 目录内覆盖全局 ``page``：

    - 默认：同一 session 共用一个 Chromium；**sg / ae / es 各共用一个 BrowserContext**，
      同一站点跨文件保留 Cookie，减少 ``ensure_*_logged_in`` 中的重复登录与冷启动。
    - 每模块仍创建 **新 Page**（标签页），模块结束关闭 Page，不关闭共享 Context。

    需完全隔离时（与旧行为一致）设置 ``ZHAOPIN_SHARED_CONTEXT=0``。
    """
    if not _USE_SHARED or _zhaopin_context_pool is None:
        yield from _legacy_module_page(config, request)
        return

    site = _site_key(config)
    ctx = _zhaopin_context_pool.get_context(site, config, request)
    pg = ctx.new_page()
    headless = _effective_headless(config)
    if not headless:
        try:
            session = ctx.new_cdp_session(pg)
            session.send(
                "Browser.setWindowBounds",
                {"windowId": 1, "bounds": {"windowState": "maximized"}},
            )
        except Exception:
            try:
                pg.evaluate(
                    """() => {
                        window.moveTo(0, 0);
                        window.resizeTo(screen.availWidth, screen.availHeight);
                    }"""
                )
            except Exception:
                pass
    pg.set_default_timeout(30000)
    pg.set_default_navigation_timeout(30000)

    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            pg.pause()
        except Exception:
            pass
    yield pg
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        try:
            pg.close()
        except Exception:
            pass
