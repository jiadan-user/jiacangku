# test_cases/property_map/conftest.py
#
# 覆盖上层 conftest 中 scope="class" 的 page fixture，
# 改为 scope="module"，使同一模块内所有测试函数共享一个浏览器实例。
import os
import pytest
from pages.login_page import LoginPage
from pages.property_map_page import PropertyMapPage
from utils.browser_manager import BrowserManager
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()


@pytest.fixture(scope="module")
def page(config):
    """
    浏览器页面 fixture（module 级别）
    同一模块内的所有测试函数共享同一个浏览器实例，只打开一次浏览器。
    登录也只执行一次（session 复用），之后所有用例直接使用已登录的页面。
    """
    browser_manager = BrowserManager()
    pg = browser_manager.start_browser(
        browser_type=config['browser']['type'],
        headless=config['browser']['headless'],
        base_url=config['base_url'],
        viewport=config['browser']['viewport']
    )

    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            pg.pause()
        except Exception:
            pass

    # ── 模块级别一次性登录 ──────────────────────────────────────────────
    site = config["site"]
    role = config["role"]
    user_name = config["user_name"]
    base_url = config["base_url"]
    username = config["test_account"]["username"]
    password = config["test_account"]["password"]

    session_manager = SessionManager(pg, base_url, session_name=f"{site}_{role}_{user_name}")
    session_loaded = session_manager.load_session()
    login_page = LoginPage(pg)

    if session_loaded:
        # 注入 cookie 后必须先访问首页，才能验证 session 是否有效
        logger.info("✓ [conftest] 成功加载 Session，访问首页验证...")
        try:
            pg.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            logger.warning(f"[conftest] 首页加载失败: {e}")
        try:
            pg.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        is_logged_in = login_page.is_login_button_text_changed(timeout=3000)
        if not is_logged_in:
            logger.info("⚠️ [conftest] Session 已过期，重新登录")
            session_loaded = False
        else:
            logger.info("✅ [conftest] Session 有效")

    if not session_loaded:
        login_page.navigate_to_home_page(base_url=base_url)
        login_page.handle_cookie_popup()
        try:
            pg.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        login_page.click_login_register_button()
        login_page.input_email(username)
        login_page.click_continue_button()
        login_page.input_password(password)
        login_page.click_login_button()
        pg.wait_for_load_state("domcontentloaded", timeout=10000)
        session_manager.save_session()
        logger.info("✅ [conftest] 登录成功，Session 已保存")
    # ────────────────────────────────────────────────────────────────────

    # 登录完成后统一处理一次 Cookie 弹窗，避免后续测试用例导航到地图页时弹窗遮挡地图
    try:
        map_page = PropertyMapPage(pg)
        map_page.handle_cookie_popup()
        logger.info("✅ [conftest] Cookie 弹窗已处理")
    except Exception as e:
        logger.warning(f"[conftest] Cookie 弹窗处理跳过: {e}")

    yield pg

    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(pg)