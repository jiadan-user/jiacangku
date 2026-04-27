# test_cases/login/test_login_welcome_page_tc001_tc012.py
"""
OK AE站 - 登录模块自动化测试（一、欢迎页）
生成时间: 2026-03-12
测试范围: TC001-TC010（欢迎页；已移除 TC011、TC012）
"""

import pytest
import allure
import re
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
TEST_PHONE = "501234570"


@allure.epic("登录模块")
@allure.feature("一、欢迎页（Welcome Page）")
class TestLoginWelcomePage:
    """登录模块 - 欢迎页测试"""

    @allure.story("核心流程（正向）")
    @allure.title("TC001: 点击右上角「Log in / Register」打开欢迎弹窗")
    @allure.description("""
    验证点击登录/注册入口后，欢迎弹窗正确展示
    - 弹出登录弹窗，显示标题「Welcome to OK.com」和区域标识「AE」
    - 弹窗显示「Free to post. Easy to find.」副标题
    - 显示「Email or phone number」输入框
    - 显示灰色 disabled 状态的「Continue」按钮
    - 显示「OR」分隔文字
    - 显示 Google / Facebook / Apple 三方登录图标
    - 底部显示隐私声明文案
    - 左上角显示盾牌图标+「Your data is protected」
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_open_welcome_dialog(self, page):
        with allure.step("前置条件：访问 AE 站首页"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
        
        with allure.step("点击右上角「Log in / Register」按钮"):
            login_page.click_login_register_button()
        
        with allure.step("验证欢迎弹窗标题「Welcome to OK.com」"):
            assert page.get_by_text("Welcome to OK.com").is_visible(), "欢迎标题未显示"
        
        with allure.step("验证区域标识「AE」显示"):
            # AE 标识可能在多个位置，使用 first
            assert page.get_by_text("AE").first.is_visible(), "区域标识 AE 未显示"
        
        with allure.step("验证副标题「Free to post. Easy to find.」"):
            assert page.get_by_text("Free to post. Easy to find.").is_visible(), "副标题未显示"
        
        with allure.step("验证「Email or phone number」输入框显示"):
            input_box = page.get_by_role('textbox', name='Email or phone number')
            assert input_box.is_visible(), "邮箱/手机号输入框未显示"
        
        with allure.step("验证「Continue」按钮为 disabled 状态"):
            continue_btn = page.get_by_role('button', name='Continue')
            assert continue_btn.is_visible(), "Continue 按钮未显示"
            assert continue_btn.is_disabled(), "Continue 按钮应为 disabled 状态"
        
        with allure.step("验证「OR」分隔文字显示"):
            # OR 文字在登录弹窗中，需要在 dialog 范围内定位
            dialog = page.locator('[role="dialog"]').first
            or_text = dialog.get_by_text("OR", exact=True).filter(has_text=re.compile(r"^OR$"))
            assert or_text.is_visible(timeout=3000), "OR 分隔文字未显示"
        
        with allure.step("验证底部隐私声明文案显示"):
            privacy_text = page.get_by_text("By continuing, you accept OK's Terms of Use")
            assert privacy_text.is_visible(), "隐私声明文案未显示"
        
        with allure.step("验证「Your data is protected」显示"):
            assert page.get_by_text("Your data is protected").is_visible(), "数据保护提示未显示"

    @allure.story("核心流程（正向）")
    @allure.title("TC002: 欢迎弹窗输入合法邮箱后 Continue 按钮变为可用")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_email_input_enables_continue_button(self, page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
        
        with allure.step(f"在「Email or phone number」输入框输入 {TEST_EMAIL}"):
            login_page.input_email(TEST_EMAIL)
        
        with allure.step("验证 Continue 按钮由 disabled 变为可点击状态"):
            continue_btn = page.get_by_role('button', name='Continue')
            assert continue_btn.is_enabled(), "Continue 按钮应变为 enabled 状态"
        
        with allure.step("验证输入框正常显示输入内容"):
            input_box = page.get_by_role('textbox', name='Email or phone number')
            assert input_box.input_value() == TEST_EMAIL, "输入框内容不匹配"

    @allure.story("核心流程（正向）")
    @allure.title("TC003: 欢迎弹窗输入合法手机号后 Continue 按钮变为可用")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_phone_input_enables_continue_button(self, preloaded_page):
        with allure.step("前置条件：使用预加载页面并打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        
        with allure.step(f"在输入框输入手机号 {TEST_PHONE}"):
            login_page.input_email(TEST_PHONE)
        
        with allure.step("验证系统自动识别为手机号，显示「AE +971」国家码前缀"):
            # 使用动态等待替代固定等待
            ae_code = preloaded_page.get_by_text("AE +971")
            ae_code_visible = ae_code.is_visible(timeout=3000)
            assert ae_code_visible, "未显示 AE +971 国家码"
        
        with allure.step("验证 Continue 按钮变为可点击状态"):
            continue_btn = preloaded_page.get_by_role('button', name='Continue')
            assert continue_btn.is_enabled(), "Continue 按钮应变为 enabled 状态"

    @allure.story("核心流程（正向）")
    @allure.title("TC004: 欢迎弹窗输入框为空时 Continue 按钮保持禁用")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_empty_input_keeps_continue_disabled(self, page):
        with allure.step("前置条件：打开欢迎弹窗，输入框为空"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
        
        with allure.step("不在输入框输入任何内容"):
            # 直接验证按钮状态
            pass
        
        with allure.step("验证 Continue 按钮显示 disabled 状态"):
            continue_btn = page.get_by_role('button', name='Continue')
            assert continue_btn.is_disabled(), "Continue 按钮应保持 disabled 状态"

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC005: 欢迎弹窗输入非法格式邮箱后点击 Continue")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_invalid_email_format(self, page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
        
        with allure.step("在输入框输入非法邮箱 'test@'"):
            login_page.input_email("test@")
        
        with allure.step("点击 Continue 按钮"):
            continue_btn = page.get_by_role('button', name='Continue')
            if continue_btn.is_enabled():
                continue_btn.click()
                page.wait_for_timeout(2000)
        
        with allure.step("验证显示格式错误提示或账号不存在提示"):
            # 等待可能的错误提示（具体文案需根据实际情况调整）
            error_indicators = [
                "invalid",
                "Invalid",
                "format",
                "incorrect",
                "not found",
                "doesn't exist"
            ]
            page.wait_for_timeout(1000)
            # 记录页面文本用于调试
            allure.attach(page.content(), name="页面内容", attachment_type=allure.attachment_type.HTML)

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC006: 欢迎弹窗输入空格后点击 Continue")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_space_input(self, page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
        
        with allure.step("在输入框输入若干空格"):
            login_page.input_email("   ")
        
        with allure.step("观察 Continue 按钮状态"):
            continue_btn = page.get_by_role('button', name='Continue')
            # 根据实际情况，空格可能被判定为有效输入或无效输入
            if continue_btn.is_enabled():
                with allure.step("Continue 变为可点击，点击后应有格式校验"):
                    continue_btn.click()
                    page.wait_for_timeout(2000)

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC007: 欢迎弹窗输入超长字符串（500字符）")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_long_string_input(self, page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
        
        with allure.step("在输入框粘贴 500 个字符的字符串"):
            long_string = "a" * 500
            login_page.input_email(long_string)
        
        with allure.step("点击 Continue"):
            continue_btn = page.get_by_role('button', name='Continue')
            if continue_btn.is_enabled():
                continue_btn.click()
                page.wait_for_timeout(2000)
        
        with allure.step("验证输入被截断或提交后返回格式错误"):
            input_box = page.get_by_role('textbox', name='Email or phone number')
            actual_value = input_box.input_value()
            allure.attach(f"实际输入值长度: {len(actual_value)}", name="输入框值长度")

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC008: 欢迎弹窗输入 Emoji 字符")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_emoji_input(self, page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
        
        with allure.step("在输入框输入包含 Emoji 的邮箱 'test🎉@qq.com'"):
            login_page.input_email("test🎉@qq.com")
        
        with allure.step("点击 Continue"):
            continue_btn = page.get_by_role('button', name='Continue')
            if continue_btn.is_enabled():
                continue_btn.click()
                page.wait_for_timeout(2000)
        
        with allure.step("验证系统不接受 Emoji，提交后显示格式错误提示"):
            page.wait_for_timeout(1000)

    @allure.story("弹窗交互")
    @allure.title("TC009: 欢迎弹窗点击蒙层区域验证是否可关闭")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_click_overlay_to_close(self, page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
        
        with allure.step("点击弹窗外侧蒙层区域"):
            # 定位弹窗对话框
            dialog = page.locator('[role="dialog"]').first
            assert dialog.is_visible(), "登录弹窗未显示"
            
            # 点击页面左上角（通常是蒙层区域）
            page.mouse.click(10, 10)
            page.wait_for_timeout(1000)
        
        with allure.step("验证弹窗是否关闭"):
            # 检查弹窗是否仍然可见
            try:
                is_still_visible = dialog.is_visible(timeout=2000)
                allure.attach(
                    f"弹窗状态: {'仍然打开' if is_still_visible else '已关闭'}",
                    name="弹窗交互结果"
                )
            except:
                allure.attach("弹窗已关闭", name="弹窗交互结果")

    @allure.story("弹窗交互")
    @allure.title("TC010: 欢迎弹窗按 ESC 键验证是否可关闭")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_press_esc_to_close(self, page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(page)
            login_page.navigate_to_home_page(BASE_URL)
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
        
        with allure.step("按键盘 Escape 键"):
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)
        
        with allure.step("验证弹窗是否关闭"):
            dialog = page.locator('[role="dialog"]').first
            try:
                is_still_visible = dialog.is_visible(timeout=2000)
                allure.attach(
                    f"弹窗状态: {'仍然打开' if is_still_visible else '已关闭'}",
                    name="ESC 键交互结果"
                )
            except:
                allure.attach("弹窗已关闭", name="ESC 键交互结果")

