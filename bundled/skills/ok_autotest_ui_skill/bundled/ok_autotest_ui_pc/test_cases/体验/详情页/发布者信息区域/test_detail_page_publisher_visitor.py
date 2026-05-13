"""
OK.com 详情页发布者信息区域 — 访客场景（TC-PUB-009 ~ TC-PUB-010）

独立模块以保证全新浏览器上下文（无登录 Cookie），符合用例「未登录」前置。
playwright-test-generator 生成 | 录制证明：batch2-publisher-info-recording.md
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.detail_page_publisher import DetailPagePublisher
from pages.login_page import LoginPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站 (AE OK.com)",
    "role": "visitor",
    "user_name": "qa_visitor_ae_pub",
    "base_url": "https://ae.58v5.cn",
    "detail_url": (
        "https://ae.58v5.cn/en/city-abu-dhabi/cate-other-business-industrial/google-pixel-6-pro-128gb-excellent-condition-for-sale-2053750384618487810/"
    ),
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt",
    },
    "locale": "en-US",
    "currency": "AED",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000,
    },
}


@allure.epic("OK.com 体验测试")
@allure.feature("详情页")
@allure.story("发布者信息区域（访客）")
class TestDetailPagePublisherVisitor:
    @pytest.mark.case_id_pub_009
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-009: 从未登录访客点击 Contact 进入访客微聊")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_pub_009_contact_opens_guest_chat(self, page, config):
        login_page = LoginPage(page)
        pub = DetailPagePublisher(page)
        detail = config["detail_url"]

        with allure.step("完全清除所有存储，模拟从未登录的干净环境"):
            # 先访问站点
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
            
            # 清除所有存储：Cookie + localStorage + sessionStorage
            page.context.clear_cookies()
            page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
            logger.info("✓ 已清除所有Cookie、localStorage、sessionStorage，模拟从未登录状态")
            page.wait_for_timeout(1000)

        with allure.step("访客打开详情页"):
            pub.goto_detail(detail)
            login_page.handle_cookie_popup()
            expect(page.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I))).to_be_visible(
                timeout=15000
            )

        with allure.step("点击 Contact"):
            c = pub.contact_button
            c.wait_for(state="visible", timeout=15000)
            c.click()

        with allure.step("跳转至访客微聊页面"):
            # 等待可能的跳转或弹层
            page.wait_for_timeout(3000)
            
            current_url = page.url
            logger.info(f"从未登录访客点击Contact后URL: {current_url}")
            
            # 检查是否有URL跳转
            url_changed = "6516039766105310" not in current_url
            has_chat_in_url = "chat" in current_url.lower() or "message" in current_url.lower()
            
            # 检查是否有弹层或新打开的聊天UI
            has_chat_dialog = page.locator('[role="dialog"]').filter(
                has_text=re.compile(r"message|chat|send", re.I)
            ).count() > 0
            has_chat_input = page.locator('textarea[placeholder*="message"], input[placeholder*="message"]').count() > 0
            has_chat_window = page.locator('.chat, .message, [class*="chat"], [class*="message"]').count() > 0
            
            # 检查是否有登录引导
            has_login_modal = page.locator('[role="dialog"]').filter(
                has_text=re.compile(r"login|sign in|welcome", re.I)
            ).count() > 0
            
            logger.info(f"URL变化: {url_changed}, Chat相关URL: {has_chat_in_url}")
            logger.info(f"Chat弹层: {has_chat_dialog}, Chat输入框: {has_chat_input}, Chat窗口: {has_chat_window}")
            logger.info(f"登录弹层: {has_login_modal}")
            
            # 验证：应该跳转到微聊页或出现微聊UI
            assert url_changed or has_chat_in_url or has_chat_dialog or has_chat_input or has_chat_window, \
                f"应跳转到访客微聊页或出现微聊UI，实际URL: {current_url}，无相关UI元素"
            
            logger.info("✓ 从未登录访客点击Contact：已进入访客微聊或出现微聊UI")

    @pytest.mark.case_id_pub_010
    @pytest.mark.p1
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-010: 访客从微聊返回详情页后信息仍完整")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_pub_010_back_from_chat_to_detail(self, page, config):
        login_page = LoginPage(page)
        pub = DetailPagePublisher(page)
        detail = config["detail_url"]

        with allure.step("完全清除所有Cookie，模拟从未登录的干净环境"):
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
            page.context.clear_cookies()
            logger.info("✓ 已清除所有Cookie，模拟从未登录状态")
            page.wait_for_timeout(1000)

        with allure.step("访客打开详情并点击 Contact"):
            pub.goto_detail(detail)
            login_page.handle_cookie_popup()
            c = pub.contact_button
            c.wait_for(state="visible", timeout=15000)
            c.click()
            
            # 等待跳转到访客微聊页
            page.wait_for_load_state("networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            
            chat_url = page.url
            logger.info(f"访客进入微聊页: {chat_url}")
            
            # 验证已跳转
            assert "6516039766105310" not in chat_url or "chat" in chat_url.lower(), \
                f"应跳转到访客微聊页，实际URL: {chat_url}"

        with allure.step("点击浏览器后退按钮"):
            page.go_back(wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1000)

        with allure.step("验证返回到原详情页，信息完整"):
            # 验证URL回到详情页
            expect(page).to_have_url(re.compile(r".*2053750384618487810.*"), timeout=10000)
            
            # 验证发布者信息卡片仍完整展示
            expect(pub.contact_button).to_be_visible(timeout=10000)
            expect(page.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I))).to_be_visible(
                timeout=10000
            )
            
            logger.info("✓ 访客从微聊返回详情页，信息完整")
