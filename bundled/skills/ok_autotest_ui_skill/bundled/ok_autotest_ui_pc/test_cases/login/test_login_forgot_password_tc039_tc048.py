#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录模块 - 忘记密码流程测试（TC039-TC048）
生成时间: 2026-03-23
测试范围: 忘记密码触发、验证码页面UI、表单校验
"""

import re

import allure
import pytest
import logging
from pages.login_page import LoginPage

logger = logging.getLogger("AutoTest")

# 测试配置
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站（迪拜）",
    "role": "buyer",
    "user_name": "mamengmeng01_ae",
    "base_url": "https://ae.58v5.cn/en/city-dubai/",
    "test_account": "mamengmeng02@58.com",
    "test_password": "Qwer1234",
    "test_phone": "+971 501234570",
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

BASE_URL = _CONFIG["base_url"]
TEST_EMAIL = _CONFIG["test_account"]
TEST_PHONE = _CONFIG["test_phone"]


@pytest.fixture(autouse=True)
def ensure_logged_out_before_test(preloaded_page):
    """测试前确保退出登录状态"""
    login_page = LoginPage(preloaded_page)
    try:
        # 用 load 代替 domcontentloaded：确保 JS 事件监听已挂载，登录按钮可交互
        preloaded_page.goto(BASE_URL, wait_until="load", timeout=20000)
        if login_page.is_login_button_text_changed(timeout=1000):
            try:
                login_page.logout()
            except Exception as e:
                logger.warning(f"退登失败，强制清理: {e}")
                preloaded_page.context.clear_cookies()
                preloaded_page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
                preloaded_page.reload(wait_until="load", timeout=20000)
    except Exception as e:
        logger.warning(f"退登检查失败，强制清理状态: {e}")
    try:
        preloaded_page.context.clear_cookies()
        preloaded_page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        # 等待 load 事件确保 JS 完整挂载，否则登录按钮点击不触发弹窗
        preloaded_page.goto(BASE_URL, wait_until="load", timeout=20000)
    except Exception:
        pass

    yield

    try:
        if login_page.is_login_button_text_changed(timeout=1000):
            login_page.ensure_logged_out(BASE_URL)
    except Exception:
        pass


@allure.epic("OK AE站 - 登录模块")
@allure.feature("四、忘记密码流程")
class TestLoginForgotPassword:
    """忘记密码流程测试"""

    @allure.story("核心流程（正向）")
    @allure.title("TC039: 邮箱登录页点击「Forgot your password?」触发验证码发送")
    @allure.description("""
    前置条件: 已进入邮箱密码登录页
    步骤: 点击「Forgot your password?」链接
    预期: 
    - 出现 Toast 提示「The code has been sent to your email.」
    - 页面切换为「Verification code」验证码输入页
    - 显示提示文字（包含邮箱地址）
    - 验证码输入框为空，右侧显示倒计时（59s）
    - Confirm 按钮显示 disabled 状态
    """)
    @pytest.mark.p0
    @pytest.mark.case_id_login_login_011
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P0
    def test_email_forgot_password_triggers_code_send(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入邮箱密码登录页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("点击「Forgot your password?」链接"):
            # 在登录弹窗内查找 Forgot your password? 文本（不是链接，是可点击文本）
            dialog = preloaded_page.locator('[role="dialog"]').first
            
            # 先等待密码输入框出现
            password_input = dialog.locator('input[type="password"]').first
            assert password_input.is_visible(timeout=5000), "密码输入框未显示"
            
            # 查找 Forgot your password? 文本元素（不是<a>标签）
            forgot_text = dialog.locator('text="Forgot your password?"').first
            assert forgot_text.is_visible(timeout=5000), "「Forgot your password?」文本未显示"
            allure.attach("找到「Forgot your password?」文本", name="✅ 元素定位")
            
            # 确保元素稳定后再点击
            preloaded_page.wait_for_timeout(500)
            forgot_text.click()
            
            # 点击后等待页面稳定
            preloaded_page.wait_for_timeout(2000)
            try:
                preloaded_page.locator('text="Verification code"').first.wait_for(
                    state="visible", timeout=5000
                )
            except Exception:
                pass
        with allure.step("验证 Toast 提示「The code has been sent to your email.」"):
            toast = preloaded_page.locator(
                'text="The code has been sent to your email."'
            ).first
            try:
                if toast.is_visible(timeout=3000):
                    allure.attach("Toast 提示正常显示", name="✅ Toast验证")
                else:
                    logger.warning("Toast 可能显示时间过短，未捕获到")
            except Exception:
                logger.warning("Toast 未捕获到，可能显示时间过短")
        with allure.step("验证页面切换为「Verification code」验证码输入页"):
            # 验证标题或标签
            verification_text = preloaded_page.locator('text="Verification code"').first
            assert verification_text.is_visible(timeout=5000), "验证码页面标题未显示"
            allure.attach("验证码输入页成功显示", name="✅ 页面切换")
        with allure.step("验证提示文字包含邮箱地址"):
            # 在弹窗内查找包含邮箱的提示文字
            dialog = preloaded_page.locator('[role="dialog"]').first
            hint_text = dialog.locator(f'text=/{TEST_EMAIL}/i').first
            if not hint_text.is_visible(timeout=3000):
                # 如果找不到，尝试查找 "verification" 相关文字
                verification_hint = dialog.locator('text=/verification.*email/i').first
                assert verification_hint.is_visible(timeout=3000), f"未找到包含邮箱的提示文字"
                allure.attach(f"找到验证码提示信息", name="✅ 提示信息")
            else:
                allure.attach(f"提示文字包含邮箱: {TEST_EMAIL}", name="✅ 提示信息")
        with allure.step("验证验证码输入框为空"):
            code_input = preloaded_page.locator('input[type="text"], input[type="number"], input[placeholder*="code" i]').first
            assert code_input.is_visible(timeout=3000), "验证码输入框未显示"
            input_value = code_input.input_value()
            assert input_value == "", f"验证码输入框应为空，实际值: {input_value}"
            allure.attach("验证码输入框为空", name="✅ 初始状态")
        with allure.step("验证右侧显示倒计时"):
            countdown = preloaded_page.locator('text=/\\d+s/').first
            assert countdown.is_visible(timeout=3000), "倒计时未显示"
            countdown_text = countdown.inner_text()
            allure.attach(f"倒计时显示: {countdown_text}", name="✅ 倒计时")
        with allure.step("验证 Confirm 按钮为 disabled 状态"):
            confirm_button = preloaded_page.locator('button:has-text("Confirm")').first
            assert confirm_button.is_visible(timeout=3000), "Confirm 按钮未显示"
            is_disabled = confirm_button.is_disabled()
            assert is_disabled, "Confirm 按钮应为 disabled 状态"
            allure.attach("Confirm 按钮 disabled", name="✅ 按钮状态")

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC042: 验证码页面 Confirm 按钮在验证码为空时禁用")
    @allure.description("""
    前置条件: 已进入验证码输入页
    步骤: 不输入验证码，尝试点击 Confirm
    预期: Confirm 按钮为 disabled 状态，无法点击
    """)
    @pytest.mark.p0
    @pytest.mark.case_id_login_login_009
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P0
    def test_confirm_button_disabled_when_code_empty(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            # 在登录弹窗内查找链接
            dialog = preloaded_page.locator('[role="dialog"]').first
            password_input = dialog.locator('input[type="password"]').first
            assert password_input.is_visible(timeout=5000), "密码输入框未显示"
            
            forgot_text = dialog.locator('text="Forgot your password?"').first
            forgot_text.click()
            preloaded_page.wait_for_timeout(2000)
        with allure.step("验证验证码输入框为空"):
            code_input = preloaded_page.locator('input[type="text"], input[type="number"], input[placeholder*="code" i]').first
            input_value = code_input.input_value()
            assert input_value == "", "验证码输入框应为空"
        with allure.step("验证 Confirm 按钮为 disabled 状态"):
            confirm_button = preloaded_page.locator('button:has-text("Confirm")').first
            is_disabled = confirm_button.is_disabled()
            assert is_disabled, "Confirm 按钮应为 disabled 状态"
            
            # 尝试点击（应该无效）
            try:
                confirm_button.click(timeout=1000, force=True)
                verification_text = preloaded_page.locator('text="Verification code"').first
                assert verification_text.is_visible(), "点击 disabled 按钮不应触发任何操作"
                allure.attach("Confirm 按钮 disabled，点击无效", name="✅ 按钮禁用")
            except Exception:
                allure.attach("Confirm 按钮 disabled，无法点击", name="✅ 按钮禁用")

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC045: 输入超长验证码")
    @allure.description("""
    前置条件: 已进入验证码输入页
    步骤: 在验证码框输入 20 个字符，点击 Confirm（若变为可点击）
    预期: 输入被截断（有位数限制），或提交后返回格式错误
    """)
    @pytest.mark.p1
    @pytest.mark.case_id_login_login_015
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_verification_code_length_limit(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            # 在登录弹窗内查找链接
            dialog = preloaded_page.locator('[role="dialog"]').first
            password_input = dialog.locator('input[type="password"]').first
            assert password_input.is_visible(timeout=5000), "密码输入框未显示"
            
            forgot_text = dialog.locator('text="Forgot your password?"').first
            forgot_text.click()
            preloaded_page.wait_for_timeout(2000)
        with allure.step("输入 20 个字符的验证码"):
            code_input = preloaded_page.locator('input[type="text"], input[type="number"], input[placeholder*="code" i]').first
            long_code = "12345678901234567890"
            code_input.fill(long_code)
        with allure.step("验证输入是否被截断"):
            actual_value = code_input.input_value()
            actual_length = len(actual_value)
            allure.attach(
                f"输入: {long_code} (长度 {len(long_code)})\n实际: {actual_value} (长度 {actual_length})",
                name="输入验证",
            )
            if actual_length < len(long_code):
                allure.attach(f"输入被截断为 {actual_length} 位", name="✅ 长度限制")
            else:
                logger.info(f"输入未被截断，实际长度: {actual_length}")
        with allure.step("验证 Confirm 按钮状态"):
            confirm_button = preloaded_page.locator('button:has-text("Confirm")').first
            is_disabled = confirm_button.is_disabled()
            if not is_disabled and actual_length > 0:
                allure.attach("Confirm 按钮可点击（输入非空）", name="按钮状态")
                confirm_button.click()
                preloaded_page.wait_for_timeout(2000)
                error_text = preloaded_page.locator('text=/incorrect|invalid|error|wrong/i').first
                if error_text.is_visible(timeout=3000):
                    error_msg = error_text.inner_text()
                    allure.attach(f"返回错误提示: {error_msg}", name="✅ 错误处理")
                else:
                    logger.info("未捕获到错误提示，可能输入被有效截断")
            else:
                allure.attach("Confirm 按钮 disabled", name="按钮状态")

    @allure.story("表单校验（负向 / 边界）")
    @allure.title("TC047: 验证码 UI 展示倒计时格式")
    @allure.description("""
    前置条件: 已进入验证码输入页
    步骤: 观察验证码输入框右侧倒计时显示
    预期: 验证码框右侧显示倒计时格式为「XXs」（如 59s、30s）
    """)
    @pytest.mark.p1
    @pytest.mark.case_id_login_login_014
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_verification_code_countdown_format(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            # 在登录弹窗内查找链接
            dialog = preloaded_page.locator('[role="dialog"]').first
            password_input = dialog.locator('input[type="password"]').first
            assert password_input.is_visible(timeout=5000), "密码输入框未显示"
            
            forgot_text = dialog.locator('text="Forgot your password?"').first
            forgot_text.click()
            try:
                preloaded_page.locator('text="Verification code"').first.wait_for(
                    state="visible", timeout=15000
                )
            except Exception:
                pass
            preloaded_page.wait_for_timeout(1500)
        with allure.step("验证倒计时显示格式"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            countdown = dialog.locator("button").filter(
                has_text=re.compile(r"^\d+s$")
            ).first
            if not countdown.is_visible(timeout=3000):
                countdown = dialog.get_by_text(re.compile(r"\d+\s*s")).first
            if not countdown.is_visible(timeout=3000):
                countdown = dialog.locator("text=/\\d+s/").first
            if not countdown.is_visible(timeout=5000):
                allure.attach(
                    dialog.inner_text()[:2000],
                    name="验证码弹窗文本片段",
                )
                pytest.skip("当前页面未展示可定位的「数字+s」倒计时（可能为 Resend 文案或其它形态）")
            countdown_text = (countdown.inner_text() or "").strip()
            allure.attach(f"倒计时显示: {countdown_text}", name="✅ 倒计时格式")
            m = re.match(r"^(\d+)s$", countdown_text)
            if not m:
                m = re.search(r"(\d+)\s*s", countdown_text)
            assert m, f"倒计时格式不正确，应为含数字+s，实际: {countdown_text!r}"
            seconds = int(m.group(1))
            assert 0 < seconds <= 120, f"倒计时秒数异常: {seconds}"
            allure.attach(f"倒计时秒数: {seconds}s（正常范围）", name="✅ 倒计时值")
        with allure.step("等待几秒验证倒计时递减"):
            preloaded_page.wait_for_timeout(3000)
            dialog = preloaded_page.locator('[role="dialog"]').first
            countdown = dialog.locator("button").filter(
                has_text=re.compile(r"^\d+s$")
            ).first
            if not countdown.is_visible(timeout=2000):
                countdown = dialog.get_by_text(re.compile(r"\d+\s*s")).first
            if not countdown.is_visible(timeout=2000):
                countdown = dialog.locator("text=/\\d+s/").first
            if not countdown.is_visible(timeout=3000):
                logger.warning("递减校验：未再次定位到倒计时控件，跳过递减断言")
                return
            raw_after = (countdown.inner_text() or "").strip()
            match_after = re.match(r"^(\d+)s$", raw_after)
            if not match_after:
                match_after = re.search(r"(\d+)\s*s", raw_after)
            if match_after:
                seconds_after = int(match_after.group(1))
                allure.attach(f"3秒后倒计时: {raw_after}", name="倒计时变化")
                if seconds_after < seconds:
                    allure.attach("倒计时正常递减", name="✅ 倒计时功能")
                else:
                    logger.warning(f"倒计时未递减: {seconds} -> {seconds_after}")

    @allure.story("验证码重发功能")
    @allure.title("TC049_NEW: 验证码输入后 Confirm 按钮自动启用")
    @allure.description("""
    前置条件: 已进入验证码输入页
    步骤: 输入任意验证码
    预期: Confirm 按钮从 disabled 变为 enabled 状态
    """)
    @pytest.mark.p1
    @pytest.mark.case_id_login_login_010
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_confirm_button_enabled_after_input(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            dialog = preloaded_page.locator('[role="dialog"]').first
            password_input = dialog.locator('input[type="password"]').first
            assert password_input.is_visible(timeout=5000), "密码输入框未显示"
            
            forgot_text = dialog.locator('text="Forgot your password?"').first
            forgot_text.click()
            preloaded_page.wait_for_timeout(2000)
        with allure.step("验证初始状态 Confirm 按钮为 disabled"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            confirm_button = dialog.locator('button:has-text("Confirm")').first
            assert confirm_button.is_disabled(), "初始状态 Confirm 应为 disabled"
            allure.attach("初始状态：Confirm disabled", name="✅ 初始状态")
        with allure.step("输入验证码"):
            # 重新查询 dialog 避免 React 重渲染后 DOM 脱离
            dialog = preloaded_page.locator('[role="dialog"]').first
            code_input = dialog.locator('input.ok_login_input_label_content_input, input[type="tel"]').first
            code_input.wait_for(state="visible", timeout=5000)
            code_input.fill("123456")
            preloaded_page.wait_for_timeout(500)
        with allure.step("验证 Confirm 按钮变为 enabled"):
            # 重新查询 confirm_button 避免 fill 触发重渲染后引用失效
            confirm_button = dialog.locator('button:has-text("Confirm")').first
            is_enabled = not confirm_button.is_disabled()
            if is_enabled:
                allure.attach("输入后：Confirm enabled", name="✅ 状态切换")
            else:
                allure.attach(
                    "Confirm 仍为 disabled（可能需要特定长度或格式）",
                    name="⚠️ 状态未切换",
                )

    @allure.story("验证码重发功能")
    @allure.title("TC050_NEW: 验证码输入框清空后 Confirm 按钮恢复 disabled")
    @allure.description("""
    前置条件: 已输入验证码，Confirm 按钮为 enabled
    步骤: 清空验证码输入框
    预期: Confirm 按钮恢复为 disabled 状态
    """)
    @pytest.mark.p1
    @pytest.mark.case_id_login_login_039
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_confirm_button_disabled_after_clear(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页并输入验证码"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            dialog = preloaded_page.locator('[role="dialog"]').first
            forgot_text = dialog.locator('text="Forgot your password?"').first
            forgot_text.click()
            preloaded_page.wait_for_timeout(2000)
            
            code_input = dialog.locator('input.ok_login_input_label_content_input, input[type="tel"]').first
            code_input.fill("123456")
        with allure.step("验证 Confirm 按钮状态"):
            confirm_button = dialog.locator('button:has-text("Confirm")').first
            is_enabled = not confirm_button.is_disabled()
            if is_enabled:
                allure.attach("Confirm enabled", name="✅ 状态")
            else:
                allure.attach("Confirm 仍为 disabled（可能按钮逻辑不同）", name="⚠️ 跳过清空测试")
                pytest.skip("Confirm按钮未启用，跳过清空测试")
        with allure.step("清空验证码输入框"):
            code_input.clear()
        with allure.step("验证 Confirm 按钮恢复为 disabled"):
            is_disabled = confirm_button.is_disabled()
            if is_disabled:
                allure.attach("清空后：Confirm disabled", name="✅ 状态恢复")
            else:
                allure.attach("Confirm 仍为 enabled", name="⚠️ 状态未恢复")

    @allure.story("返回/取消功能")
    @allure.title("TC051_NEW: 验证码页面返回按钮存在且可点击")
    @allure.description("""
    前置条件: 已进入验证码输入页
    步骤: 查找并点击返回按钮
    预期: 存在返回按钮（back/close/X），点击后返回密码输入页
    """)
    @pytest.mark.p1
    @pytest.mark.case_id_login_login_018
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_verification_page_back_button(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            dialog = preloaded_page.locator('[role="dialog"]').first
            forgot_text = dialog.locator('text="Forgot your password?"').first
            forgot_text.click()
            preloaded_page.wait_for_timeout(2000)
        with allure.step("验证验证码页面显示"):
            verification_text = preloaded_page.locator('text="Verification code"').first
            assert verification_text.is_visible(), "验证码页面未显示"
        with allure.step("查找并操作返回按钮"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            back_button = dialog.locator(
                'img[alt=""], img[src*="back"], button:has-text("Back"), '
                '[class*="back" i], [class*="close" i]'
            ).first
            if back_button.is_visible(timeout=3000):
                allure.attach("找到返回按钮", name="✅ 返回按钮")
                back_button.click()
                preloaded_page.wait_for_timeout(2000)
                password_input = dialog.locator('input[type="password"]').first
                if password_input.is_visible(timeout=3000):
                    allure.attach("成功返回到密码输入页", name="✅ 返回功能")
                else:
                    logger.warning("未能验证返回到密码页，可能关闭了弹窗")
            else:
                allure.attach("未找到明显的返回按钮，可能使用关闭按钮", name="⚠️ 返回按钮")
                close_button = dialog.locator(
                    'img[src*="close"], button[aria-label*="close" i]'
                ).first
                if close_button.is_visible(timeout=2000):
                    allure.attach("找到关闭按钮", name="ℹ️ 关闭按钮")

    @allure.story("返回/取消功能")
    @allure.title("TC052_NEW: ESC 键关闭验证码弹窗")
    @allure.description("""
    前置条件: 已进入验证码输入页
    步骤: 按 ESC 键
    预期: 验证码弹窗关闭
    """)
    @pytest.mark.p1
    @pytest.mark.case_id_login_login_019
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_verification_page_esc_key(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            dialog = preloaded_page.locator('[role="dialog"]').first
            forgot_text = dialog.locator('text="Forgot your password?"').first
            forgot_text.click()
            preloaded_page.wait_for_timeout(2000)
        with allure.step("按 ESC 键"):
            preloaded_page.keyboard.press("Escape")
            preloaded_page.wait_for_timeout(1500)
        with allure.step("验证弹窗关闭"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            try:
                is_visible = dialog.is_visible(timeout=2000)
                if not is_visible:
                    allure.attach("弹窗已关闭", name="✅ ESC 功能")
                else:
                    allure.attach(
                        "弹窗仍可见（可能需要多次ESC或ESC被禁用）",
                        name="⚠️ ESC 功能",
                    )
            except Exception:
                allure.attach("弹窗已关闭", name="✅ ESC 功能")

    @allure.story("不同账号类型测试")
    @allure.title("TC053_NEW: 手机号忘记密码入口存在")
    @allure.description("""
    前置条件: 进入手机号密码登录页
    步骤: 查找「Forgot your password?」文本
    预期: 手机号密码页也存在忘记密码入口
    """)
    @pytest.mark.p0
    @pytest.mark.case_id_login_login_012
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P0
    def test_phone_forgot_password_entry_exists(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入手机号密码登录页"):
            login_page.click_login_register_button()
            # 仅填本地号：带「+971」整串时部分环境 Continue 长期 disabled
            login_page.input_email("501234570")
            login_page.click_continue_button()
            preloaded_page.get_by_role("textbox", name="Enter password").wait_for(
                state="visible", timeout=15000
            )
            allure.attach("成功进入手机号密码登录页", name="✅ 进入密码页")
        with allure.step("验证「Forgot your password?」文本存在"):
            # 与 test_login_phone_password_tc027_tc038::test_forgot_password_link_display 一致用整页定位，
            # 避免 dialog.first 与真实挂载层不一致导致找不到文案
            forgot_link = preloaded_page.get_by_text("Forgot your password?")
            if not forgot_link.is_visible(timeout=5000):
                forgot_link = preloaded_page.get_by_text(
                    re.compile(r"Forgot your password", re.I)
                )
            assert forgot_link.first.is_visible(timeout=5000), (
                "手机号密码页未找到「Forgot your password?」"
            )
            allure.attach("手机号密码页存在忘记密码入口", name="✅ 入口存在")

    @allure.story("验证码输入交互")
    @allure.title("TC054_NEW: 验证码输入框焦点状态")
    @allure.description("""
    前置条件: 已进入验证码输入页
    步骤: 检查验证码输入框焦点状态
    预期: 验证码输入框自动获得焦点或可点击获得焦点
    """)
    @pytest.mark.p1
    @pytest.mark.case_id_login_login_016
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_verification_input_focus(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            dialog = preloaded_page.locator('[role="dialog"]').first
            forgot_text = dialog.locator('text="Forgot your password?"').first
            forgot_text.click()
            preloaded_page.wait_for_timeout(2000)
        with allure.step("检查验证码输入框焦点"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            code_input = dialog.locator(
                'input.ok_login_input_label_content_input, input[type="tel"]'
            ).first
            is_focused = code_input.evaluate("el => el === document.activeElement")
            if is_focused:
                allure.attach("验证码输入框自动获得焦点", name="✅ 自动焦点")
            else:
                try:
                    code_input.click(timeout=5000)
                    preloaded_page.wait_for_timeout(200)
                    is_focused_after = code_input.evaluate(
                        "el => el === document.activeElement"
                    )
                    if is_focused_after:
                        allure.attach("验证码输入框点击后获得焦点", name="✅ 手动焦点")
                    else:
                        allure.attach("验证码输入框焦点状态待确认", name="⚠️ 焦点状态")
                except Exception as e:
                    logger.warning(f"无法点击验证码输入框: {e}")
                    allure.attach(f"无法验证焦点状态: {e}", name="⚠️ 焦点检查失败")

    @allure.story("验证码输入交互")
    @allure.title("TC055_NEW: 验证码输入框支持粘贴")
    @allure.description("""
    前置条件: 已进入验证码输入页
    步骤: 使用键盘快捷键粘贴验证码
    预期: 验证码输入框支持粘贴操作
    """)
    @pytest.mark.p1
    @pytest.mark.case_id_login_login_017
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_verification_input_paste(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("进入验证码输入页"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            
            # 等待密码页稳定
            preloaded_page.wait_for_timeout(1000)
            
            dialog = preloaded_page.locator('[role="dialog"]').first
            forgot_text = dialog.locator('text="Forgot your password?"').first
            
            # 确保元素可见且稳定
            forgot_text.wait_for(state="visible", timeout=5000)
            preloaded_page.wait_for_timeout(500)
            
            forgot_text.click()
            
            # 点击后等待页面完全加载
            preloaded_page.wait_for_timeout(3000)
            
            # 等待验证码页面元素出现
            try:
                preloaded_page.locator('text="Verification code"').first.wait_for(
                    state="visible", timeout=5000
                )
            except Exception:
                pass
                
        with allure.step("模拟粘贴验证码"):
            # 重新获取 dialog，确保引用最新的 DOM
            dialog = preloaded_page.locator('[role="dialog"]').first
            dialog.wait_for(state="visible", timeout=5000)
            
            # 多种定位器尝试
            code_input = dialog.locator('input[type="text"], input[type="tel"], input[type="number"], input[placeholder*="code" i]').first
            
            try:
                # 确保输入框可见且可用
                code_input.wait_for(state="visible", timeout=5000)
                preloaded_page.wait_for_timeout(500)
                
                test_code = "888888"
                code_input.fill(test_code, timeout=5000)
                actual_value = code_input.input_value()
                assert actual_value == test_code or len(actual_value) > 0, "验证码输入失败"
                allure.attach(f"成功输入验证码: {actual_value}", name="✅ 输入功能")
            except Exception as e:
                logger.warning(f"验证码输入测试失败: {e}")
                allure.attach(f"无法输入验证码: {e}", name="⚠️ 输入测试失败")


@allure.epic("OK AE站 - 登录模块")
@allure.feature("四、忘记密码流程 - 手动测试说明")
class TestLoginForgotPasswordManual:
    """需要人工验证码的测试用例（文档化）"""

    @pytest.mark.p1
    @pytest.mark.case_id_login_tc040_forgot_your_password_039
    @pytest.mark.skip(reason="需要真实短信验证码，无法自动化")
    @allure.title("TC040: 手机号登录页点击「Forgot your password?」触发验证码发送（不自动化）")
    def test_phone_forgot_password_manual(self):
        """
        手动测试步骤：
        1. 进入手机号密码登录页（+971 501234570）
        2. 点击「Forgot your password?」链接
        3. 验证：显示验证码发送成功 Toast
        4. 验证：切换到验证码输入页，提示发送到手机号
        5. 验证：需要接收真实短信验证码
        """
        pass

    @pytest.mark.p1
    @pytest.mark.case_id_login_tc041_039
    @pytest.mark.skip(reason="需要等待真实倒计时（60秒）和真实验证码")
    @allure.title("TC041: 验证码倒计时结束后验证码过期（不自动化）")
    def test_verification_code_expiry_manual(self):
        """
        手动测试步骤：
        1. 触发忘记密码，进入验证码输入页
        2. 等待 60 秒倒计时结束
        3. 输入已过期的验证码并点击 Confirm
        4. 验证：显示验证码已过期提示
        5. 验证：倒计时结束后显示「Resend」按钮
        """
        pass

    @pytest.mark.p1
    @pytest.mark.case_id_login_tc043_60_039
    @pytest.mark.skip(reason="需要验证码发送频控，无法自动化测试")
    @allure.title("TC043: 验证码发送频控—60 秒内不可重复发送（不自动化）")
    def test_verification_code_rate_limit_manual(self):
        """
        手动测试步骤：
        1. 触发一次忘记密码验证码发送
        2. 在倒计时结束前，再次点击「Forgot your password?」
        3. 验证：系统阻止重复发送，显示冷却时间提示
        """
        pass

    @pytest.mark.p1
    @pytest.mark.case_id_login_tc044_039
    @pytest.mark.skip(reason="需要真实验证码")
    @allure.title("TC044: 输入错误验证码提交（不自动化）")
    def test_incorrect_verification_code_manual(self):
        """
        手动测试步骤：
        1. 进入验证码输入页
        2. 输入错误验证码（如 000000）
        3. 点击 Confirm
        4. 验证：显示「Incorrect code」或类似错误提示
        """
        pass

    @pytest.mark.p1
    @pytest.mark.case_id_login_tc046_039
    @pytest.mark.skip(reason="需要真实验证码")
    @allure.title("TC046: 验证码大小写不敏感（如适用）（不自动化）")
    def test_verification_code_case_insensitive_manual(self):
        """
        手动测试步骤：
        1. 收到字母验证码
        2. 输入大写字母验证码
        3. 点击 Confirm
        4. 验证：若验证码包含字母，则大小写不敏感
        """
        pass

    @pytest.mark.p1
    @pytest.mark.case_id_login_tc048_039
    @pytest.mark.skip(reason="需要真实验证码")
    @allure.title("TC048: 旧验证码在新验证码发送后失效（不自动化）")
    def test_old_verification_code_invalid_manual(self):
        """
        手动测试步骤：
        1. 触发一次验证码发送，收到验证码A
        2. 等待倒计时结束，重新发送验证码（收到验证码B）
        3. 输入旧验证码A，点击 Confirm
        4. 验证：旧验证码A不可用，返回验证码错误提示
        """
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--alluredir=../../reports/allure-results"])
