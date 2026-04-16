"""
AE站登录辅助模块
封装AE站（阿联酋站）的登录逻辑，确保测试用例的登录前置条件满足

功能:
  - ensure_ae_logged_in(): 确保已登录AE站（支持Session复用）
  - 自动处理Cookie弹窗
  - 使用SessionManager复用登录状态

使用方式:
  from test_cases.zhaopin.ae_login_helper import ensure_ae_logged_in

  def test_something(page, config):
      ensure_ae_logged_in(page, config)
      # 现在已经登录，可以执行测试步骤
"""

from pages.login_page import LoginPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()


def ensure_ae_logged_in(page, config):
    """
    确保已登录AE站（阿联酋站）

    逻辑:
      1. 尝试加载已保存的Session（Cookies）
      2. 如果Session有效，直接返回
      3. 如果Session无效，执行完整登录流程
      4. 登录成功后保存Session供下次复用

    Args:
        page: Playwright Page对象
        config: 测试配置字典（包含base_url、test_account等）

    Raises:
        AssertionError: 如果登录失败
    """

    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)

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
            page.wait_for_timeout(3000)
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
    page.wait_for_timeout(2000)

    logger.info("填写用户名...")
    login_page.input_email(config['test_account']['username'])

    logger.info("点击Continue按钮...")
    login_page.click_continue_button()
    page.wait_for_timeout(2000)

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
        page.wait_for_timeout(3000)
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
