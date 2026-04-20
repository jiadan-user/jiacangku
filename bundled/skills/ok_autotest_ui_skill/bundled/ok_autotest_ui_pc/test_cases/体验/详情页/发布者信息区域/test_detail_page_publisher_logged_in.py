"""
OK.com 详情页发布者信息区域 — 已登录场景（TC-PUB-001 ~ TC-PUB-008）

playwright-test-generator 生成 | 用例文档：OK.com-详情页发布者信息区域-测试用例-20260409.md
录制证明：playwright-test-generator/batch1-publisher-info-recording.md、batch2-publisher-info-recording.md
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.detail_page_publisher import DetailPagePublisher
from pages.login_page import LoginPage
from utils.logger import setup_logger
from utils.session_manager import SessionManager

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站 (AE OK.com)",
    "role": "buyer",
    "user_name": "qa_buyer_ae",
    "base_url": "https://ae.58v5.cn",
    "detail_url": (
        "https://ae.58v5.cn/en/city-abu-dhabi/cate-others266/ddfasdf-6516039766105310/"
    ),
    "publisher_display_name": "OKerSA_mihwjid",
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


def _ensure_logged_in_and_open_detail(page, config) -> DetailPagePublisher:
    """Session 复用登录 + 打开目标详情页（SCRIPT_SPEC SessionManager 规范）"""
    login_page = LoginPage(page)
    pub = DetailPagePublisher(page)
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config["base_url"], session_name)

    with allure.step("加载登录态或执行登录"):
        if not session_manager.load_session():
            login_page.navigate_to_home_page(base_url=config["base_url"])
            login_page.handle_cookie_popup()
            login_page.click_login_register_button()
            login_page.input_email(config["test_account"]["username"])
            login_page.click_continue_button()
            login_page.input_password(config["test_account"]["password"])
            login_page.click_login_button()
            page.locator("text=/OKer/").first.wait_for(state="visible", timeout=20000)
            session_manager.save_session()
            logger.info("✓ 登录成功并已保存 session: %s", session_name)
        else:
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=60000)
            login_page.handle_cookie_popup()
            page.locator("text=/OKer/").or_(page.get_by_text("Log in / Register")).first.wait_for(
                state="visible", timeout=15000
            )
            logger.info("✓ 已加载 session: %s", session_name)

    with allure.step("打开发布者详情页"):
        pub.goto_detail(config["detail_url"])
        expect(pub.contact_button).to_be_visible(timeout=15000)

    return pub


@allure.epic("OK.com 体验测试")
@allure.feature("详情页")
@allure.story("发布者信息区域（已登录）")
class TestDetailPagePublisherLoggedIn:
    @pytest.mark.case_id_pub_001
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-001: 已认证用户信息完整展示")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_pub_001_publisher_card_logged_in(self, page, config):
        pub = _ensure_logged_in_and_open_detail(page, config)
        name = config["publisher_display_name"]

        with allure.step("校验发布者昵称与认证标识"):
            expect(pub.publisher_display_name(name)).to_be_visible()
            expect(page.get_by_text(re.compile(r"Verified\s+User", re.I))).to_be_visible()

        with allure.step("校验 listings / sold 文案"):
            expect(page.locator("text=/96\\s*listings/i").first).to_be_visible()
            expect(page.locator("text=/5[,，]?558[,，]?889\\s*sold/i").first).to_be_visible()

        with allure.step("校验 Contact 按钮（深色主按钮）"):
            btn = pub.contact_button
            expect(btn).to_be_visible()
            # 等待元素稳定后再滚动，避免DOM重绘导致的detached错误
            btn.wait_for(state="visible", timeout=10000)
            page.wait_for_timeout(1000)  # 等待DOM完全稳定
            btn.scroll_into_view_if_needed()
            # 背景色可能在子节点；取按钮及一层子元素的最大 RGB 深度
            bg = btn.evaluate(
                """(element) => {
                  const pick = (el) => window.getComputedStyle(el).backgroundColor;
                  let c = pick(element);
                  const child = element.firstElementChild;
                  if (child) {
                    const c2 = pick(child);
                    if (c2 && c2 !== 'rgba(0, 0, 0, 0)' && c2 !== 'transparent') c = c2;
                  }
                  return c || '';
                }"""
            )
            assert bg and (
                "17" in bg or "rgb(0" in bg or "rgba(0" in bg or "0, 0, 0" in bg or "0,0,0" in bg
            ), f"unexpected Contact backgroundColor: {bg!r}"

    @pytest.mark.case_id_pub_002
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-002: 点击发布者用户名跳转店铺页")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_pub_002_click_publisher_name_navigates(self, page, config):
        pub = _ensure_logged_in_and_open_detail(page, config)
        name = config["publisher_display_name"]

        with allure.step("点击发布者用户名"):
            pub.click_publisher_name(name)

        with allure.step("校验进入 profile / services"):
            page.wait_for_url(re.compile(r"/profile/[^/]+/services"), timeout=20000)
            expect(page).to_have_url(re.compile(r"/profile/.*/services/?"))
            expect(page).to_have_title(re.compile(re.escape(name), re.I))

    @pytest.mark.case_id_pub_003
    @pytest.mark.p1
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-003: 点击发布者头像区域跳转店铺页")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_pub_003_click_publisher_avatar_area_navigates(self, page, config):
        pub = _ensure_logged_in_and_open_detail(page, config)

        with allure.step("点击发布者卡片可点区域（含头像/Verified）"):
            pub.click_publisher_card_including_badge()

        with allure.step("校验进入 profile / services"):
            page.wait_for_url(re.compile(r"/profile/[^/]+/services"), timeout=20000)
            expect(page).to_have_url(re.compile(r"/profile/.*/services/?"))

    @pytest.mark.case_id_pub_004
    @pytest.mark.p2
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-004: listings 数量展示格式")
    @allure.severity(allure.severity_level.MINOR)
    def test_tc_pub_004_listings_format(self, page, config):
        pub = _ensure_logged_in_and_open_detail(page, config)
        with allure.step("校验 listings 展示"):
            expect(page.locator("text=/\\d+\\s*listings/i").first).to_be_visible()

    @pytest.mark.case_id_pub_005
    @pytest.mark.p2
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-005: sold 数量千分位格式")
    @allure.severity(allure.severity_level.MINOR)
    def test_tc_pub_005_sold_thousands_separator(self, page, config):
        pub = _ensure_logged_in_and_open_detail(page, config)
        with allure.step("校验 sold 含千分位逗号"):
            expect(page.locator("text=/\\d{1,3}(,\\d{3})+\\s*sold/i").first).to_be_visible()

    @pytest.mark.case_id_pub_006
    @pytest.mark.p0
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-006: 已登录点击 Contact 进入聊天页")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_pub_006_contact_opens_chat(self, page, config):
        pub = _ensure_logged_in_and_open_detail(page, config)

        with allure.step("点击 Contact"):
            pub.contact_button.click()

        with allure.step("校验 Messages / chat URL"):
            page.wait_for_url(re.compile(r"aepub\.58v5\.cn/.*/chat"), timeout=25000)
            expect(page).to_have_title(re.compile("Messages", re.I))
            expect(page.get_by_text(re.compile(r"For your safety", re.I))).to_be_visible(
                timeout=15000
            )
            expect(page.get_by_role("textbox", name=re.compile("Input message", re.I))).to_be_visible(
                timeout=15000
            )

    @pytest.mark.case_id_pub_007
    @pytest.mark.p2
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-007: Contact 按钮 hover 光标与背景")
    @allure.severity(allure.severity_level.MINOR)
    def test_tc_pub_007_contact_hover_style(self, page, config):
        pub = _ensure_logged_in_and_open_detail(page, config)
        btn = pub.contact_button

        with allure.step("hover Contact"):
            btn.hover()

        with allure.step("校验 pointer 与深色背景"):
            cursor = btn.evaluate("el => getComputedStyle(el).cursor")
            bg = btn.evaluate("el => getComputedStyle(el).backgroundColor")
            assert cursor == "pointer"
            assert "rgb(17, 17, 17)" in bg or "rgb(0, 0, 0)" in bg or "17" in bg

    @pytest.mark.case_id_pub_008
    @pytest.mark.p1
    @pytest.mark.detail_page
    @pytest.mark.ae
    @allure.title("TC-PUB-008: Contact 快速多次点击后仅到达聊天页")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_pub_008_contact_rapid_clicks_single_chat(self, page, config):
        pub = _ensure_logged_in_and_open_detail(page, config)
        btn = pub.contact_button

        with allure.step("同一按钮上连续派发三次 click 事件（对齐录制并行连点语义）"):
            btn.evaluate(
                """
                (el) => {
                  for (let i = 0; i < 3; i++) {
                    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                  }
                }
                """
            )

        with allure.step("最终应落在聊天页"):
            page.wait_for_url(re.compile(r"aepub\.58v5\.cn/.*/chat"), timeout=25000)
            expect(page).to_have_title(re.compile("Messages", re.I))
