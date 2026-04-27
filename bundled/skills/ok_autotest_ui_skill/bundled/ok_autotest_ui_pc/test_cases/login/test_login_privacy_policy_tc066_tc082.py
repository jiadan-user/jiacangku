# test_cases/login/test_login_privacy_policy_tc066_tc082.py
"""
OK AE站 - 登录模块自动化测试（九、隐私协议与合规）
生成时间: 2026-03-12
测试范围: TC066-TC082（隐私协议与合规）
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

BASE_URL = "https://ae.58v5.cn/en/city-dubai/"
TEST_EMAIL = "mamengmeng02@58.com"
TEST_PASSWORD = "Qwer1234"


@allure.epic("登录模块")
@allure.feature("九、隐私协议与合规")
class TestLoginPrivacyPolicy:
    """登录模块 - 隐私协议与合规测试"""

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_023
    @allure.story("核心流程（正向）")
    @allure.title("TC066: 欢迎页底部隐私声明完整文案展示")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_privacy_statement_full_text_display(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step("查看弹窗底部隐私声明文案区域"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            privacy_text = dialog.get_by_text("By continuing, you accept OK's Terms of Use")
            assert privacy_text.is_visible(timeout=5000), "未显示隐私声明文案"
        with allure.step("验证「Terms of Use」为可点击的超链接样式"):
            terms_link = dialog.get_by_text("Terms of Use")
            assert terms_link.is_visible(), "未显示 Terms of Use 链接"
        with allure.step("验证「Privacy Policy」为可点击的超链接样式"):
            privacy_link = dialog.get_by_text("Privacy Policy")
            assert privacy_link.is_visible(), "未显示 Privacy Policy 链接"

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_029
    @allure.story("核心流程（正向）")
    @allure.title("TC067: 欢迎页点击 Terms of Use 链接跳转正确页面")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_terms_of_use_link_navigation(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step("点击底部文案中的「Terms of Use」链接"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            terms_link = dialog.get_by_text("Terms of Use", exact=False).first
            with preloaded_page.context.expect_page(timeout=10000) as new_page_info:
                terms_link.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded")
        with allure.step("验证在新标签页打开条款页面"):
            assert new_page is not None, "未打开新标签页"
            current_url = new_page.url
            allure.attach(current_url, name="跳转URL")
            assert "policy" in current_url or "terms" in current_url, f"URL 不符合预期: {current_url}"
        with allure.step("验证原登录弹窗保持打开状态"):
            assert dialog.is_visible(), "原登录弹窗应保持打开"
        new_page.close()

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_022
    @allure.story("核心流程（正向）")
    @allure.title("TC068: 欢迎页点击 Privacy Policy 链接跳转正确页面")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P1
    def test_privacy_policy_link_navigation(self, preloaded_page):
        with allure.step("前置条件：打开欢迎弹窗"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
        with allure.step("点击底部文案中的「Privacy Policy」链接"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            privacy_link = dialog.get_by_text("Privacy Policy", exact=False).first
            with preloaded_page.context.expect_page(timeout=10000) as new_page_info:
                privacy_link.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded")
        with allure.step("验证在新标签页打开隐私政策页面"):
            assert new_page is not None, "未打开新标签页"
            current_url = new_page.url
            allure.attach(current_url, name="跳转URL")
            assert "policy" in current_url or "privacy" in current_url, f"URL 不符合预期: {current_url}"
        with allure.step("验证原登录弹窗保持打开状态"):
            assert dialog.is_visible(), "原登录弹窗应保持打开"
        new_page.close()

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_024
    @allure.story("核心流程（正向）")
    @allure.title("TC069: 邮箱密码登录页底部隐私声明文案展示")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_privacy_statement_in_email_password_page(self, preloaded_page):
        with allure.step("前置条件：已进入邮箱密码登录页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
        with allure.step("查看密码登录页底部隐私声明区域"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            privacy_text = dialog.get_by_text("By continuing, you accept OK's Terms of Use")
            assert privacy_text.is_visible(timeout=5000), "未显示隐私声明文案"
        with allure.step("验证 Terms of Use 和 Privacy Policy 链接均可点击"):
            terms_link = dialog.get_by_text("Terms of Use")
            assert terms_link.is_visible(), "未显示 Terms of Use 链接"
            privacy_link = dialog.get_by_text("Privacy Policy")
            assert privacy_link.is_visible(), "未显示 Privacy Policy 链接"

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_025
    @allure.story("核心流程（正向）")
    @allure.title("TC070: 手机号密码登录页底部隐私声明文案展示")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_privacy_statement_in_phone_password_page(self, preloaded_page):
        with allure.step("前置条件：已进入手机号密码登录页"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email("501234570")
            login_page.click_continue_button()
        with allure.step("查看密码登录页底部隐私声明区域"):
            privacy_text = preloaded_page.get_by_text("By continuing, you accept OK's Terms of Use")
            is_visible = privacy_text.is_visible(timeout=3000)
            allure.attach(f"隐私声明可见: {is_visible}", name="显示状态")

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_028
    @allure.story("链接功能（负向 / 边界）")
    @allure.title("TC072: Terms of Use 链接在不同登录页面跳转一致")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_terms_of_use_consistent_across_pages(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        urls = []
        with allure.step("在欢迎页点击 Terms of Use，记录跳转 URL"):
            login_page.click_login_register_button()
            dialog = preloaded_page.locator('[role="dialog"]').first
            with preloaded_page.context.expect_page(timeout=10000) as new_page_info:
                dialog.get_by_text("Terms of Use").first.click()
            new_page = new_page_info.value
            urls.append(new_page.url)
            new_page.close()
            preloaded_page.reload(wait_until="domcontentloaded")
            preloaded_page.wait_for_timeout(1000)
        with allure.step("进入邮箱密码页，点击 Terms of Use，记录跳转 URL"):
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            dialog = preloaded_page.locator('[role="dialog"]').first
            with preloaded_page.context.expect_page(timeout=10000) as new_page_info:
                dialog.get_by_text("Terms of Use").first.click()
            new_page = new_page_info.value
            urls.append(new_page.url)
            new_page.close()
        with allure.step("验证所有页面的 Terms of Use 链接跳转到同一域名"):
            from urllib.parse import urlparse
            paths = [urlparse(url).path for url in urls]
            assert len(set(paths)) == 1, f"URL 路径不一致: {urls}"
            allure.attach(f"URL列表: {urls}\n路径: {paths[0]}", name="跳转一致性验证")

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_026
    @allure.story("链接功能（负向 / 边界）")
    @allure.title("TC074: Terms of Use 链接在新标签页打开后原弹窗状态保持")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_terms_link_preserves_dialog_state(self, preloaded_page):
        with allure.step("前置条件：欢迎弹窗已打开，已输入邮箱但未点击 Continue"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
        with allure.step("点击 Terms of Use 链接（在新标签页打开）"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            with preloaded_page.context.expect_page(timeout=10000) as new_page_info:
                dialog.get_by_text("Terms of Use").first.click()
            new_page = new_page_info.value
        with allure.step("关闭新打开的条款页标签"):
            new_page.close()
        with allure.step("验证原登录弹窗保持打开状态"):
            assert dialog.is_visible(), "原登录弹窗应保持打开"
        with allure.step("验证之前输入的邮箱内容保留"):
            input_box = preloaded_page.get_by_role('textbox', name='Email or phone number')
            assert input_box.input_value() == TEST_EMAIL, "输入内容应保留"
        with allure.step("验证 Continue 按钮状态保持为可点击"):
            continue_btn = preloaded_page.get_by_role('button', name='Continue')
            assert continue_btn.is_enabled(), "Continue 按钮应保持 enabled 状态"

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_020
    @allure.story("链接功能（负向 / 边界）")
    @allure.title("TC075: Privacy Policy 链接在新标签页打开后原弹窗状态保持")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.P2
    def test_privacy_link_preserves_dialog_state(self, preloaded_page):
        with allure.step("前置条件：已进入邮箱密码登录页，已输入密码"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            login_page.input_password(TEST_PASSWORD)
        with allure.step("点击 Privacy Policy 链接（在新标签页打开）"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            with preloaded_page.context.expect_page(timeout=10000) as new_page_info:
                dialog.get_by_text("Privacy Policy").first.click()
            new_page = new_page_info.value
        with allure.step("关闭新打开的隐私政策页标签"):
            new_page.close()
        with allure.step("验证原登录弹窗保持打开状态"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            assert dialog.is_visible(), "原登录弹窗应保持打开"
        with allure.step("验证 Log in 按钮状态保持为可点击"):
            login_btn = preloaded_page.get_by_role('button', name='Log in')
            assert login_btn.is_enabled(), "Log in 按钮应保持 enabled 状态"

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_066
    @allure.story("安全与合规")
    @allure.title("TC080: 登录页面不在 URL 中暴露密码（不自动化）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="此用例不需要自动化，属于安全检查类用例")
    @pytest.mark.P1
    def test_no_password_in_url(self, preloaded_page):
        with allure.step("前置条件：完成登录流程"):
            login_page = LoginPage(preloaded_page)
            login_page.click_login_register_button()
            login_page.input_email(TEST_EMAIL)
            login_page.click_continue_button()
            url_before = preloaded_page.url
            login_page.input_password(TEST_PASSWORD)
            url_after_input = preloaded_page.url
            login_page.click_login_button()
            preloaded_page.wait_for_timeout(2000)
            url_after_login = preloaded_page.url
        with allure.step("验证 URL 中不包含密码、token 等敏感信息明文"):
            assert TEST_PASSWORD not in url_before, "URL 中包含密码明文（输入前）"
            assert TEST_PASSWORD not in url_after_input, "URL 中包含密码明文（输入后）"
            assert TEST_PASSWORD not in url_after_login, "URL 中包含密码明文（登录后）"
            allure.attach(
                f"输入前: {url_before}\n输入后: {url_after_input}\n登录后: {url_after_login}",
                name="URL 变化记录",
            )

    @pytest.mark.p1
    @pytest.mark.case_id_login_login_021
    @allure.story("安全与合规")
    @allure.title("TC081: Terms of Use 和 Privacy Policy 链接使用 HTTPS 协议（不自动化）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.skip(reason="此用例不需要自动化，属于安全检查类用例")
    @pytest.mark.P1
    def test_privacy_links_use_https(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("前置条件：确保处于登出状态"):
            login_page.reset_login_state()
        try:
            login_register_visible = preloaded_page.get_by_text(
                "Log in / Register", exact=True
            ).is_visible(timeout=1000)
            if not login_register_visible:
                logger.info("检测到已登录状态，清除会话...")
                preloaded_page.context.clear_cookies()
                preloaded_page.evaluate(
                    "() => { localStorage.clear(); sessionStorage.clear(); }"
                )
                preloaded_page.reload(wait_until="domcontentloaded")
        except Exception as e:
            logger.debug(f"登录状态检查: {e}")
        with allure.step("打开欢迎弹窗"):
            login_page.click_login_register_button()
        with allure.step("检查 Terms of Use 链接的 href 属性"):
            dialog = preloaded_page.locator('[role="dialog"]').first
            terms_link = dialog.locator('a:has-text("Terms of Use")').first
            terms_href = terms_link.get_attribute('href')
            if terms_href:
                assert terms_href.startswith('https://'), f"Terms of Use 链接应使用 HTTPS: {terms_href}"
                allure.attach(terms_href, name="Terms of Use URL")
        with allure.step("检查 Privacy Policy 链接的 href 属性"):
            privacy_link = dialog.locator('a:has-text("Privacy Policy")').first
            privacy_href = privacy_link.get_attribute('href')
            if privacy_href:
                assert privacy_href.startswith('https://'), (
                    f"Privacy Policy 链接应使用 HTTPS: {privacy_href}"
                )
                allure.attach(privacy_href, name="Privacy Policy URL")
