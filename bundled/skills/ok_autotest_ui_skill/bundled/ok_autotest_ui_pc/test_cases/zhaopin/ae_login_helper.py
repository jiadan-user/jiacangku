"""
AE站登录辅助模块
封装AE站（阿联酋站）的登录逻辑，确保测试用例的登录前置条件满足

功能:
  - ensure_ae_logged_in(): 确保已登录AE站（支持 Session 复用）
  - 同一浏览器上下文中若已登录则快路径直接返回，避免每条用例重复加载 Session / 导航
  - 自动处理Cookie弹窗
  - 使用SessionManager复用登录状态

使用方式:
  from test_cases.zhaopin.ae_login_helper import ensure_ae_logged_in

  def test_something(page, config):
      ensure_ae_logged_in(page, config)
      # 现在已经登录，可以执行测试步骤

  # 需强制从磁盘重载 Session 时（少见）:
  # ensure_ae_logged_in(page, config, force=True)
"""

import re

from pages.login_page import LoginPage
from test_cases.zhaopin.explicit_waits import dom_content_loaded_soft
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()


def _ae_fast_path_logged_in(page, config) -> bool:
    """
    判断当前浏览器上下文是否已在 AE 站点且处于登录态（用于跳过重复的 Session 加载与导航）。

    注意：显式登录/注册页不使用快路径，避免误判。
    """
    try:
        raw = page.url or ""
        if not raw or raw in ("about:blank", "chrome://newtab/"):
            return False
        url_lower = raw.lower()
        path_lower = ""
        try:
            from urllib.parse import urlparse

            path_lower = urlparse(raw).path.lower()
        except Exception:
            pass
        if "/login" in path_lower or "signin" in url_lower:
            return False

        base = (config.get("base_url") or "").rstrip("/").lower()
        if not base:
            return False
        if not raw.lower().startswith(base):
            return False

        return _is_ae_logged_in(page)
    except Exception:
        return False


def ensure_ae_logged_in(page, config, *, force: bool = False):
    """
    确保已登录AE站（阿联酋站）

    逻辑:
      1. 【快路径】同一 module 内浏览器未关闭时，若当前页已在 AE 且已登录，直接返回（不重复加载 Session、不 goto）
      2. 尝试加载已保存的Session（Cookies）
      3. 如果Session有效，直接返回
      4. 如果Session无效，执行完整登录流程
      5. 登录成功后保存Session供下次复用

    Args:
        page: Playwright Page对象
        config: 测试配置字典（包含base_url、test_account等）
        force: 为 True 时跳过快路径（例如在需要强制从磁盘重载 Session 的场景）

    Raises:
        AssertionError: 如果登录失败
    """

    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)

    if not force and _ae_fast_path_logged_in(page, config):
        logger.info("✓ 当前浏览器上下文已处于 AE 登录态，跳过 Session 加载与导航")
        return

    logger.info(f"尝试加载Session: {session_name}")
    if session_manager.load_session():
        logger.info("Session加载成功，验证登录状态...")
        try:
            page.goto(f"{config['base_url']}/en/city-abu-dhabi/", wait_until="domcontentloaded", timeout=25000)
            try:
                page.wait_for_load_state("networkidle", timeout=6000)
            except Exception:
                pass
            if _is_ae_logged_in(page):
                logger.info("✓ Session有效，已登录AE站")
                return
            else:
                logger.warning("Session已过期，将执行登录流程")
        except Exception as e:
            logger.warning(f"Session验证超时（{e}），信任Cookie直接使用")
            try:
                page.goto("about:blank", wait_until="domcontentloaded", timeout=5000)
            except Exception:
                pass
            return
    else:
        logger.info("未找到有效Session，将执行登录流程")

    logger.info("开始AE站登录流程...")
    login_page = LoginPage(page)

    logger.info("清除失效Cookie并导航到AE站首页...")
    try:
        page.context.clear_cookies()
    except Exception:
        pass
    try:
        login_page.navigate_to_home_page(base_url=config['base_url'])
    except Exception as e:
        logger.warning(f"首页导航异常（{e}），尝试 commit 模式重新导航...")
        try:
            page.goto(config['base_url'], wait_until="commit", timeout=30000)
            dom_content_loaded_soft(page, timeout=15000)
            try:
                page.get_by_text(re.compile(r"Log\s*in|OK\.com|OKer", re.I)).first.wait_for(
                    state="visible", timeout=10000
                )
            except Exception:
                pass
        except Exception as e2:
            logger.error(f"commit 模式导航也失败: {e2}")
            raise AssertionError(f"无法访问AE站，请检查网络/VPN: {e2}")

    logger.info("处理Cookie弹窗...")
    login_page.handle_cookie_popup()
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass

    logger.info("点击Log in / Register按钮...")
    login_page.click_login_register_button()
    try:
        page.get_by_role("textbox", name="Email or phone number").first.wait_for(
            state="visible", timeout=15000
        )
    except Exception:
        page.locator('input[type="email"], input[type="text"]').first.wait_for(
            state="visible", timeout=10000
        )

    logger.info("填写用户名...")
    login_page.input_email(config['test_account']['username'])

    logger.info("点击Continue按钮...")
    login_page.click_continue_button()
    try:
        page.locator('input[type="password"]').first.wait_for(state="visible", timeout=15000)
    except Exception:
        pass

    logger.info("填写密码...")
    login_page.input_password(config['test_account']['password'])

    logger.info("点击Login按钮提交...")
    login_page.click_login_button()
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass

    logger.info("验证登录状态...")
    if not _is_ae_logged_in(page):
        try:
            page.locator("text=Log in / Register").first.wait_for(state="hidden", timeout=20000)
        except Exception:
            pass
        if not _is_ae_logged_in(page):
            logger.error("登录失败！")
            raise AssertionError("AE站登录失败，未检测到登录成功标志")

    logger.info("✓ 登录成功！")
    logger.info(f"保存Session: {session_name}")
    session_manager.save_session()
    logger.info("✓ Session已保存，下次测试将自动复用")


def _is_ae_logged_in(page) -> bool:
    """
    检查AE站是否已登录

    通过检查页面中用户相关元素是否存在来判断
    AE站登录后：导航栏显示用户昵称（如 OKer_xxx），"Log in / Register" 消失
    """
    try:
        # 方法1：确认 "Log in / Register" 按钮已消失
        login_btn = page.locator("text=Log in / Register")
        if not login_btn.is_visible(timeout=2000):
            return True
        return False
    except Exception:
        # 找不到元素（超时）通常意味着已登录
        return True
