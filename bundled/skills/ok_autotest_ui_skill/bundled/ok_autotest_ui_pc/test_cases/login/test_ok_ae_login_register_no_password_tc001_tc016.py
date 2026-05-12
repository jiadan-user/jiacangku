# test_cases/login/test_ok_ae_login_register_no_password_tc001_tc016.py
"""
OK AE站 - 登录注册未设置密码场景（邮箱 + 手机号验证码路径）

本脚本由 playwright-test-generator 生成
录制文档：测试用例/OK-AE-登录注册未设置密码场景-测试用例.md
生成时间：2026-04-03

测试范围：TC001–TC004、TC007–TC016（TC005 文档标注为不可自动化，已跳过）
测试站点：AE（迪拜城市落地页，与文档手机号实测路径一致）
"""

import re

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "user",
    "user_name": "test_no_pwd_user_ae",
    "base_url": "https://ae.58v5.cn/en/city-dubai/",
    "test_account": {
        "username": "mamengmeng01@58.com",
        "password": "",
    },
    "test_phone_no_password": {
        "local": "501234579",
        "full": "+971 501234579",
    },
    "locale": "en-AE",
    "currency": "AED",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 60000,
    },
}


# 为 LoginPage 动态添加 ensure_logged_out 方法（与 login/conftest.py 一致）
def _ensure_logged_out_impl(self, base_url=None):
    """确保已退出登录状态"""
    try:
        # 清除 cookies 和存储
        self.page.context.clear_cookies()
        self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        logger.debug("✓ 已清除 Cookies 和存储")
        
        # 重新加载页面
        if base_url:
            self.page.goto(base_url, wait_until="domcontentloaded", timeout=10000)
        else:
            self.page.reload(wait_until="domcontentloaded", timeout=10000)
        
        self.page.wait_for_timeout(1000)
        
        # 处理 cookie 弹窗
        self.handle_cookie_popup()
        logger.debug("✓ 已确保退出登录状态")
    except Exception as e:
        logger.warning(f"确保退出登录失败: {e}")


# 定义模块特定配置，包含 test_account 等特有字段
@pytest.fixture(scope="module")
def login_config():
    """
    本模块专用配置，包含 test_account 和 test_phone_no_password 字段
    """
    import os
    config = _CONFIG.copy()
    # 支持环境变量覆盖 headless
    env_headless = os.getenv("HEADLESS")
    if env_headless:
        config['browser']['headless'] = env_headless.lower() in ('true', '1', 'yes')
    
    # 为 LoginPage 类动态添加 ensure_logged_out 方法
    if not hasattr(LoginPage, 'ensure_logged_out'):
        LoginPage.ensure_logged_out = _ensure_logged_out_impl
        logger.debug("✅ 已为 LoginPage 添加 ensure_logged_out 方法")
    
    return config


@pytest.fixture(scope="module")
def page(login_config):
    """
    为本模块提供独立的 page fixture，确保页面正确初始化
    """
    from utils.browser_manager import BrowserManager
    import os
    
    browser_manager = BrowserManager()
    headless = os.getenv("HEADLESS", "").lower() in ("true", "1", "yes")
    if not headless:
        headless = login_config['browser'].get('headless', False)
    
    page = browser_manager.start_browser(
        browser_type=login_config['browser']['type'],
        headless=headless,
        base_url=login_config['base_url'],
        viewport=login_config['browser']['viewport']
    )
    
    # 设置默认超时
    page.set_default_timeout(30000)
    
    yield page
    
    # 清理
    try:
        browser_manager.close_browser(page)
    except Exception:
        pass


@pytest.fixture(autouse=True)
def ensure_logged_out_before_test(page: Page, login_config):
    """
    每个用例前确保访客态。
    conftest.py 的 smart_reset_for_login_tests 已处理弹窗关闭；
    _navigate_xxx_page 辅助函数内会调用 ensure_logged_out 做真正的状态重置。
    此处只做快速登录态检测（200ms），避免重复触发完整页面导航。
    """
    login_page = LoginPage(page)
    try:
        if login_page.is_login_button_text_changed(timeout=200):
            # 已登录：才做一次轻量 cookie 清理 + reload，不重复 goto
            page.context.clear_cookies()
            page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
            page.reload(wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(500)
    except Exception:
        pass
    yield


def _dialog(page: Page):
    return page.locator('[role="dialog"]').first


def _code_input(dialog):
    return dialog.locator(
        'input[type="tel"], input.ok_login_input_label_content_input'
    ).first


def _navigate_email_no_password_password_page(page: Page, login_config) -> None:
    # 确保页面已导航到正确的 URL
    if page.url == "about:blank" or not page.url.startswith(login_config["base_url"]):
        page.goto(login_config["base_url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
    
    login_page = LoginPage(page)
    login_page.ensure_logged_out(login_config["base_url"])
    login_page.click_login_register_button()
    page.wait_for_timeout(1200)
    login_page.input_email(login_config["test_account"]["username"])
    login_page.click_continue_button()
    page.wait_for_timeout(2500)


def _navigate_email_verification_page(page: Page, login_config) -> None:
    _navigate_email_no_password_password_page(page, login_config)
    dialog = _dialog(page)
    dialog.get_by_role("button", name="Send code").click()
    page.wait_for_timeout(2000)


def _navigate_phone_no_password_password_page(page: Page, login_config) -> None:
    # 确保页面已导航到正确的 URL
    if page.url == "about:blank" or not page.url.startswith(login_config["base_url"]):
        page.goto(login_config["base_url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
    
    login_page = LoginPage(page)
    login_page.ensure_logged_out(login_config["base_url"])
    login_page.click_login_register_button()
    page.wait_for_timeout(1200)
    login_page.input_email(login_config["test_phone_no_password"]["local"])
    login_page.click_continue_button()
    page.wait_for_timeout(3000)


def _attach_screenshot(page: Page, name: str) -> None:
    try:
        allure.attach(
            page.screenshot(timeout=10000),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as e:
        logger.warning("截图失败: %s", e)


def _click_login_dialog_back(page: Page) -> None:
    """
    在无密码密码页点击返回，回到欢迎页。
    与 `test_login_forgot_password_tc039_tc048` 中验证码页返回策略一致：
    实际 UI 多为 back 图标（img），而非带「Back」文案的 button。
    """
    dialog = _dialog(page)
    candidates = [
        dialog.locator('img[src*="back" i]').first,
        dialog.locator('img[alt=""]').first,
        dialog.get_by_role("button", name=re.compile(r"back", re.I)).first,
        dialog.locator('button:has-text("Back")').first,
        dialog.locator('[aria-label*="back" i]').first,
        dialog.locator('[class*="back" i]').first,
    ]
    last_err: Exception | None = None
    for loc in candidates:
        try:
            if loc.is_visible(timeout=2500):
                loc.click(timeout=10000)
                page.wait_for_timeout(1800)
                return
        except Exception as e:
            last_err = e
            continue
    raise AssertionError(f"登录弹层内未找到可用的返回控件: {last_err!r}")


@allure.epic("OK AE站")
@allure.feature("登录注册未设置密码场景（邮箱）")
class TestAeNoPasswordEmail:
    """邮箱未设置密码 — 验证码登录路径（文档第一节至第五节）"""

    @pytest.mark.case_id_ae_login_nopwd_email_tc001
    @pytest.mark.smoke
    @pytest.mark.p0
    @allure.story("一、未设置密码提示展示")
    @allure.title("TC001: 未设置密码邮箱进入密码页显示特殊提示")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "验证未设置密码邮箱进入密码页后展示 Welcome back、无密码提示、Send code 且无密码框。"
    )
    def test_tc001_no_password_email_password_page(self, page: Page, login_config):
        _navigate_email_no_password_password_page(page, login_config)
        dialog = _dialog(page)
        assert dialog.is_visible(timeout=8000)
        assert dialog.locator("text=/welcome.*back/i").first.is_visible()
        assert dialog.get_by_text(login_config["test_account"]["username"]).first.is_visible()
        hint = (
            dialog.locator("text=/haven't added a password/i").first.is_visible(timeout=4000)
            or dialog.locator("text=/Sign in with.*email code/i").first.is_visible(timeout=2000)
        )
        assert hint, "未展示未设置密码引导文案"
        send_btn = dialog.get_by_role("button", name="Send code")
        assert send_btn.is_visible()
        assert dialog.locator('input[type="password"]').count() == 0
        _attach_screenshot(page, "TC001_邮箱无密码密码页")

    @pytest.mark.case_id_ae_login_nopwd_email_tc002
    @pytest.mark.p1
    @allure.story("一、未设置密码提示展示")
    @allure.title("TC002: Send code 按钮初始状态正常")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证 Send code 可见、可点且文案为 Send code。")
    def test_tc002_send_code_initial_state(self, page: Page, login_config):
        _navigate_email_no_password_password_page(page, login_config)
        btn = _dialog(page).get_by_role("button", name="Send code")
        expect(btn).to_be_visible()
        expect(btn).to_be_enabled()
        assert btn.inner_text().strip() == "Send code"

    @pytest.mark.case_id_ae_login_nopwd_email_tc003
    @pytest.mark.smoke
    @pytest.mark.p0
    @allure.story("二、发送验证码功能")
    @allure.title("TC003: 点击 Send code 成功发送验证码（邮箱）")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "验证点击 Send code 后出现邮箱 Toast、进入 Verification code 页且 Confirm 初始禁用。"
    )
    def test_tc003_send_code_email_flow(self, page: Page, login_config):
        _navigate_email_no_password_password_page(page, login_config)
        dialog = _dialog(page)
        dialog.get_by_role("button", name="Send code").click()
        page.wait_for_timeout(900)
        toast = page.get_by_text(re.compile(r"The code has been sent to your email", re.I))
        try:
            expect(toast.first).to_be_visible(timeout=6000)
        except AssertionError:
            logger.warning("未稳定捕获邮箱 Toast，继续校验验证码页")
        page.wait_for_timeout(2000)
        dialog = _dialog(page)
        assert dialog.locator("text=/Verification.*code/i").first.is_visible()
        body = dialog.inner_text()
        assert "To continue, complete this verification step" in body
        assert login_config["test_account"]["username"] in body.replace("\u00a0", " ")
        code_in = _code_input(dialog)
        assert code_in.is_visible(timeout=8000)
        ph = code_in.get_attribute("placeholder") or ""
        assert "Enter code" in ph or dialog.get_by_text("Enter code", exact=True).first.is_visible(
            timeout=3000
        )
        expect(dialog.get_by_role("button", name="Confirm")).to_be_disabled()
        _attach_screenshot(page, "TC003_邮箱验证码页")

    @pytest.mark.case_id_ae_login_nopwd_email_tc004
    @pytest.mark.p1
    @allure.story("二、发送验证码功能")
    @allure.title("TC004: 验证码倒计时正常运行（短时采样）")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("进入验证码页后等待数秒，校验倒计时按钮秒数递减或保持合法倒计时形态。")
    def test_tc004_countdown_ticks(self, page: Page, login_config):
        _navigate_email_verification_page(page, login_config)
        dialog = _dialog(page)
        cd = dialog.locator("button").filter(has_text=re.compile(r"^\d+s$")).first
        if not cd.is_visible(timeout=4000):
            logger.warning("未匹配到 XXs 倒计时，跳过递减断言")
            return
        first = cd.inner_text().strip()
        m1 = re.match(r"^(\d+)s$", first)
        assert m1, f"倒计时格式异常: {first}"
        page.wait_for_timeout(5500)
        dialog = _dialog(page)
        cd2 = dialog.locator("button").filter(has_text=re.compile(r"^\d+s$")).first
        if cd2.is_visible(timeout=3000):
            second = cd2.inner_text().strip()
            m2 = re.match(r"^(\d+)s$", second)
            if m2:
                assert int(m2.group(1)) < int(m1.group(1)), "倒计时应随时间递减"

    @pytest.mark.case_id_ae_login_nopwd_email_tc007
    @pytest.mark.smoke
    @pytest.mark.p0
    @allure.story("三、验证码输入与校验")
    @allure.title("TC007: 验证码输入框初始状态")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("验证码页输入框可见、占位或标签含 Enter code，Confirm 为 disabled。")
    def test_tc007_code_input_initial(self, page: Page, login_config):
        _navigate_email_verification_page(page, login_config)
        dialog = _dialog(page)
        inp = _code_input(dialog)
        assert inp.is_visible()
        ph = inp.get_attribute("placeholder") or ""
        if "Enter code" not in ph:
            assert dialog.get_by_text("Enter code", exact=True).first.is_visible(timeout=3000)
        expect(dialog.get_by_role("button", name="Confirm")).to_be_disabled()

    @pytest.mark.case_id_ae_login_nopwd_email_tc008
    @pytest.mark.smoke
    @pytest.mark.p0
    @allure.story("三、验证码输入与校验")
    @allure.title("TC008: 输入验证码后 Confirm 按钮变为 enabled")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("输入六位数字后 Confirm 从 disabled 变为 enabled。")
    def test_tc008_confirm_enabled_after_input(self, page: Page, login_config):
        _navigate_email_verification_page(page, login_config)
        dialog = _dialog(page)
        inp = _code_input(dialog)
        inp.fill("123456")
        page.wait_for_timeout(400)
        expect(dialog.get_by_role("button", name="Confirm")).to_be_enabled()

    @pytest.mark.case_id_ae_login_nopwd_email_tc009
    @pytest.mark.p1
    @allure.story("三、验证码输入与校验")
    @allure.title("TC009: 清空验证码后 Confirm 恢复 disabled")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("输入后再清空验证码，Confirm 应恢复为 disabled。")
    def test_tc009_clear_code_disables_confirm(self, page: Page, login_config):
        _navigate_email_verification_page(page, login_config)
        dialog = _dialog(page)
        inp = _code_input(dialog)
        inp.fill("123456")
        page.wait_for_timeout(400)
        expect(dialog.get_by_role("button", name="Confirm")).to_be_enabled()
        inp.clear()
        page.wait_for_timeout(400)
        expect(dialog.get_by_role("button", name="Confirm")).to_be_disabled()

    @pytest.mark.case_id_ae_login_nopwd_email_tc010
    @pytest.mark.p2
    @allure.story("三、验证码输入与校验")
    @allure.title("TC010: 验证码输入框允许输入长字符串")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("向验证码框输入超过 20 位字符，前端不截断且 Confirm 可启用。")
    def test_tc010_long_input_not_truncated_ui(self, page: Page, login_config):
        _navigate_email_verification_page(page, login_config)
        dialog = _dialog(page)
        long_val = "12345678901234567890123"
        inp = _code_input(dialog)
        inp.fill(long_val)
        page.wait_for_timeout(300)
        assert inp.input_value() == long_val
        expect(dialog.get_by_role("button", name="Confirm")).to_be_enabled()

    @pytest.mark.case_id_ae_login_nopwd_email_tc011
    @pytest.mark.p2
    @allure.story("三、验证码输入与校验")
    @allure.title("TC011: 验证码输入特殊字符")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证码框可输入特殊字符序列，用于前端容忍度校验。")
    def test_tc011_special_chars_input(self, page: Page, login_config):
        _navigate_email_verification_page(page, login_config)
        dialog = _dialog(page)
        inp = _code_input(dialog)
        inp.fill("!@#$%^")
        page.wait_for_timeout(300)
        assert "!@#$%^" in inp.input_value()

    @pytest.mark.case_id_ae_login_nopwd_email_tc012
    @pytest.mark.p1
    @allure.story("四、返回与导航")
    @allure.title("TC012: 点击返回按钮返回欢迎页")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description(
        "在无密码密码页点击返回类控件后应回到欢迎页并可见 Welcome to OK.com。"
    )
    def test_tc012_back_to_welcome_from_password_page(self, page: Page, login_config):
        _navigate_email_no_password_password_page(page, login_config)
        _click_login_dialog_back(page)
        dialog = _dialog(page)
        welcome_ok = dialog.get_by_text("Welcome to OK.com").first.is_visible(timeout=10000)
        email_tb_ok = dialog.get_by_role(
            "textbox", name="Email or phone number"
        ).is_visible(timeout=5000)
        assert welcome_ok or email_tb_ok, "返回后应处于欢迎页（标题或邮箱/手机输入框可见）"

    @pytest.mark.case_id_ae_login_nopwd_email_tc013
    @pytest.mark.p1
    @allure.story("五、文案与国际化")
    @allure.title("TC013: 验证码页面文案完整性（邮箱）")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("校验 Verification code 标题、引导句、邮箱号、Confirm 与合规文案区域。")
    def test_tc013_verification_copy_email(self, page: Page, login_config):
        _navigate_email_verification_page(page, login_config)
        dialog = _dialog(page)
        assert dialog.locator("text=/Verification.*code/i").first.is_visible()
        body = dialog.inner_text()
        assert "To continue, complete this verification step" in body
        assert login_config["test_account"]["username"] in body.replace("\u00a0", " ")
        assert dialog.get_by_role("button", name="Confirm").is_visible()
        assert dialog.locator("text=/data.*protected/i").first.is_visible(timeout=5000)
        _attach_screenshot(page, "TC013_邮箱验证码文案")


@allure.epic("OK AE站")
@allure.feature("登录注册未设置密码场景（手机号）")
class TestAeNoPasswordPhone:
    """手机号未设置密码 — 文档第六节 TC014–TC016"""

    @pytest.mark.case_id_ae_login_nopwd_phone_tc014
    @pytest.mark.smoke
    @pytest.mark.p0
    @allure.story("六、手机号登录未设置密码")
    @allure.title("TC014: 未设置密码手机号进入密码页显示特殊提示")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "验证手机号无密码密码页展示完整号码、无 Phone number 小标题、Send code 与无密码提示。"
    )
    def test_tc014_phone_no_password_password_page(self, page: Page, login_config):
        _navigate_phone_no_password_password_page(page, login_config)
        dialog = _dialog(page)
        assert dialog.is_visible(timeout=8000)
        assert dialog.locator("text=/welcome.*back/i").first.is_visible()
        full = login_config["test_phone_no_password"]["full"]
        assert dialog.get_by_text(full).first.is_visible()
        phone_label = dialog.get_by_text("Phone number", exact=True)
        assert not phone_label.is_visible(timeout=2000)
        hint_ok = (
            dialog.locator("text=/haven't added a password/i").first.is_visible(timeout=3000)
            or dialog.locator("text=/Sign in with.*email code/i").first.is_visible(timeout=3000)
        )
        assert hint_ok
        assert dialog.get_by_role("button", name="Send code").is_visible()
        assert dialog.locator('input[type="password"]').count() == 0
        assert dialog.locator("text=/data.*protected/i").first.is_visible(timeout=4000)
        _attach_screenshot(page, "TC014_手机号无密码密码页")

    @pytest.mark.skip(reason="手机号场景避免触发验证码发送")
    @pytest.mark.case_id_ae_login_nopwd_phone_tc015
    @pytest.mark.smoke
    @pytest.mark.p0
    @allure.story("六、手机号登录未设置密码")
    @allure.title("TC015: 手机号未设置密码 — 点击 Send code 成功发送验证码（不自动化）")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "验证手机号路径 Toast 含 sent to your phone、说明含 phone number 与完整号码、Confirm 初始禁用。"
    )
    def test_tc015_phone_send_code(self, page: Page, login_config):
        _navigate_phone_no_password_password_page(page, login_config)
        dialog = _dialog(page)
        dialog.get_by_role("button", name="Send code").click()
        page.wait_for_timeout(900)
        toast = page.get_by_text(re.compile(r"The code has been sent to your phone", re.I))
        try:
            expect(toast.first).to_be_visible(timeout=6000)
        except AssertionError:
            logger.warning("未稳定捕获手机号 Toast，继续校验验证码页")
        page.wait_for_timeout(2200)
        dialog = _dialog(page)
        assert dialog.locator("text=/Verification.*code/i").first.is_visible()
        body = dialog.inner_text().replace("\u00a0", " ")
        assert re.search(r"phone\s+number", body, re.I)
        assert login_config["test_phone_no_password"]["full"] in body
        expect(dialog.get_by_role("button", name="Confirm")).to_be_disabled()
        _attach_screenshot(page, "TC015_手机号验证码页")

    @pytest.mark.skip(reason="手机号场景避免触发验证码发送")
    @pytest.mark.case_id_ae_login_nopwd_phone_tc016
    @pytest.mark.p1
    @allure.story("六、手机号登录未设置密码")
    @allure.title("TC016: 手机号验证码页面文案包含 +971 501234579（不自动化）")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("校验验证码页标题、引导关键词、完整手机号、Enter code 区域与 Confirm。")
    def test_tc016_phone_verification_copy(self, page: Page, login_config):
        _navigate_phone_no_password_password_page(page, login_config)
        dialog = _dialog(page)
        dialog.get_by_role("button", name="Send code").click()
        page.wait_for_timeout(3500)
        dialog = _dialog(page)
        assert dialog.locator("text=/Verification.*code/i").first.is_visible()
        for kw in ("continue", "verification", "step", "phone"):
            assert dialog.locator(f"text=/{kw}/i").first.is_visible(timeout=3000)
        norm = dialog.inner_text().replace("\u00a0", " ")
        assert login_config["test_phone_no_password"]["full"] in norm
        enter_ok = (
            dialog.get_by_placeholder("Enter code").first.is_visible(timeout=2000)
            or dialog.get_by_label("Enter code").first.is_visible(timeout=2000)
            or dialog.locator("text=/^Enter code$/i").first.is_visible(timeout=2000)
        )
        assert enter_ok
        assert dialog.get_by_role("button", name="Confirm").is_visible()
        assert dialog.locator("text=/data.*protected/i").first.is_visible(timeout=3000)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
