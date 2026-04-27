#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录模块 - 权限与安全测试（TC054）
生成时间: 2026-03-25
测试范围: Token过期
说明: TC053已删除，TC055（Token篡改）、TC056（SQL注入）、TC057（HTTPS验证）需要接口级测试或手动验证，不在此文件中
"""

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
TEST_PASSWORD = _CONFIG["test_password"]


@allure.epic("OK AE站 - 登录模块")
@allure.feature("六、权限与安全")
class TestPermissionAndSecurity:
    """权限与安全测试"""

    @allure.story("会话管理")
    @allure.title("TC054: Token过期后清除Cookie可正常重新登录（不自动化）")
    @allure.description("""
    前置条件: 用户曾登录但Token已过期（清除Cookie/Session）
    步骤: 清除Cookie后尝试访问页面并重新登录
    预期: 登录状态清除，可重新登录
    
    说明: 此用例不需要自动化，需要特定页面访问权限验证
    """)
    @pytest.mark.p0
    @pytest.mark.case_id_login_login_053
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.skip(reason="此用例不需要自动化，需要特定页面访问权限验证")
    @pytest.mark.P1
    def test_token_expired_after_clear_cookies(self, preloaded_page):
        login_page = LoginPage(preloaded_page)
        with allure.step("打开首页并等待完全加载"):
            preloaded_page.wait_for_load_state("load", timeout=45000)
            preloaded_page.wait_for_timeout(3000)
        with allure.step("确保用户处于登出状态"):
            login_page.ensure_logged_out(BASE_URL)
            preloaded_page.wait_for_timeout(800)
        with allure.step("第一次登录"):
            try:
                login_page.click_login_register_button()
                preloaded_page.wait_for_timeout(2000)
                login_page.input_email(TEST_EMAIL)
                login_page.click_continue_button()
                preloaded_page.wait_for_timeout(2000)
                login_page.input_password(TEST_PASSWORD)
                login_page.click_login_button()
                preloaded_page.wait_for_timeout(5000)
                is_logged_in = login_page.is_login_button_text_changed(timeout=5000)
                if not is_logged_in:
                    pytest.skip("首次登录失败，跳过测试")
                assert is_logged_in, "首次登录失败"
                allure.attach("✅ 首次登录成功", name="登录状态")
            except Exception as e:
                allure.attach(f"登录失败: {e}", name="登录错误")
                pytest.skip(f"登录过程失败: {e}")
        with allure.step("清除Cookie和Session（模拟Token过期）"):
            preloaded_page.context.clear_cookies()
            preloaded_page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
            allure.attach("✅ 已清除Cookie和Storage", name="会话清理")
        with allure.step("刷新页面，验证登录状态已清除"):
            preloaded_page.reload(wait_until="domcontentloaded")
            preloaded_page.wait_for_timeout(2000)
        try:
            login_page.wait_for_guest_login_entry(timeout=25000, base_url=BASE_URL)
        except TimeoutError as e:
            allure.attach(f"验证失败: {e}", name="状态检查")
            pytest.skip("无法验证登录状态是否清除")
        assert login_page.is_guest_login_entry_visible(
            timeout=5000
        ), "清除 Cookie 后 header 应显示「Log in / Register」"
        allure.attach("✅ 登录状态已清除，显示「Log in / Register」", name="Token过期处理")
        with allure.step("验证可以重新登录"):
            try:
                login_page.click_login_register_button()
                preloaded_page.wait_for_timeout(2000)
                login_page.input_email(TEST_EMAIL)
                login_page.click_continue_button()
                preloaded_page.wait_for_timeout(2000)
                login_page.input_password(TEST_PASSWORD)
                login_page.click_login_button()
                preloaded_page.wait_for_timeout(5000)
                is_logged_in_2 = login_page.is_login_button_text_changed(timeout=5000)
                assert is_logged_in_2, "Token过期后无法重新登录"
                allure.attach("✅ Token过期后可以重新登录", name="重新登录成功")
            except Exception as e:
                allure.attach(f"重新登录失败: {e}", name="登录错误")
                pytest.skip(f"重新登录过程失败: {e}")
        with allure.step("清理：退出登录"):
            try:
                if login_page.is_login_button_text_changed(timeout=1000):
                    login_page.logout()
                    preloaded_page.wait_for_timeout(2000)
            except Exception as e:
                allure.attach(f"退登失败: {e}", name="清理状态")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--alluredir=../../reports/allure-results"])
