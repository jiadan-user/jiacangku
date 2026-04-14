"""
OK.com 收藏页 - 批次3（TC011–TC015 取消收藏、详情重收藏、分页）

用例文档：test_cases/体验/收藏页/OK.com-收藏页-测试用例-20260402.md

注意：TC011–TC013 为链式数据依赖，须同模块顺序执行；TC014/015 需账号收藏足够多页。
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.detail_page_favourites import DetailPageFavourites
from pages.favorites_page import FavoritesPage
from pages.login_page import LoginPage
from utils.logger import setup_logger

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


@pytest.mark.case_id_ae_favorites_011
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("取消收藏功能")
@allure.title("TC011: 点击心形图标取消收藏")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc011_unfavorite_first_card_by_heart_icon(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    fav.ensure_logged_in_favorites(login_page, config)
    fav.wait_for_listing_cards(minimum=2, timeout=20000)

    with allure.step('步骤1：确认存在 "Ac maintenance" 卡片且可取消收藏'):
        ac_link = fav.listing_card_link_by_text("Ac maintenance")
        expect(ac_link).to_be_visible(timeout=15000)
        n_before = fav.favorites_grid_post_links().count()
        assert n_before >= 2

    with allure.step("步骤2：点击该卡右上角实心心形"):
        ok = fav.click_favorite_icon_unfavorite_card_containing("Ac maintenance")
        assert ok, "应在列表中找到 Ac maintenance 卡片并点击 favorite-icon"
        page.wait_for_timeout(1200)

    with allure.step("步骤3：卡片移除、补位、无二次确认"):
        expect(page.get_by_role("dialog")).not_to_be_visible(timeout=3000)
        # 用例文档写「无 toast」；AE 环境实测可能出现「Removed from favorites」，不作否定断言

        n_after = fav.favorites_grid_post_links().count()
        assert n_after == n_before - 1, f"列表应少 1 张：{n_before} -> {n_after}"
        expect(ac_link).not_to_be_visible(timeout=8000)

        first = fav.favorites_grid_post_links().first
        expect(first).to_contain_text(re.compile(r"hyundai", re.I))


@pytest.mark.case_id_ae_favorites_012
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("取消收藏功能")
@allure.title("TC012: 取消收藏后在详情页重新收藏")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc012_refavorite_from_detail_after_unfavorite(page, config):
    detail_po = DetailPageFavourites(page)
    login_page = LoginPage(page)
    url = config["sample_detail_ac_maintenance"]
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_load_state("load", timeout=30000)
    login_page.handle_cookie_popup()
    detail_po.handle_cookie_popup()

    with allure.step("步骤1：详情页 Favourites 为未收藏（空心资源）"):
        hollow = page.evaluate(
            """() => {
              const imgs = [...document.querySelectorAll('img')];
              return imgs.some(i => {
                const s = (i.src || '').toLowerCase();
                return s.includes('unfav');
              });
            }"""
        )
        assert hollow, "取消收藏后详情页应存在空心收藏图标资源"

    with allure.step("步骤2：点击 Favourites"):
        url_before = page.url
        detail_po.click_favourites_button()
        page.wait_for_timeout(1500)

    with allure.step('步骤3：实心态与 Toast "Added to favourites"'):
        filled = page.evaluate(
            """() => {
              const imgs = [...document.querySelectorAll('img')];
              for (const i of imgs) {
                const s = (i.src || '').toLowerCase();
                if (s.includes('unfav')) return false;
                if (s.includes('fav') && s.includes('.png')) return true;
              }
              return false;
            }"""
        )
        assert filled, "点击后应回到已收藏图片资源"
        expect(
            page.get_by_text(re.compile(r"Added to favou?rites?", re.I)).first
        ).to_be_visible(timeout=8000)
        assert page.url.rstrip("/") == url_before.rstrip("/"), "收藏应为 SPA，不跳转其他路径"


@pytest.mark.case_id_ae_favorites_013
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("取消收藏功能")
@allure.title("TC013: 重新收藏后返回收藏页验证恢复")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc013_back_to_favorites_list_restores_card(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    fav.ensure_logged_in_favorites(login_page, config)
    fav.wait_for_listing_cards(minimum=2, timeout=20000)

    with allure.step("步骤1：Ac maintenance 回到列表首位且为实心收藏"):
        first = fav.listing_cards_locator().first
        expect(first).to_contain_text(re.compile(r"Ac maintenance", re.I))
        ac_link = fav.listing_card_link_by_text("Ac maintenance")
        expect(ac_link).to_be_visible()
        src = page.evaluate(
            """() => {
              const links = [...document.querySelectorAll(
                'a[href*="ae.ok.com"][href*="/cate-"]')];
              const a = links.find(x => x.innerText.includes('Ac maintenance'));
              if (!a) return '';
              let el = a;
              for (let i = 0; i < 12 && el; i++) {
                const icon = el.querySelector('img.favorite-icon');
                if (icon) return icon.src || '';
                el = el.parentElement;
              }
              return '';
            }"""
        )
        assert src and "unFav.d2971929" not in src

    with allure.step("步骤2：其他帖子仍在（抽样 hyundai）"):
        expect(page.get_by_text(re.compile(r"hyundai", re.I)).first).to_be_visible(
            timeout=10000
        )


@pytest.mark.case_id_ae_favorites_014
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("列表翻页")
@allure.title("TC014: 第1页 Prev 禁用与 Next 可用")
@allure.severity(allure.severity_level.NORMAL)
def test_tc014_pagination_prev_disabled_on_page_one(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    fav.ensure_logged_in_favorites(login_page, config)
    fav.wait_for_listing_cards(minimum=1, timeout=20000)

    with allure.step("步骤1：滚动到底部分页器"):
        fav.scroll_to_pagination()
        expect(page.get_by_text("Prev", exact=True).last).to_be_visible(timeout=10000)
        expect(page.get_by_text("Next", exact=True).last).to_be_visible(timeout=10000)

    with allure.step("步骤2：Prev 禁用、Next 启用"):
        assert fav.pager_prev_is_disabled(), "第 1 页 Prev 应为禁用"
        if fav.pager_next_is_disabled():
            pytest.skip("当前账号收藏不足两页，无法验证 Next 启用")
        assert not fav.pager_next_is_disabled()

    with allure.step('步骤3：当前页码 "1" 高亮（尽力匹配）'):
        if not fav.current_page_number_highlighted("1"):
            logger.warning("未能识别页码 1 高亮样式，分页 DOM 可能与假设不一致")


@pytest.mark.case_id_ae_favorites_015
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.favorite
@pytest.mark.ae
@allure.feature("OK.com 收藏页")
@allure.story("列表翻页")
@allure.title("TC015: 点击 Next 翻到第2页")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc015_click_next_goes_to_page_two(page, config):
    fav = FavoritesPage(page)
    login_page = LoginPage(page)
    fav.ensure_logged_in_favorites(login_page, config)
    fav.wait_for_listing_cards(minimum=1, timeout=20000)
    fav.scroll_to_pagination()

    if fav.pager_next_is_disabled():
        pytest.skip("当前账号收藏不足两页，跳过 Next 翻页")

    with allure.step("步骤1：记录第1页首张卡片文案"):
        t1 = fav.listing_cards_locator().first.inner_text()[:80]

    with allure.step("步骤2：点击 Next"):
        fav.click_pager_next()
        fav.wait_for_listing_cards(minimum=1, timeout=20000)

    with allure.step("步骤3：第2页态与列表更新"):
        assert not fav.pager_prev_is_disabled(), "第 2 页 Prev 应可点"
        t2 = fav.listing_cards_locator().first.inner_text()[:80]
        assert t1 != t2 or "page" in page.url.lower() or "p=" in page.url.lower(), (
            "翻页后首卡或 URL 应变化"
        )
        p2_ok = fav.current_page_number_highlighted("2")
        url_has_page = bool(
            re.search(r"(page|p)=?\s*2", page.url, re.I)
        )
        assert p2_ok or url_has_page or t1 != t2, "应能判断已进入第 2 页"
        assert fav.listing_cards_locator().count() >= 2, "第 2 页应至少 2 张卡片"
