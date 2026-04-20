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
        "https://ae.58v5.cn/en/city-abu-dhabi/cate-others266/ddfasdf-6516039766105310/"
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
    @allure.title("TC-PUB-009: 未登录点击 Contact 弹出登录层")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_pub_009_contact_opens_login_modal(self, page, config):
        login_page = LoginPage(page)
        pub = DetailPagePublisher(page)
        detail = config["detail_url"]

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

        with allure.step("等待登录弹层出现（避免匹配页面上隐藏的空白 dialog 节点）"):
            # 等待弹窗出现，58v5.cn环境可能需要更长时间
            page.wait_for_timeout(3000)  # 增加等待时间
            
            # 使用宽松的定位器，增加超时时间
            dlg = page.locator('[role="dialog"]').filter(
                has_text=re.compile(r"Welcome", re.I)
            ).first
            
            # 尝试等待dialog出现，如果失败则检查是否有其他登录元素
            try:
                dlg.wait_for(state="visible", timeout=15000)
            except Exception as e:
                # 如果dialog没找到，尝试直接查找Email输入框
                logger.warning(f"未找到Welcome dialog: {e}")
                email_input = page.get_by_role("textbox", name=re.compile("Email", re.I))
                email_input.wait_for(state="visible", timeout=5000)
                # 重新定位dialog
                dlg = page.locator('[role="dialog"]').first
            
            # 验证登录弹窗的关键元素
            expect(page.get_by_role("textbox", name=re.compile("Email", re.I))).to_be_visible(timeout=5000)

        with allure.step("仍停留在详情 URL"):
            expect(page).to_have_url(re.compile(r".*6516039766105310.*"))

        with allure.step("登录弹层内容"):
            expect(dlg).to_be_visible(timeout=5000)
            # 验证登录弹窗的关键元素
            expect(page.get_by_role("textbox", name=re.compile("Email", re.I))).to_be_visible()
            expect(page.get_by_role("button", name=re.compile("Continue", re.I))).to_be_visible()
            # 验证Welcome文本
            expect(page.get_by_text(re.compile(r"Welcome.*OK", re.I))).to_be_visible()

    @pytest.mark.case_id_pub_010
    @pytest.mark.p1
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-010: 关闭登录弹层后仍在详情页")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_pub_010_close_login_modal_stays_on_detail(self, page, config):
        login_page = LoginPage(page)
        pub = DetailPagePublisher(page)
        detail = config["detail_url"]

        with allure.step("访客打开详情并点开 Contact"):
            pub.goto_detail(detail)
            login_page.handle_cookie_popup()
            c = pub.contact_button
            c.wait_for(state="visible", timeout=15000)
            c.click()
            # 等待登录弹窗出现（使用宽松的定位器）
            page.wait_for_timeout(2000)
            page.locator('[role="dialog"]').filter(
                has_text=re.compile(r"Welcome", re.I)
            ).first.wait_for(state="visible", timeout=10000)

        with allure.step("点击弹层关闭"):
            pub.close_login_dialog_if_present()

        with allure.step("弹层消失且仍在详情"):
            # 验证登录弹窗已隐藏
            page.wait_for_timeout(1000)
            expect(
                page.locator('[role="dialog"]').filter(
                    has_text=re.compile(r"Welcome", re.I)
                ).first
            ).to_be_hidden(timeout=10000)
            expect(page).to_have_url(re.compile(r".*6516039766105310.*"))
            expect(pub.contact_button).to_be_visible(timeout=10000)
