"""
OK.com 详情页 Location 区域 — 访客场景（TC-LOCATION-A-001 ~ D-001）

playwright-test-generator 生成 | 用例文档：web-qa-brain/OK.com-详情页Location区域-测试用例-20260410.md
录制证明：playwright-test-generator/batch-location-area-recording.md
"""

import re

import allure
import pytest
from playwright.sync_api import expect

from pages.detail_page_location import DetailPageLocation
from pages.login_page import LoginPage

_CONFIG = {
    "site": "ae",
    "site_name": "AE 预览站 (58v5)",
    "role": "visitor",
    "user_name": "visitor_ae_location",
    "base_url": "https://ae.58v5.cn",
    "detail_url": (
        "https://ae.58v5.cn/en/city-dubai/cate-activities-groups/gong-meditation-6468820435993310/"
    ),
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt",
    },
    "locale": "en-AE",
    "currency": "AED",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1440, "height": 900},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 60000,
    },
}


def _open_detail(loc: DetailPageLocation, login_page: LoginPage, config):
    loc.goto_detail(config["detail_url"])
    login_page.handle_cookie_popup()
    loc.location_card.wait_for(state="visible", timeout=20000)


@allure.epic("OK.com 体验测试")
@allure.feature("详情页")
@allure.story("Location 区域（访客）")
class TestDetailPageLocationVisitor:
    @pytest.mark.case_id_location_a001
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-A-001：Location 模块整体可见且结构完整")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_location_a001_card_structure(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)

        with allure.step("Location 卡片容器"):
            card = loc.location_card
            expect(card).to_be_visible()
            card.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            box = card.bounding_box()
            assert box is not None, "Location 卡片边界框获取失败,元素可能未完全渲染"
            assert 580 <= box["width"] <= 760, f"卡片宽度异常: {box['width']}"
            assert 180 <= box["height"] <= 320, f"卡片高度异常: {box['height']}"

        with allure.step("自上而下：标题 / 地址 / Show map"):
            expect(loc.location_section_title).to_be_visible()
            expect(loc.location_address).to_be_visible()
            expect(loc.show_map_button).to_be_visible()

    @pytest.mark.case_id_location_a002
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-A-002：Location 标题文案")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_location_a002_title_text(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)
        expect(loc.location_section_title).to_have_text(re.compile(r"^\s*Location\s*$", re.I))

    @pytest.mark.case_id_location_a003
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-A-003：地址文案展示")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_location_a003_address_display(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)
        txt = loc.location_address.inner_text().strip()
        assert len(txt) >= 2, "Location 地址为空或过短"
        box = loc.location_address.bounding_box()
        assert box is not None and box["height"] >= 12

    @pytest.mark.case_id_location_a004
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-A-004：Show map 预览区与按钮")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_location_a004_show_map_area(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)
        preview = loc.show_map_preview
        expect(preview).to_be_visible()
        pb = preview.bounding_box()
        assert pb is not None
        assert pb["height"] >= 100, f"预览区高度异常: {pb['height']}"
        assert pb["width"] >= 400, f"预览区宽度异常: {pb['width']}"
        btn = loc.show_map_button
        expect(btn).to_contain_text(re.compile(r"Show\s*map", re.I))
        bb = btn.bounding_box()
        assert bb is not None and bb["width"] >= 80 and bb["height"] >= 32

    @pytest.mark.case_id_location_b001
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-B-001：点击 Show map 打开全屏地图模态")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_location_b001_b002_open_map_modal(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)
        loc.show_map_button.scroll_into_view_if_needed()
        loc.show_map_button.click()
        modal = loc.map_modal
        modal.wait_for(state="visible", timeout=15000)
        expect(modal).to_be_visible()
        expect(page.locator(".modal-fullscreen")).to_be_visible()
        expect(page.locator(".modal-dialog.modal-fullscreen")).to_be_visible()
        gm = page.locator(".modal.show #map .gm-style").first
        gm.wait_for(state="visible", timeout=20000)
        expect(gm).to_be_visible()
        close_btn = loc.map_modal_close
        expect(close_btn).to_be_visible()
        expect(close_btn).to_have_attribute("alt", "close")
        close_btn.click()
        page.wait_for_timeout(800)
        expect(modal).not_to_be_visible(timeout=10000)

    @pytest.mark.case_id_location_b003
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-B-003：点击关闭图标关闭地图模态")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_location_b003_close_map_modal(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)
        loc.show_map_button.scroll_into_view_if_needed()
        loc.show_map_button.click()
        loc.map_modal.wait_for(state="visible", timeout=15000)
        loc.map_modal_close.click()
        page.wait_for_timeout(1000)
        expect(loc.map_modal).not_to_be_visible(timeout=10000)

    @pytest.mark.case_id_location_b004
    @pytest.mark.p1
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-B-004：关闭后可再次打开地图")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_location_b004_reopen_map(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)
        btn = loc.show_map_button
        btn.scroll_into_view_if_needed()
        btn.click()
        loc.map_modal.wait_for(state="visible", timeout=15000)
        loc.map_modal_close.click()
        page.wait_for_timeout(800)
        expect(loc.map_modal).not_to_be_visible(timeout=10000)
        btn.click()
        loc.map_modal.wait_for(state="visible", timeout=15000)
        expect(page.locator(".modal.show #map .gm-style").first).to_be_visible(timeout=20000)
        loc.map_modal_close.click()
        page.wait_for_timeout(800)

    @pytest.mark.case_id_location_c001
    @pytest.mark.p1
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-C-001：主信息区地址与 Location 地址一致")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_location_c001_address_consistency(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)
        main_txt = loc.main_info_address.inner_text().strip()
        loc_txt = loc.location_address.inner_text().strip()
        assert main_txt == loc_txt, f"主信息区「{main_txt}」与 Location「{loc_txt}」不一致"

    @pytest.mark.case_id_location_d001
    @pytest.mark.p2
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-LOCATION-D-001：地图模态打开后按 Escape 的行为")
    @allure.severity(allure.severity_level.MINOR)
    def test_tc_location_d001_escape_keeps_modal_open(self, page, config):
        login_page = LoginPage(page)
        loc = DetailPageLocation(page)
        _open_detail(loc, login_page, config)
        loc.show_map_button.scroll_into_view_if_needed()
        loc.show_map_button.click()
        loc.map_modal.wait_for(state="visible", timeout=15000)
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        expect(loc.map_modal).to_be_visible(timeout=3000)
        loc.map_modal_close.click()
        page.wait_for_timeout(800)
        expect(loc.map_modal).not_to_be_visible(timeout=10000)
