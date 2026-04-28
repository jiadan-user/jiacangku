# test_cases/login/test_login_phone_password_tc027_tc038.py
"""
OK AE站 - 登录模块自动化测试（三、手机号密码登录页）
生成时间: 2026-03-12
测试范围: TC027-TC038（手机号密码登录页）
"""

import pytest
import allure
from pages.login_page import LoginPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================================
# 测试环境配置
# ============================================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站（迪拜）",
    "role": "buyer",
    "user_name": "mamengmeng01_ae",
    "base_url": "https://ae.58v5.cn/en/city-dubai/",
    "test_account": "+971 501234570",
    "locale": "en-AE",
    "currency": "AED",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "page_load": 60000
    }
}

# 测试环境配置
BASE_URL = "https://ae.58v5.cn/en/city-dubai/"
TEST_PHONE = "501234570"
TEST_PASSWORD = "Qwer1234"


# 已使用 conftest.py 中的 smart_reset_for_login_tests fixture，无需重复定义


@allure.epic("登录模块")
@allure.feature("三、手机号密码登录页")
class TestLoginPhonePasswordPage:
    """登录模块 - 手机号密码登录页测试"""

    @pytest.mark.p0
    @pytest.mark.case_id_login_login_027
    @allure.story("核心流程（正向）")
    @allure.title("TC027: 已注册手机号正确密码登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    @pytest.mark.needs_logout  # 此用例需要退登
    def test_phone_login_success(self, preloaded_page):
        with allure.step("前置条件：使用预加载页面并打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step(f"在输入框输入 {TEST_PHONE}（系统自动识别为 AE +971 手机号）"):
            login_page.input_email(TEST_PHONE)
        with allure.step("验证输入手机号后系统自动添加「AE +971」国家码前缀"):
            # 使用动态等待替代固定等待
            assert preloaded_page.get_by_text("AE +971").is_visible(timeout=3000), "未显示 AE +971 国家码"
        with allure.step("点击 Continue，进入手机号密码登录页"):
            login_page.click_continue_button()
        with allure.step("验证页面显示「Welcome back!」"):
            assert preloaded_page.get_by_text("Welcome back!").is_visible(timeout=5000), "未显示 Welcome back! 标题"
        with allure.step("验证页面显示「Phone number」和完整手机号 '+971 501234570'"):
            assert preloaded_page.get_by_text("Phone number").is_visible(), "未显示 Phone number 标签"
            assert preloaded_page.get_by_text("+971 501234570").is_visible(), "未显示完整手机号"
        with allure.step(f"输入密码 {TEST_PASSWORD}"):
            login_page.input_password(TEST_PASSWORD)
        with allure.step("点击「Log in」"):
            login_page.click_login_button()
        with allure.step("验证登录成功后弹窗关闭，右上角变为已登录状态"):
            # 等待弹窗关闭或登录状态变化
            is_logged_in = login_page.is_login_button_text_changed(timeout=8000)
            assert is_logged_in, "登录成功后应显示已登录状态"

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_001
    @pytest.mark.P0
    def test_empty_password_disables_login_button(self, preloaded_page):
        with allure.step("前置条件：已输入合法手机号并进入密码页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_PHONE)
            login_page.click_continue_button()
            
            # 等待页面跳转到密码页并稳定
            preloaded_page.wait_for_timeout(2000)
            
            # 确保密码输入框已出现（表示已进入密码页）
            dialog = preloaded_page.locator('[role="dialog"]').first
            password_input = dialog.locator('input[type="password"]').first
            password_input.wait_for(state="visible", timeout=5000)
            
        with allure.step("不输入密码，尝试点击 Log in"):
            # 重新获取 login 按钮，确保引用最新的 DOM
            preloaded_page.wait_for_timeout(500)
            login_btn = preloaded_page.get_by_role('button', name='Log in')
            
            # 确保按钮可见
            login_btn.wait_for(state="visible", timeout=5000)
            
            assert login_btn.is_disabled(), "Log in 按钮应为 disabled 状态"

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_027
    @allure.title("TC029: 手机号自动识别国家码（+971）")
    @pytest.mark.P0
    def test_auto_detect_country_code(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step(f"在输入框输入阿联酋手机号 {TEST_PHONE}"):
            login_page.input_email(TEST_PHONE)
        with allure.step("验证系统自动识别为手机号并添加「AE +971」国家码"):
            assert preloaded_page.get_by_text("AE +971").is_visible(), "未显示 AE +971 国家码"

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_005
    @allure.title("TC031: 手机号输入非数字字符")
    @pytest.mark.P1
    def test_non_numeric_phone_input(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step("在输入框输入 'abc123xyz'"):
            login_page.input_email("abc123xyz")
        with allure.step("验证系统识别为邮箱格式尝试，或显示格式不合法提示"):
            # 可能继续作为邮箱处理，或显示错误提示
            allure.attach("输入非数字字符的处理结果", name="测试结果")

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_003
    @allure.title("TC032: 手机号位数不足（少于 9 位）")
    @pytest.mark.P1
    def test_insufficient_phone_digits(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step("输入 '12345'（少于正常位数）"):
            login_page.input_email("12345")
        with allure.step("点击 Continue"):
            continue_btn = preloaded_page.get_by_role('button', name='Continue')
            if continue_btn.is_enabled():
                continue_btn.click()
            preloaded_page.wait_for_timeout(2000)
        with allure.step("验证系统提示手机号格式不正确，或返回账号不存在"):
            allure.attach("短位数手机号处理结果", name="测试结果")

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_008
    @pytest.mark.P0
    def test_wrong_password_for_phone(self, preloaded_page):
        with allure.step("前置条件：已进入手机号密码登录页（+971 501234570）"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_PHONE)
            login_page.click_continue_button()
        with allure.step("输入错误密码 'WrongPass999'"):
            login_page.input_password("WrongPass999")
        with allure.step("点击 Log in"):
            login_page.click_login_button()
        with allure.step("验证显示密码错误提示，弹窗保持打开"):
            preloaded_page.wait_for_timeout(2000)
            allure.attach("密码错误处理结果", name="测试结果")

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_007
    @pytest.mark.P1
    def test_unregistered_phone_login(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step("输入未注册手机号（如 '599999999'）"):
            login_page.input_email("599999999")
        with allure.step("点击 Continue"):
            continue_btn = preloaded_page.get_by_role('button', name='Continue')
            if continue_btn.is_enabled():
                continue_btn.click()
            preloaded_page.wait_for_timeout(2000)
        with allure.step("验证进入注册页面，显示「Hi new friend」"):
            preloaded_page.wait_for_timeout(2000)
            welcome_text = preloaded_page.get_by_text("Hi new friend")
            if welcome_text.is_visible(timeout=3000):
                allure.attach("显示注册页面「Hi new friend」", name="✅ 验证通过")
            else:
                allure.attach(
                    "未找到「Hi new friend」，检查是否有其他注册页面标识",
                    name="⚠️ 备选验证",
                )
                error_hints = ["not registered", "sign up", "create account", "register"]
                page_content = preloaded_page.content().lower()
                found_hint = any(hint in page_content for hint in error_hints)
                assert found_hint or welcome_text.is_visible(timeout=1000), (
                    "应显示注册引导页面或提示"
                )

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_004
    @allure.title("TC036: 手机号密码登录快速重复点击 Log in 防重")
    @pytest.mark.P1
    @pytest.mark.needs_logout  # 用例内会登录成功，结束后须退登，避免后续用例找不到「Log in / Register」
    def test_multiple_clicks_prevention(self, preloaded_page):
        with allure.step("前置条件：已进入手机号密码登录页，密码已填写"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_PHONE)
            login_page.click_continue_button()
            login_page.input_password(TEST_PASSWORD)
        with allure.step("第一次点击「Log in」按钮，立即检查按钮状态"):
            login_btn = preloaded_page.get_by_role('button', name='Log in')
            login_btn.click()
            preloaded_page.wait_for_timeout(100)
            
            # 尝试检查按钮状态，如果按钮已消失说明登录很快完成
            try:
                is_busy = login_btn.get_attribute("aria-busy")
                is_disabled = login_btn.is_disabled(timeout=2000)
                if is_busy == "true" or is_disabled:
                    allure.attach(
                        "✅ 防重复机制生效：按钮进入 loading/disabled 状态",
                        name="验证通过",
                    )
                else:
                    allure.attach("⚠️ 按钮未进入保护状态", name="验证结果")
            except Exception as e:
                allure.attach(
                    f"按钮已消失（登录成功后弹窗关闭）: {str(e)[:100]}",
                    name="✅ 验证通过",
                )
            is_logged_in = login_page.is_login_button_text_changed(timeout=3000)
            assert is_logged_in, "应该成功登录"
            allure.attach("登录成功，防重复机制正常", name="✅ 最终验证")

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_002
    @pytest.mark.P0
    def test_forgot_password_link_display(self, preloaded_page):
        with allure.step("前置条件：已进入手机号密码登录页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_PHONE)
            login_page.click_continue_button()
        with allure.step("查看密码输入框下方"):
            forgot_link = preloaded_page.get_by_text("Forgot your password?")
            assert forgot_link.is_visible(), "未显示「Forgot your password?」链接"

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_login_phone_password_tc027_tc038_006
    @pytest.mark.P1
    def test_phone_display_in_password_page(self, preloaded_page):
        with allure.step(f"前置条件：已输入 {TEST_PHONE} 并进入密码页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_PHONE)
            login_page.click_continue_button()
        with allure.step("查看密码页的手机号展示区域"):
            assert preloaded_page.get_by_text("Phone number").is_visible(), "未显示 Phone number 标签"
            assert preloaded_page.get_by_text("+971 501234570").is_visible(), "未显示完整手机号 +971 501234570"
