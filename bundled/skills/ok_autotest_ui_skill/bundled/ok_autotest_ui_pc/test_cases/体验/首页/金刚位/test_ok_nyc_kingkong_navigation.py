"""
美国站 OK.com - 纽约首页金刚位导航区

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-金刚位导航区-测试用例-20260324.md
MCP 证明：web-qa-brain/ok_kingkong_mcp_proof_20260324.md
生成时间：2026-03-24

测试站点：US OK.com（纽约城市页）
测试角色：访客 / 买家（SessionManager，单浏览器 class fixture）
测试目标：金刚位各入口跳转、标题与 Jobs 访客/买家落地差异
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.ok_city_header_page import OkCityHeaderPage
from pages.ok_kingkong_nav_page import OkKingkongNavPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "us",
    "site_name": "US OK.com",
    "role": "buyer",
    "user_name": "shenchang_buyer_us",
    "base_url": "https://us.ok.com/en/city-new-york1/",
    "test_account": {
        "username": "shenchang@58.com",
        "password": "123456Tt",
    },
    "locale": "en-US",
    "currency": "USD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1440, "height": 900},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000,
    },
}

def _session_name(config):
    return f"{config['site']}_{config['role']}_{config['user_name']}"


def _wait_url_domcontentloaded(page, pattern: str, timeout: int = 35000):
    """等待 URL（优先 domcontentloaded，兼容旧版 Playwright 无 wait_until 参数）"""
    try:
        page.wait_for_url(pattern, timeout=timeout, wait_until="domcontentloaded")
    except TypeError:
        page.wait_for_url(pattern, timeout=timeout)


def _ensure_guest_on_nyc(page, config):
    """访客态：清空 Cookie/Storage 后回纽约首页"""
    kk = OkKingkongNavPage(page)
    login_page = LoginPage(page)
    header_page = OkCityHeaderPage(page)
    header_page.set_viewport_recording_size()
    page.context.clear_cookies()
    try:
        page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} }")
    except Exception:
        pass
    kk.goto_nyc_home(config["base_url"])
    page.wait_for_load_state("domcontentloaded", timeout=45000)
    login_page.handle_cookie_popup()
    header_page.dismiss_ok_cookie_banner()
    page.wait_for_load_state("domcontentloaded", timeout=15000)


def _ensure_buyer_on_nyc(page, config):
    """买家态：load_session 失败则登录并 save_session（含 Cookie 条处理）"""
    kk = OkKingkongNavPage(page)
    login_page = LoginPage(page)
    header_page = OkCityHeaderPage(page)
    session_manager = SessionManager(
        page, config["base_url"], session_name=_session_name(config)
    )

    header_page.set_viewport_recording_size()
    loaded = session_manager.load_session()
    kk.goto_nyc_home(config["base_url"])
    page.wait_for_load_state("domcontentloaded", timeout=45000)
    login_page.handle_cookie_popup()
    header_page.dismiss_ok_cookie_banner()
    page.wait_for_load_state("domcontentloaded", timeout=10000)
    page.wait_for_timeout(1500)

    if loaded and login_page.is_login_button_text_changed(timeout=5000):
        logger.info("✓ Session 有效，已登录")
        return

    logger.info("执行登录流程")
    session_manager.clear_session()
    page.reload(wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1500)
    login_page.handle_cookie_popup()
    header_page.dismiss_ok_cookie_banner()

    max_retries = 2
    for attempt in range(max_retries):
        try:
            login_page.click_login_register_button()
            page.wait_for_timeout(2500)
            if page.get_by_text("Email or phone number").first.is_visible(timeout=8000):
                break
            if attempt < max_retries - 1:
                header_page.dismiss_ok_cookie_banner()
        except Exception as e:
            if attempt >= max_retries - 1:
                raise
            logger.info(f"打开登录弹层重试: {e}")
            header_page.dismiss_ok_cookie_banner()

    login_page.input_email(config["test_account"]["username"])
    login_page.click_continue_button()
    login_page.input_password(config["test_account"]["password"])
    header_page.dismiss_ok_cookie_banner()
    login_page.click_login_button()
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    assert login_page.is_login_button_text_changed(timeout=10000), "登录后应进入买家态"
    page.wait_for_load_state("load", timeout=25000)
    session_manager.save_session()
    logger.info("✓ Session 已保存")


@pytest.fixture(scope="class")
def page(config):
    """
    覆盖 conftest 的 module page：本脚本单类单浏览器（整文件只启动一次 Chromium）。
    """
    from utils.browser_manager import BrowserManager

    browser_manager = BrowserManager()
    _page = browser_manager.start_browser(
        browser_type=config["browser"]["type"],
        headless=config["browser"]["headless"],
        base_url=config["base_url"],
        viewport=config["browser"]["viewport"],
    )
    browser_manager.mark_in_use()
    yield _page
    browser_manager.mark_released()
    browser_manager.close_browser(_page)


@pytest.fixture(scope="class", autouse=True)
def _bind_page_to_class(request, page, config):
    """供 setup_method 在每则用例前回到纽约首页。"""
    request.cls._cls_page = page
    request.cls._cls_config = config
    yield


class TestOkKingkongNavNyc:
    """纽约金刚位 TC001–TC017：同一浏览器内交替访客/买家态。"""

    def setup_method(self):
        """每则测试前回到纽约首页，降低上一则落地页的串扰。"""
        p = getattr(self.__class__, "_cls_page", None)
        cfg = getattr(self.__class__, "_cls_config", None)
        if p is None or cfg is None or p.is_closed():
            return
        p.goto(cfg["base_url"], wait_until="domcontentloaded", timeout=60000)
        p.wait_for_load_state("domcontentloaded", timeout=20000)

    @pytest.mark.case_id_kingkong_nyc_tc001
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客展示")
    @allure.title("访客在纽约首页应展示完整金刚位入口")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证未登录态下金刚位八个入口可见且首页标题正确")
    def test_tc001_guest_kingkong_entries_visible(self, page, config):
        # ========== Arrange：访客态 ==========
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        # ========== Act / Assert ==========
        with allure.step("验证八个金刚位链接可见"):
            for name in (
                OkKingkongNavPage.LINK_MARKETPLACE,
                OkKingkongNavPage.LINK_FREE,
                OkKingkongNavPage.LINK_JOBS,
                OkKingkongNavPage.LINK_PROPERTY,
                OkKingkongNavPage.LINK_CARS,
                OkKingkongNavPage.LINK_SERVICES,
                OkKingkongNavPage.LINK_COMMUNITY,
                OkKingkongNavPage.LINK_ALL,
            ):
                expect(kk.kingkong_link(name)).to_be_visible(timeout=15000)
            logger.info("✓ 八个金刚位入口均可见")

        with allure.step("验证首页标题"):
            assert "New York Classified Information Website - OK" in page.title(), page.title()
            logger.info("✓ 首页标题符合预期")

    @pytest.mark.case_id_kingkong_nyc_tc002
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客 Marketplace")
    @allure.title("访客点击金刚位 Marketplace 应进入纽约 Marketplace 导购页")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证访客点击 Marketplace 后 URL、标题、h1 与导航区关键文案")
    def test_tc002_guest_click_marketplace(self, page, config):
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Marketplace"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_MARKETPLACE)
            logger.info("✓ 已点击 Marketplace")

        with allure.step("断言落地页"):
            _wait_url_domcontentloaded(page, "**/cate-marketplace/**", timeout=45000)
            assert "iconSource=marketplace" in page.url or "cate-marketplace" in page.url, page.url
            assert "Marketplace in the New York" in page.title(), page.title()
            assert kk.get_primary_h1_text().strip() == "Marketplace", kk.get_primary_h1_text()
            kk.wait_for_visible_text("Best Match", exact=True, timeout=20000)
            logger.info("✓ Marketplace 落地页校验通过")

    @pytest.mark.case_id_kingkong_nyc_tc003
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 买家 Marketplace")
    @allure.title("买家点击金刚位 Marketplace 行为应与访客一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证已登录买家点击 Marketplace 后 URL、标题与 h1 与访客一致")
    def test_tc003_buyer_click_marketplace(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Marketplace"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_MARKETPLACE)
            logger.info("✓ 已点击 Marketplace")

        with allure.step("断言落地页"):
            _wait_url_domcontentloaded(page, "**/cate-marketplace/**", timeout=45000)
            assert "city-new-york1" in page.url, page.url
            assert "Marketplace in the New York" in page.title(), page.title()
            assert kk.get_primary_h1_text().strip() == "Marketplace", kk.get_primary_h1_text()
            kk.wait_for_visible_text("Best Match", exact=True, timeout=20000)
            logger.info("✓ 买家 Marketplace 与访客一致")

    @pytest.mark.case_id_kingkong_nyc_tc004
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客 Free")
    @allure.title("访客点击金刚位 Free 应进入纽约 Free 列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 0 价筛选 URL 与页面一级标题、Filter 区域")
    def test_tc004_guest_click_free(self, page, config):
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Free"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_FREE)
            logger.info("✓ 已点击 Free")

        with allure.step("断言落地页"):
            _wait_url_domcontentloaded(page, "**/city-new-york1/cate/**", timeout=45000)
            assert "lowestPrice=0" in page.url and "highestPrice=0" in page.url, page.url
            assert "New York Classifieds Website - OK" in page.title(), page.title()
            expect(page.get_by_role("heading", name="All").first).to_be_visible(timeout=15000)
            expect(page.get_by_text("Filter").first).to_be_visible(timeout=15000)
            logger.info("✓ Free 落地页校验通过")

    @pytest.mark.case_id_kingkong_nyc_tc005
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 买家 Free")
    @allure.title("买家点击金刚位 Free 应与访客一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证买家点击 Free 后 URL 与页面关键文案")
    def test_tc005_buyer_click_free(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Free"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_FREE)
            logger.info("✓ 已点击 Free")

        with allure.step("断言落地页"):
            _wait_url_domcontentloaded(page, "**/city-new-york1/cate/**", timeout=45000)
            assert "lowestPrice=0" in page.url and "highestPrice=0" in page.url, page.url
            assert "New York Classifieds Website - OK" in page.title(), page.title()
            expect(page.get_by_role("heading", name="All").first).to_be_visible(timeout=15000)
            expect(page.get_by_text("Filter").first).to_be_visible(timeout=15000)
            logger.info("✓ 买家 Free 与访客一致")

    @pytest.mark.case_id_kingkong_nyc_tc006
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客 Jobs")
    @allure.title("访客点击金刚位 Jobs 应进入纽约职位列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证访客 Jobs 落地为纽约列表：URL 含 city-new-york1，标题含 New York")
    def test_tc006_guest_click_jobs(self, page, config):
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Jobs"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_JOBS)
            expect(page).to_have_url(re.compile(r"cate-jobs"), timeout=30000)
            if "city-new-york1" not in page.url:
                logger.info("Jobs 首次未含 city-new-york1，自首页重试一次")
                kk.goto_nyc_home(config["base_url"])
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                kk.click_kingkong_link(OkKingkongNavPage.LINK_JOBS)
                expect(page).to_have_url(re.compile(r"cate-jobs"), timeout=30000)
            logger.info("✓ 已点击 Jobs")

        with allure.step("断言纽约职位列表"):
            assert "city-new-york1" in page.url, page.url
            assert "iconSource=jobs" in page.url, page.url
            assert re.search(r"\d+K\+ Jobs in the New York", page.title()), page.title()
            assert "Jobs in the US" not in page.title(), page.title()
            home_href = kk.get_nav_home_href()
            assert home_href.rstrip("/") == "https://us.ok.com/en/city-new-york1", home_href
            assert kk.get_primary_h1_text().strip() == "Jobs", kk.get_primary_h1_text()
            assert kk.is_top_search_visible(), "应可见顶栏搜索框"
            logger.info("✓ 访客 Jobs 落地为纽约列表")

    @pytest.mark.case_id_kingkong_nyc_tc007
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 买家 Jobs")
    @allure.title("买家点击金刚位 Jobs 应进入全美职位列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证买家 Jobs 落地为全美列表：URL 不含 city-new-york1，Home 指向站点根")
    def test_tc007_buyer_click_jobs(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Jobs"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_JOBS)
            logger.info("✓ 已点击 Jobs")

        with allure.step("断言全美职位列表"):
            page.wait_for_url("**/cate-jobs/**", timeout=20000)
            assert "city-new-york1" not in page.url, page.url
            assert re.search(r"/en/city/cate-jobs", page.url), page.url
            assert "iconSource=jobs" in page.url, page.url
            assert re.search(r"\d+K\+ Jobs in the US", page.title()), page.title()
            home_href = kk.get_nav_home_href()
            assert home_href.rstrip("/") == "https://us.ok.com/en", home_href
            assert kk.get_primary_h1_text().strip() == "Jobs", kk.get_primary_h1_text()
            logger.info("✓ 买家 Jobs 落地为全美列表")

    @pytest.mark.case_id_kingkong_nyc_tc008
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客 Property")
    @allure.title("访客点击金刚位 Property 应进入纽约房产 For Sale 列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 Property 导购 URL、标题与 For Sale h1")
    def test_tc008_guest_click_property(self, page, config):
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Property"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_PROPERTY)
            logger.info("✓ 已点击 Property")

        with allure.step("断言落地页"):
            page.wait_for_url("**/cate-property/**", timeout=20000)
            assert "iconSource=buy" in page.url, page.url
            assert re.search(r"For Sale in New York", page.title()), page.title()
            assert kk.get_primary_h1_text().strip() == "For Sale", kk.get_primary_h1_text()
            logger.info("✓ Property 落地页校验通过")

    @pytest.mark.case_id_kingkong_nyc_tc009
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 买家 Property")
    @allure.title("买家点击金刚位 Property 应与访客一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证买家 Property 落地与访客一致")
    def test_tc009_buyer_click_property(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Property"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_PROPERTY)
            logger.info("✓ 已点击 Property")

        with allure.step("断言落地页"):
            page.wait_for_url("**/cate-property/**", timeout=20000)
            assert "iconSource=buy" in page.url, page.url
            assert re.search(r"For Sale in New York", page.title()), page.title()
            assert kk.get_primary_h1_text().strip() == "For Sale", kk.get_primary_h1_text()
            logger.info("✓ 买家 Property 与访客一致")

    @pytest.mark.case_id_kingkong_nyc_tc010
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客 Cars")
    @allure.title("访客点击金刚位 Cars 应进入纽约车辆列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 Cars 列表 URL、标题与 h1")
    def test_tc010_guest_click_cars(self, page, config):
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Cars"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_CARS)
            logger.info("✓ 已点击 Cars")

        with allure.step("断言落地页"):
            page.wait_for_url("**/cate-cars/**", timeout=20000)
            assert "iconSource=cars" in page.url, page.url
            assert re.search(r"Cars in the New York", page.title()), page.title()
            assert kk.get_primary_h1_text().strip() == "Cars", kk.get_primary_h1_text()
            logger.info("✓ Cars 落地页校验通过")

    @pytest.mark.case_id_kingkong_nyc_tc011
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 买家 Cars")
    @allure.title("买家点击金刚位 Cars 应与访客一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证买家 Cars 落地与访客一致")
    def test_tc011_buyer_click_cars(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Cars"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_CARS)
            logger.info("✓ 已点击 Cars")

        with allure.step("断言落地页"):
            page.wait_for_url("**/cate-cars/**", timeout=20000)
            assert "Cars in the New York" in page.title(), page.title()
            assert kk.get_primary_h1_text().strip() == "Cars", kk.get_primary_h1_text()
            logger.info("✓ 买家 Cars 与访客一致")

    @pytest.mark.case_id_kingkong_nyc_tc012
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客 Services")
    @allure.title("访客点击金刚位 Services 应进入纽约服务列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 Services 列表 URL、标题与 h1")
    def test_tc012_guest_click_services(self, page, config):
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Services"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_SERVICES)
            logger.info("✓ 已点击 Services")

        with allure.step("断言落地页"):
            page.wait_for_url("**/cate-services/**", timeout=20000)
            assert "iconSource=services" in page.url, page.url
            assert "New York Services Business Information - OK" in page.title(), page.title()
            assert kk.get_primary_h1_text().strip() == "Services", kk.get_primary_h1_text()
            logger.info("✓ Services 落地页校验通过")

    @pytest.mark.case_id_kingkong_nyc_tc013
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 买家 Services")
    @allure.title("买家点击金刚位 Services 应与访客一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证买家 Services 落地与访客一致")
    def test_tc013_buyer_click_services(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Services"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_SERVICES)
            logger.info("✓ 已点击 Services")

        with allure.step("断言落地页"):
            page.wait_for_url("**/cate-services/**", timeout=20000)
            assert "New York Services Business Information - OK" in page.title(), page.title()
            assert kk.get_primary_h1_text().strip() == "Services", kk.get_primary_h1_text()
            logger.info("✓ 买家 Services 与访客一致")

    @pytest.mark.case_id_kingkong_nyc_tc014
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客 Community")
    @allure.title("访客点击金刚位 Community 应进入纽约社区列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 Community 列表 URL、标题与 h1")
    def test_tc014_guest_click_community(self, page, config):
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Community"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_COMMUNITY)
            logger.info("✓ 已点击 Community")

        with allure.step("断言落地页"):
            page.wait_for_url("**/cate-community/**", timeout=20000)
            assert "iconSource=community" in page.url, page.url
            assert "Community in the New York" in page.title(), page.title()
            assert kk.get_primary_h1_text().strip() == "Community", kk.get_primary_h1_text()
            logger.info("✓ Community 落地页校验通过")

    @pytest.mark.case_id_kingkong_nyc_tc015
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 买家 Community")
    @allure.title("买家点击金刚位 Community 应与访客一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证买家 Community 落地与访客一致")
    def test_tc015_buyer_click_community(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 Community"):
            kk.click_kingkong_link(OkKingkongNavPage.LINK_COMMUNITY)
            logger.info("✓ 已点击 Community")

        with allure.step("断言落地页"):
            page.wait_for_url("**/cate-community/**", timeout=20000)
            assert "Community in the New York" in page.title(), page.title()
            assert kk.get_primary_h1_text().strip() == "Community", kk.get_primary_h1_text()
            logger.info("✓ 买家 Community 与访客一致")

    @pytest.mark.case_id_kingkong_nyc_tc016
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 访客 All")
    @allure.title("访客点击金刚位 All 应进入纽约全部分类页")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 listpage URL 与大类入口文案")
    def test_tc016_guest_click_all(self, page, config):
        _ensure_guest_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 All"):
            kk.click_kingkong_all_expect_navigation()
            logger.info("✓ 已点击 All 并完成导航")

        with allure.step("断言落地页"):
            expect(page).to_have_url(re.compile(r"listpage"), timeout=10000)
            assert "city-new-york1" in page.url, page.url
            assert "New York Classified Information Website - OK" in page.title(), page.title()
            root = kk.listpage_content_root()
            expect(root).to_be_visible(timeout=15000)
            kk.wait_listpage_href_link_visible("cate-marketplace", timeout=20000)
            kk.wait_listpage_href_link_visible("cate-jobs", timeout=20000)
            kk.wait_for_visible_text("Collectibles & Art", exact=False, timeout=15000)
            logger.info("✓ All 分类聚合页校验通过")

    @pytest.mark.case_id_kingkong_nyc_tc017
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页金刚位 - 买家 All")
    @allure.title("买家点击金刚位 All 应与访客一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证买家 All 分类聚合页与访客一致")
    def test_tc017_buyer_click_all(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        kk = OkKingkongNavPage(page)

        with allure.step("点击 All"):
            kk.click_kingkong_all_expect_navigation()
            logger.info("✓ 已点击 All 并完成导航")

        with allure.step("断言落地页"):
            expect(page).to_have_url(re.compile(r"listpage"), timeout=10000)
            assert "city-new-york1" in page.url, page.url
            assert "New York Classified Information Website - OK" in page.title(), page.title()
            root = kk.listpage_content_root()
            expect(root).to_be_visible(timeout=15000)
            kk.wait_listpage_href_link_visible("cate-marketplace", timeout=20000)
            kk.wait_listpage_href_link_visible("cate-jobs", timeout=20000)
            logger.info("✓ 买家 All 与访客一致")
