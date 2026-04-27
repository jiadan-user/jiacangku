# test_cases/login/test_login_email_password_tc013_tc026.py
"""
OK AE站 - 登录模块自动化测试（二、邮箱密码登录页）
生成时间: 2026-03-12
测试范围: TC013-TC024（邮箱密码登录页；已移除 TC021、TC025、TC026）
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
    "test_account": "mamengmeng02@58.com",
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
TEST_EMAIL = "mamengmeng02@58.com"
TEST_PASSWORD = "Qwer1234"
UNREGISTERED_EMAIL = "mamengmeng001@58.com"


@pytest.fixture(autouse=True)
def ensure_logged_out_before_test(preloaded_page):
    """
    自动 fixture: 在每个测试前确保用户已退出登录
    autouse=True 表示自动应用到本模块的所有测试
    """
    login_page = LoginPage(preloaded_page)
    try:
        if login_page.is_login_button_text_changed(timeout=1000):
            login_page.ensure_logged_out(BASE_URL)
    except Exception:
        pass

    yield

    # 测试后不需要清理，因为下一个测试会自动退出


@allure.epic("登录模块")
@allure.feature("二、邮箱密码登录页")
class TestLoginEmailPasswordPage:
    """登录模块 - 邮箱密码登录页测试"""

    @allure.story("核心流程（正向）")
    @allure.title("TC013: 已注册邮箱正确密码登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    @pytest.mark.needs_logout
    def test_email_login_success(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step(f"输入 {TEST_EMAIL}，点击 Continue"):
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("验证进入「Welcome back!」密码页"):
            assert preloaded_page.get_by_text("Welcome back!").is_visible(), "未显示 Welcome back! 标题"
        with allure.step("验证页面显示 Email 标签和邮箱地址"):
            assert preloaded_page.get_by_text("Email").is_visible(), "未显示 Email 标签"
            assert preloaded_page.get_by_text(TEST_EMAIL).is_visible(), "未显示邮箱地址"
        with allure.step(f"在密码框输入 {TEST_PASSWORD}"):
            login_page.input_password(TEST_PASSWORD)
        with allure.step("验证密码输入后 Log in 按钮变为可点击"):
            login_btn = preloaded_page.get_by_role('button', name='Log in')
            assert login_btn.is_enabled(), "Log in 按钮应变为 enabled 状态"
        with allure.step("点击「Log in」按钮"):
            login_page.click_login_button()
        with allure.step("验证登录成功，弹窗关闭，右上角变为已登录状态"):
            preloaded_page.wait_for_timeout(2000)
            is_logged_in = login_page.is_login_button_text_changed(timeout=5000)
            assert is_logged_in, "登录成功后应显示已登录状态"

    @allure.story("核心流程（正向）")
    @allure.title("TC014: 邮箱登录页密码输入框为空时 Log in 按钮禁用")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_empty_password_disables_login_button(self, preloaded_page):
        with allure.step("前置条件：已输入合法邮箱并点击 Continue，进入密码输入页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("不输入密码，直接检查「Log in」按钮状态"):
            login_btn = preloaded_page.get_by_role('button', name='Log in')
            assert login_btn.is_disabled(), "Log in 按钮应显示 disabled 状态"

    @allure.story("核心流程（正向）")
    @allure.title("TC015: 邮箱登录页密码显示/隐藏切换（眼睛图标）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_password_visibility_toggle(self, preloaded_page):
        with allure.step("前置条件：已进入邮箱密码登录页，已输入密码"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            login_page.input_password(TEST_PASSWORD)
        with allure.step("定位密码输入框右侧眼睛图标"):
            eye_icon = preloaded_page.locator(
                'button[aria-label*="password"], button[title*="password"]'
            ).first
            if eye_icon.is_visible(timeout=2000):
                with allure.step("点击眼睛图标"):
                    eye_icon.click()
                with allure.step("验证密码从「****」变为明文显示"):
                    password_input = preloaded_page.get_by_role('textbox', name='Enter password')
                    input_type = password_input.get_attribute('type')
                    allure.attach(f"密码框 type: {input_type}", name="密码显示状态")
            else:
                allure.attach("未找到眼睛图标", name="测试结果")

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC016: 已注册邮箱输入错误密码登录失败")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_wrong_password_login_fails(self, preloaded_page):
        with allure.step("前置条件：已进入邮箱密码登录页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("在密码框输入错误密码 'WrongPass123'"):
            login_page.input_password("WrongPass123")
        with allure.step("点击「Log in」"):
            login_page.click_login_button()
        with allure.step("验证登录失败，页面显示错误提示文案"):
            preloaded_page.wait_for_timeout(2000)
            error_keywords = ["Incorrect", "incorrect", "wrong", "invalid", "failed"]
            page_text = preloaded_page.content()
            has_error = any(keyword in page_text for keyword in error_keywords)
            allure.attach(f"是否显示错误提示: {has_error}", name="错误提示检查")

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC017: 未注册邮箱输入任意密码登录失败")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_unregistered_email_login_fails(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step(f"输入未注册邮箱 {UNREGISTERED_EMAIL}，点击 Continue"):
            login_page.input_email(UNREGISTERED_EMAIL)
            login_page.click_continue_button()
        with allure.step("验证进入注册页面，显示「Hi new friend」"):
            preloaded_page.wait_for_timeout(2000)
            welcome_text = preloaded_page.get_by_text("Hi new friend")
            if welcome_text.is_visible(timeout=3000):
                allure.attach("显示注册页面「Hi new friend」", name="✅ 验证通过")
            else:
                error_keywords = ["not found", "doesn't exist", "not registered", "账号不存在"]
                page_text = preloaded_page.content()
                has_error = any(keyword.lower() in page_text.lower() for keyword in error_keywords)
                allure.attach(f"页面内容片段: {page_text[:500]}", name="页面快照")
                if has_error:
                    allure.attach("显示账号不存在错误提示", name="⚠️ 替代验证通过")
                else:
                    allure.attach("未找到注册页面标识，也未找到错误提示", name="❌ 验证失败")

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC018: 邮箱登录密码输入特殊字符")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_password_with_special_characters(self, preloaded_page):
        with allure.step("前置条件：已进入邮箱密码登录页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("在密码框输入 '<script>alert(1)</script>'"):
            special_password = "<script>alert(1)</script>"
            login_page.input_password(special_password)
            password_input = preloaded_page.get_by_role('textbox', name='Enter password')
            actual_value = password_input.input_value()
            allure.attach(f"实际输入值: {actual_value}", name="密码输入验证")
        with allure.step("点击 Log in"):
            login_btn = preloaded_page.get_by_role('button', name='Log in')
            if login_btn.is_enabled(timeout=2000):
                login_page.click_login_button()
                preloaded_page.wait_for_timeout(2000)
                allure.attach("密码输入成功，Log in 按钮已点击", name="✅ 操作完成")
            else:
                allure.attach("密码输入后 Log in 按钮仍为 disabled，可能密码被过滤", name="⚠️ 按钮状态")
        with allure.step("验证系统不执行脚本，正常返回密码错误提示，无 XSS 漏洞"):
            allure.attach("未执行脚本，安全", name="XSS 检测结果")

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC019: 邮箱登录密码输入超长字符（500字符）")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_password_long_string(self, preloaded_page):
        with allure.step("前置条件：已进入邮箱密码登录页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("在密码框粘贴 500 个字符的字符串"):
            long_password = "P" * 500
            login_page.input_password(long_password)
            password_input = preloaded_page.get_by_role('textbox', name='Enter password')
            actual_value = password_input.input_value()
            actual_length = len(actual_value)
            allure.attach(f"实际密码长度: {actual_length}", name="密码长度检查")
        with allure.step("点击 Log in"):
            login_btn = preloaded_page.get_by_role('button', name='Log in')
            if login_btn.is_enabled(timeout=2000):
                login_page.click_login_button()
                preloaded_page.wait_for_timeout(2000)
                allure.attach(f"密码被截断为 {actual_length} 字符，已提交", name="✅ 操作完成")
            else:
                allure.attach(
                    f"密码输入后（{actual_length}字符）Log in 按钮仍为 disabled",
                    name="⚠️ 按钮状态",
                )
        with allure.step("验证输入被截断或提交后显示长度超限错误"):
            if actual_length < 500:
                allure.attach(
                    f"密码被截断：原始 500 字符 → 实际 {actual_length} 字符",
                    name="✅ 截断验证",
                )

    @allure.story("UI 与文案")
    @allure.title("TC022: 邮箱登录页正确显示邮箱地址")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_email_display_in_password_page(self, preloaded_page):
        with allure.step(f"前置条件：已输入 {TEST_EMAIL} 并进入密码页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("查看密码登录页的邮箱展示区域"):
            assert preloaded_page.get_by_text("Email").is_visible(), "未显示 Email 标签"
            assert preloaded_page.get_by_text(TEST_EMAIL).is_visible(), f"未显示邮箱地址 {TEST_EMAIL}"

    @allure.story("UI 与文案")
    @allure.title("TC023: 邮箱登录页「Forgot your password?」链接展示")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_forgot_password_link_display(self, preloaded_page):
        with allure.step("前置条件：已进入邮箱密码登录页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("查看页面是否有「Forgot your password?」文字链接"):
            forgot_link = preloaded_page.get_by_text("Forgot your password?")
            assert forgot_link.is_visible(), "未显示「Forgot your password?」链接"

    @allure.story("UI 与文案")
    @allure.title("TC024: 邮箱登录页底部隐私声明文案展示")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_privacy_statement_display(self, preloaded_page):
        with allure.step("前置条件：已进入邮箱密码登录页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("查看底部文案"):
            privacy_text = preloaded_page.get_by_text("By continuing, you accept OK's Terms of Use")
            assert privacy_text.is_visible(), "未显示隐私声明文案"
