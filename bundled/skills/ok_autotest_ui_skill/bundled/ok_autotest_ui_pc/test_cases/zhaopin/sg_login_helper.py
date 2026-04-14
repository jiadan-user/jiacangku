# test_cases/zhaopin/sg_login_helper.py
"""
新加坡站招聘模块 - 登录辅助（Session 复用）
仅第一次需要完整登录，后续用例加载已保存的 Cookie
"""
from utils.logger import setup_logger

logger = setup_logger()


def ensure_sg_logged_in(page, config):
    """
    确保已登录新加坡站。优先使用 SessionManager 加载 Cookie，若无或过期则执行登录并保存。
    仅第一次需要完整登录，后续用例复用 Session。
    """
    from pages.sg_home_page import SgHomePage
    from pages.login_page import LoginPage
    from utils.session_manager import SessionManager

    base_url = config["base_url"]
    session_name = f"sg_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, base_url, session_name=session_name)

    # 尝试加载已保存的 Session
    if session_manager.load_session():
        home_page = SgHomePage(page)
        # 加载 Cookie 后必须导航到目标页面才能验证登录状态
        home_page.navigate_to_home(base_url)
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        home_page.handle_cookie_popup()
        page.wait_for_timeout(1500)
        if home_page.is_logged_in():
            logger.info("✓ 已加载 Session，跳过登录")
            return
        logger.info("⚠️ Session 已过期，需要重新登录")
        session_manager.clear_session()

    # 执行完整登录
    home_page = SgHomePage(page)
    login_page = LoginPage(page)
    home_page.navigate_to_home(base_url)
    page.wait_for_load_state("domcontentloaded", timeout=10000)
    home_page.handle_cookie_popup()
    page.wait_for_timeout(1500)

    if not home_page.is_logged_in():
        logger.info("未登录，开始执行登录流程")
        login_page.click_login_register_button()
        page.wait_for_timeout(1500)
        login_page.input_email(config["test_account"]["username"])
        login_page.click_continue_button()
        page.wait_for_timeout(2000)
        login_page.input_password(config["test_account"]["password"])
        login_page.click_login_button()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        assert home_page.is_logged_in(), "登录失败"
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    else:
        logger.info("✓ 已登录")
        session_manager.save_session()
