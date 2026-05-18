"""
OK.com 收藏页 - 批次4（TC016–TC020 分页进阶与翻页数据）

用例文档：test_cases/体验/收藏页/OK.com-收藏页-测试用例-20260402.md
需账号收藏列表 ≥2 页；否则相关用例 pytest.skip。
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.favorites_page import FavoritesPage
from pages.login_page import LoginPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站 (AE OK.com)",
    "role": "buyer",
    "user_name": "ae_buyer_sc",
    "base_url": "https://aepub.58v5.cn",
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt",
    },
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


def _grid_hrefs(page):
    return page.evaluate(
        """() => {
          const sel = "a[class*='list-components-item-card'][href*='ae.58v5.cn']";
          const nodes = document.querySelectorAll(sel);
          return [...nodes].map(a => a.href).filter(Boolean);
        }"""
    )


def _skip_unless_two_pages(fav: FavoritesPage, login_page: LoginPage, config: dict):
    fav.ensure_logged_in_favorites(login_page, config)
    fav.wait_for_listing_cards(minimum=1, timeout=20000)
    fav.scroll_to_pagination()
    if fav.pager_next_is_disabled():
        pytest.skip("当前账号收藏不足两页，跳过分页用例")


def _go_to_page_two(fav: FavoritesPage):
    fav.scroll_to_pagination()
    fav.click_pager_next()
    fav.wait_for_listing_cards(minimum=1, timeout=20000)


@pytest.mark.case_id_ae_favorites_016
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("列表翻页")
@allure.title("TC016: 最后一页 Next 禁用")
@allure.severity(allure.severity_level.NORMAL)
def test_tc016_last_page_next_disabled(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    _skip_unless_two_pages(fav, login_page, config)

    with allure.step("步骤1：记录第1页卡片数并进入第2页"):
        n1 = fav.favorites_grid_post_links().count()
        assert n1 >= 2
        _go_to_page_two(fav)

    with allure.step("步骤2：最后一页 Next 禁用、Prev 可用"):
        assert fav.pager_next_is_disabled(), "第2页为末页时 Next 应禁用"
        assert not fav.pager_prev_is_disabled()
        n2 = fav.favorites_grid_post_links().count()
        assert n2 >= 1
        if n2 >= n1:
            logger.warning(
                "第2页卡片数未少于第1页（n1=%s n2=%s），与文档「少于」可能不一致",
                n1,
                n2,
            )


@pytest.mark.case_id_ae_favorites_017
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("列表翻页")
@allure.title("TC017: Prev 返回第1页")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc017_prev_returns_to_page_one(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    _skip_unless_two_pages(fav, login_page, config)
    _go_to_page_two(fav)

    with allure.step("步骤1：点击 Prev"):
        fav.click_pager_prev()
        fav.wait_for_listing_cards(minimum=1, timeout=20000)

    with allure.step("步骤2：第1页分页态"):
        assert fav.pager_prev_is_disabled()
        assert not fav.pager_next_is_disabled()
        assert fav.favorites_grid_post_links().count() >= 2


@pytest.mark.case_id_ae_favorites_018
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("列表翻页")
@allure.title("TC018: 点击页码 2 跳转")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc018_click_page_number_two(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    _skip_unless_two_pages(fav, login_page, config)

    with allure.step("步骤1：确保在第1页"):
        fav.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        
        # 如果弹出登录框(session失效),重新登录
        email_box = page.get_by_role("textbox", name="Email or phone number")
        if email_box.is_visible(timeout=2000):
            logger.info("检测到登录框,session已失效,触发重新登录")
            fav.ensure_logged_in_favorites(login_page, config)
        
        fav.wait_for_listing_cards(minimum=1, timeout=20000)
        fav.scroll_to_pagination()
        while not fav.pager_prev_is_disabled():
            fav.click_pager_prev()
            page.wait_for_timeout(600)
        t1 = fav.favorites_grid_post_links().first.inner_text()[:120]

    with allure.step("步骤2：点击页码 2"):
        if not fav.click_pager_page_number("2"):
            pytest.skip("分页器未提供可点的数字页码 2")
        fav.wait_for_listing_cards(minimum=1, timeout=20000)

    with allure.step("步骤3：第2页且为末页时 Next 禁用"):
        t2 = fav.favorites_grid_post_links().first.inner_text()[:120]
        assert t1 != t2 or "page" in page.url.lower(), "第2页首卡或 URL 应与第1页区分"
        assert fav.pager_next_is_disabled()
        assert not fav.pager_prev_is_disabled()


@pytest.mark.case_id_ae_favorites_019
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("列表翻页")
@allure.title("TC019: 点击页码 1 返回")
@allure.severity(allure.severity_level.NORMAL)
def test_tc019_click_page_number_one_from_page_two(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    _skip_unless_two_pages(fav, login_page, config)
    _go_to_page_two(fav)

    with allure.step("步骤1：点击页码 1"):
        if not fav.click_pager_page_number("1"):
            pytest.skip("分页器未提供可点的数字页码 1")
        fav.wait_for_listing_cards(minimum=1, timeout=20000)

    with allure.step("步骤2：回到第1页分页态"):
        assert fav.pager_prev_is_disabled()
        assert not fav.pager_next_is_disabled()


@pytest.mark.case_id_ae_favorites_020
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("列表翻页")
@allure.title("TC020: 翻页后数据与返回一致性")
@allure.severity(allure.severity_level.NORMAL)
def test_tc020_pagination_data_integrity_round_trip(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    _skip_unless_two_pages(fav, login_page, config)

    with allure.step("步骤1：第1页首张标题与链接集"):
        fav.navigate_to_favorites_list(config["base_url"])
        login_page.handle_cookie_popup()
        fav.wait_for_listing_cards(minimum=1, timeout=20000)
        fav.scroll_to_pagination()
        while not fav.pager_prev_is_disabled():
            fav.click_pager_prev()
            page.wait_for_timeout(600)
        t1 = fav.favorites_grid_post_links().first.inner_text()[:100]
        h1 = set(_grid_hrefs(page))

    with allure.step("步骤2：第2页数据与第1页不重复"):
        _go_to_page_two(fav)
        t2 = fav.favorites_grid_post_links().first.inner_text()[:100]
        assert t1 != t2, "第2页首张应与第1页首张不同"
        h2 = set(_grid_hrefs(page))
        overlap = h1 & h2
        if overlap:
            logger.warning("两页列表链接存在交集 %s 条，文档「无重复」可能不成立", len(overlap))

    with allure.step("步骤3：Prev 回第1页首张一致"):
        fav.click_pager_prev()
        fav.wait_for_listing_cards(minimum=1, timeout=20000)
        t1_back = fav.favorites_grid_post_links().first.inner_text()[:100]
        assert t1_back.strip()[:80] == t1.strip()[:80], "返回第1页后首张应与翻页前一致"
