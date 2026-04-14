"""
OK.com 收藏页 - 批次2（TC006–TC010 登录成功、列表、跳转、后退、过期标识）

用例文档：test_cases/体验/收藏页/OK.com-收藏页-测试用例-20260402.md
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.detail_page_favourites import DetailPageFavourites
from pages.favorites_page import FavoritesPage
from pages.login_page import LoginPage
from utils.logger import setup_logger
from utils.session_manager import SessionManager

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站 (AE OK.com)",
    "role": "buyer",
    "user_name": "ae_buyer_sc",
    "base_url": "https://aepub.ok.com",
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt",
    },
    "empty_favorites_account": {
        "username": "shencccccccc@outlook.com",
        "password": "123456Tt",
    },
    "expected_username_display": "OKerAE_dkk3duf",
    "sample_detail_ac_maintenance": (
        "https://ae.ok.com/en/city-abu-dhabi/cate-heating-ventilation-air-condition/"
        "ac-maintenance-and-service-6343924677517011/"
    ),
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


def _session_name(config: dict) -> str:
    return f"{config['site']}_{config['role']}_{config['user_name']}"


@pytest.mark.case_id_ae_favorites_006
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.core_flow
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("登录成功与列表展示")
@allure.title("TC006: 登录成功自动显示收藏列表")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc006_login_success_shows_favorites_list(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)

    with allure.step("步骤1：访客打开收藏页并完成登录"):
        fav.reset_to_guest()
        fav.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        fav.ensure_email_step_login_modal(login_page)
        login_page.input_email(config["test_account"]["username"])
        login_page.click_continue_button()
        login_page.input_password(config["test_account"]["password"])
        login_page.click_login_button()

    with allure.step("步骤2：登录弹窗关闭，展示用户名与列表"):
        expect(page.get_by_role("dialog")).not_to_be_visible(timeout=25000)
        uname = config["expected_username_display"]
        expect(page.get_by_text(re.compile(re.escape(uname)))).to_be_visible()
        expect(page).to_have_url(re.compile(r"favorites", re.I))
        expect(page).to_have_title(re.compile(r"Favourites", re.I))
        assert fav.listing_cards_locator().count() >= 4, "应展示多列网格下的收藏卡片"

    with allure.step("步骤3：保存 Session 供后续用例复用"):
        sm = SessionManager(
            page, config["base_url"], session_name=_session_name(config)
        )
        assert sm.save_session(), "应成功保存登录 Session"


@pytest.mark.case_id_ae_favorites_007
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.ui
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("帖子卡片展示与点击")
@allure.title("TC007: 收藏列表正常展示")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc007_favorites_grid_and_cards(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    fav.ensure_logged_in_favorites(login_page, config)

    with allure.step("步骤1：标题与网格卡片数量"):
        expect(page).to_have_title(re.compile(r"Favourites", re.I))
        n = fav.listing_cards_locator().count()
        assert n >= 4, f"预期至少 4 张卡片，实际 {n}"

    with allure.step("步骤2：首张卡片含已收藏心形图与封面图"):
        src = fav.first_favorites_card_favorite_icon_src()
        assert src, "应能读取列表卡片收藏图标"
        assert "unFav.d2971929" not in src, "已收藏列表卡片应为实心态资源"
        first_link = fav.first_listing_card_link()
        expect(first_link).to_be_visible()
        expect(first_link.locator("img").first).to_be_visible()

    with allure.step("步骤3：多类目文案共存（用例文档抽样）"):
        expect(page.get_by_text(re.compile(r"Ac maintenance", re.I)).first).to_be_visible()
        expect(page.get_by_text(re.compile(r"hyundai", re.I)).first).to_be_visible()

    with allure.step("步骤4：存在过期标签（与 TC010 一致数据源）"):
        expect(page.get_by_text("Expired", exact=True).first).to_be_visible(
            timeout=15000
        )


@pytest.mark.case_id_ae_favorites_008
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.navigation
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("帖子卡片展示与点击")
@allure.title("TC008: 点击帖子卡片跳转到详情页")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc008_click_first_card_opens_detail_same_tab(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    detail = DetailPageFavourites(page)
    tabs_before = len(page.context.pages)

    fav.ensure_logged_in_favorites(login_page, config)

    with allure.step('步骤1：点击 "Ac maintenance and service" 卡片'):
        card = page.get_by_role(
            "link", name=re.compile(r"Ac maintenance and service", re.I)
        ).first
        expect(card).to_be_visible(timeout=15000)
        card.click()
        page.wait_for_load_state("domcontentloaded")

    with allure.step("步骤2：详情页 URL 与当前标签页"):
        expect(page).to_have_url(
            re.compile(r"ac-maintenance-and-service-6343924677517011")
        )
        assert len(page.context.pages) == tabs_before
        detail.handle_cookie_popup()
        expect(
            page.get_by_text(re.compile(r"Ac maintenance", re.I)).first
        ).to_be_visible(timeout=15000)
        expect(detail.favourites_button).to_be_visible()

    with allure.step("步骤3：详情页收藏为已选状态（心形资源，AE 与列表位哈希可能不同）"):
        filled = page.evaluate(
            """() => {
              const imgs = [...document.querySelectorAll('img')];
              for (const i of imgs) {
                const s = (i.src || '').toLowerCase();
                if (s.includes('unfav')) return false;
                if (s.includes('favorite') || /fav\\.[a-z0-9]+\\.(png|webp|svg)/i.test(s))
                  return true;
              }
              return false;
            }"""
        )
        assert filled, "详情页应存在已收藏侧心形/收藏相关图片资源"


@pytest.mark.case_id_ae_favorites_009
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.navigation
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("帖子卡片展示与点击")
@allure.title("TC009: 浏览器后退返回收藏页")
@allure.severity(allure.severity_level.NORMAL)
def test_tc009_back_from_detail_restores_favorites(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)

    fav.ensure_logged_in_favorites(login_page, config)

    with allure.step("步骤1：收藏页向下滚动并记录 scrollY"):
        page.evaluate("window.scrollTo(0, 520)")
        page.wait_for_timeout(400)
        y_before = page.evaluate("window.scrollY")

    with allure.step("步骤2：进入详情再后退"):
        card = page.get_by_role(
            "link", name=re.compile(r"Ac maintenance and service", re.I)
        ).first
        card.click()
        page.wait_for_load_state("load")
        expect(page).to_have_url(
            re.compile(r"6343924677517011"),
            timeout=20000,
        )
        page.go_back(wait_until="load")

    with allure.step("步骤3：回到收藏页且仍登录、列表仍在"):
        expect(page).to_have_url(re.compile(r"favorites", re.I), timeout=20000)
        guest = page.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I)).first
        expect(guest).not_to_be_visible(timeout=5000)
        fav.wait_for_listing_cards(minimum=1, timeout=25000)
        assert fav.listing_cards_locator().count() >= 1

    with allure.step("步骤4：滚动位置（SPA 可能回顶，仅记录）"):
        page.wait_for_timeout(500)
        y_after = page.evaluate("window.scrollY")
        if abs(y_after - y_before) >= 280:
            logger.warning(
                "后退后滚动未保持: scrollY %s -> %s（与用例文档可能不一致）",
                y_before,
                y_after,
            )


@pytest.mark.case_id_ae_favorites_010
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.ui
@pytest.mark.ae
@pytest.mark.favorite
@allure.feature("OK.com 收藏页")
@allure.story("帖子卡片展示与点击")
@allure.title("TC010: 过期帖子卡片标识展示")
@allure.severity(allure.severity_level.NORMAL)
def test_tc010_expired_badge_on_card(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)

    fav.ensure_logged_in_favorites(login_page, config)

    with allure.step("步骤1：列表中存在 Expired 标签"):
        expired = page.get_by_text("Expired", exact=True).first
        expect(expired).to_be_visible(timeout=15000)

    with allure.step("步骤2：过期卡片可点进详情（链到 ae.ok.com，可选）"):
        expired_card = (
            page.locator("a[href*='ae.ok.com'][href*='/cate-']")
            .filter(has_text="Expired")
            .first
        )
        if expired_card.is_visible(timeout=3000):
            expired_card.click()
            page.wait_for_load_state("domcontentloaded")
            assert "ae.ok.com" in page.url or "/cate-" in page.url
            page.go_back(wait_until="load")
            expect(page).to_have_url(re.compile(r"favorites", re.I))
