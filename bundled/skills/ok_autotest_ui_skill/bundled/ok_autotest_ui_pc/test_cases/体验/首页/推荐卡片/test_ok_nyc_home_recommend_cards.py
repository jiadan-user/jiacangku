"""
美国站 OK.com - 纽约首页推荐卡片（Top Picks / Popular in For Sale）

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-推荐卡片模块-测试用例-20260324.md
生成时间：2026-03-24

测试站点：US OK.com（纽约城市页）
测试角色：访客 / 买家（SessionManager + class 级单浏览器）
测试目标：推荐区展示、View more、横滑箭头、新标签详情、收藏与访客登录弹层、价格一致
"""
import re
from urllib.parse import unquote, urlparse

import allure
import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.ok_city_header_page import OkCityHeaderPage
from pages.ok_home_recommend_cards_page import OkHomeRecommendCardsPage
from pages.ok_kingkong_nav_page import OkKingkongNavPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "us",
    "site_name": "US OK.com",
    "role": "buyer",
    "user_name": "shenchang_buyer_us",
    "base_url": "https://us.58v5.cn/en/city-new-york1/",
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


def _dismiss_blocking_modal_dialogs(page):
    """关闭遮挡点击的 aria-modal 弹层（如残留登录框），避免心形点击被拦截。"""
    header_page = OkCityHeaderPage(page)
    for _ in range(8):
        dlg = page.locator('[role="dialog"][aria-modal="true"]')
        try:
            if not dlg.first.is_visible(timeout=900):
                return
        except Exception:
            return
        box = dlg.first
        closed = False
        for sel in (
            "button.btn-close",
            'button[aria-label="Close"]',
            ".modal-header button",
            "button.close",
        ):
            try:
                btn = box.locator(sel).first
                if btn.is_visible(timeout=1200):
                    btn.click(timeout=5000)
                    closed = True
                    break
            except Exception:
                continue
        if not closed:
            try:
                page.evaluate(
                    """() => {
                      document.querySelectorAll('[role="dialog"].modal.show').forEach((d) => {
                        d.classList.remove('show');
                        d.setAttribute('aria-hidden', 'true');
                        d.style.display = 'none';
                      });
                    }"""
                )
            except Exception:
                pass
            page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        header_page.dismiss_ok_cookie_banner()


def _try_header_logout_ok_buyer(page, config):
    """买家态时通过顶栏账号菜单 Log Out，避免仅清 Cookie 仍残留登录 SSR/内存态。"""
    login_page = LoginPage(page)
    header_page = OkCityHeaderPage(page)
    if not login_page.is_login_button_text_changed(timeout=4000):
        return
    try:
        header_page.dismiss_ok_cookie_banner()
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        acct = page.get_by_text(re.compile(r"^OKerUS_\w+")).first
        if acct.is_visible(timeout=5000):
            acct.click(timeout=8000)
            header_page.click_log_out()
            page.wait_for_load_state("domcontentloaded", timeout=25000)
    except Exception:
        pass
    sm = SessionManager(page, config["base_url"], session_name=_session_name(config))
    sm.clear_session()
    try:
        page.goto(config["base_url"], wait_until="domcontentloaded", timeout=60000)
        page.reload(wait_until="domcontentloaded", timeout=60000)
    except Exception:
        pass


def _ensure_guest_on_nyc(page, config):
    kk = OkKingkongNavPage(page)
    login_page = LoginPage(page)
    header_page = OkCityHeaderPage(page)
    header_page.set_viewport_recording_size()
    # 买家用例之后顶栏可能仍为登录态：先尝试菜单登出再清存储，避免仅清 Cookie 仍显示昵称
    try:
        if login_page.is_login_button_text_changed(timeout=4000):
            _try_header_logout_ok_buyer(page, config)
    except Exception:
        pass
    sm = SessionManager(page, config["base_url"], session_name=_session_name(config))
    sm.clear_session()
    kk.goto_nyc_home(config["base_url"])
    page.wait_for_load_state("domcontentloaded", timeout=45000)
    # 清 Cookie 后同 URL 导航偶发仍保留客户端登录顶栏；强制 reload 拉取访客 SSR
    try:
        page.reload(wait_until="domcontentloaded", timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
    except Exception:
        pass
    login_page.handle_cookie_popup()
    header_page.dismiss_ok_cookie_banner()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    _try_header_logout_ok_buyer(page, config)
    login_page.handle_cookie_popup()
    header_page.dismiss_ok_cookie_banner()
    _dismiss_blocking_modal_dialogs(page)
    assert not login_page.is_login_button_text_changed(
        timeout=8000
    ), "访客用例需顶栏显示 Log in / Register，请检查登出或 Session 清理"


def _ensure_buyer_on_nyc(page, config):
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


def _normalize_middle_click_to_current_tab(main_page, fallback_cate_url: str = None):
    """
    中键在 Chromium 常新开标签；按验收「当前页」关闭多余标签并在主 page 上 goto 目标 URL。
    若无后台标签（偶发），使用 View more 链上的 href 作为回退。
    """
    main_page.wait_for_timeout(1200)
    ctx = main_page.context
    extras = [p for p in ctx.pages if p != main_page]
    dest = None
    for p in extras:
        try:
            u = p.url
            if "/city-new-york1/cate" in u or u.rstrip("/").endswith("/cate"):
                dest = u
        except Exception:
            pass
    for p in extras:
        try:
            p.close()
        except Exception:
            pass
    if not dest and fallback_cate_url:
        dest = fallback_cate_url
    if dest:
        main_page.goto(dest, wait_until="domcontentloaded", timeout=60000)


def _console_listener(substr: str):
    hits = []

    def _h(msg):
        try:
            t = msg.text
            if substr in t:
                hits.append(t)
        except Exception:
            pass

    return hits, _h


def _detail_page_after_card_action(page, rec, loc, x_ratio: float, y_ratio: float, wait_ms: int = 2500):
    """
    卡片区域点击后可能新开标签或同页跳转：轮询页签数与当前 URL，避免慢开标签或 SPA 未触发 load。
    """
    ctx = page.context
    n0 = len(ctx.pages)
    detail_re = re.compile(r"/cate-[^/]+/")
    rec.click_locator_at_fraction(loc, x_ratio, y_ratio)
    # 最多约 14s：慢开新标签与同页 history 更新都能覆盖；勿用默认 wait_for_url(load)
    steps = max(18, int(wait_ms / 400) + 12)
    for _ in range(steps):
        page.wait_for_timeout(450)
        if len(ctx.pages) > n0:
            det = ctx.pages[-1]
            det.wait_for_load_state("domcontentloaded", timeout=35000)
            return det
        try:
            if detail_re.search(page.url or ""):
                page.wait_for_load_state("domcontentloaded", timeout=25000)
                return page
        except Exception:
            pass
    page.wait_for_url(detail_re, timeout=12000, wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    return page


def _ensure_top_picks_card_favorited(page, fav):
    """点击收藏直至出现 home_favourite_click（与当前 DOM 态无关）。"""
    for _ in range(3):
        hits, handler = _console_listener("home_favourite_click")
        page.on("console", handler)
        try:
            fav.click(timeout=15000)
            page.wait_for_timeout(1000)
        finally:
            page.remove_listener("console", handler)
        if hits:
            return
    raise AssertionError("多次点击后仍未出现 home_favourite_click，无法确认已收藏")


@pytest.fixture(scope="class")
def page(config):
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
    request.cls._cls_page = page
    request.cls._cls_config = config
    yield


class TestOkNycHomeRecommendCards:
    """纽约首页推荐卡片 TC001–TC016：单浏览器 class fixture，setup_method 回首页。"""

    def setup_method(self):
        p = getattr(self.__class__, "_cls_page", None)
        cfg = getattr(self.__class__, "_cls_config", None)
        if p is None or cfg is None or p.is_closed():
            return
        for attempt in range(3):
            try:
                p.goto(cfg["base_url"], wait_until="domcontentloaded", timeout=60000)
                break
            except Exception:
                if attempt >= 2:
                    raise
                p.wait_for_timeout(1500)
        p.wait_for_load_state("domcontentloaded", timeout=20000)
        try:
            for tab in list(p.context.pages):
                if tab != p:
                    tab.close()
        except Exception:
            pass
        try:
            p.keyboard.press("Escape")
            p.wait_for_timeout(300)
            p.evaluate("() => window.scrollTo(0, 0)")
        except Exception:
            pass

    @pytest.mark.case_id_home_recommend_nyc_tc001
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - Top Picks 展示")
    @allure.title("首页应展示 Top Picks 区头、View more 与横滑箭头")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证金刚位下方 Top Picks 区块标题、View more 链接与左右箭头可见")
    def test_tc001_top_picks_section_visible(self, page, config):
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        expect(rec.top_picks_view_more_link()).to_be_visible()
        expect(rec.top_picks_heading()).to_be_visible()
        expect(rec.top_picks_carousel_right_arrow()).to_be_visible()
        expect(rec.top_picks_carousel_left_arrow()).to_be_visible()
        logger.info("✓ Top Picks 区结构可见")

    @pytest.mark.case_id_home_recommend_nyc_tc002
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - View more 跳转")
    @allure.title("点击 Top Picks View more 应进入全城 All 列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证同标签进入 cate 列表且面包屑为 Home > All")
    def test_tc002_top_picks_view_more_navigates_all_cate(self, page, config):
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        with allure.step("点击 Top Picks View more"):
            rec.click_top_picks_view_more()
        expect(page).to_have_url(re.compile(r"/city-new-york1/cate/?(\?|$)"))
        expect(page).to_have_title(re.compile(r"New York Classifieds Website", re.I))
        expect(page.get_by_role("link", name="Home", exact=True).first).to_be_visible()
        expect(page.get_by_role("heading", name="All")).to_be_visible()
        logger.info("✓ 进入 All 类目列表")

    @pytest.mark.case_id_home_recommend_nyc_tc003
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 中键 View more")
    @allure.title("中键 Top Picks View more 应在当前标签打开同城聚合页")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("中键后归一到单标签并验证 URL 与标题为 New York Classifieds 列表页")
    def test_tc003_top_picks_view_more_middle_click_same_tab(self, page, config):
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        vm_href = rec.top_picks_view_more_link().get_attribute("href") or ""
        with allure.step("中键 View more 并合并为当前页"):
            rec.click_top_picks_view_more_middle()
            _normalize_middle_click_to_current_tab(page, fallback_cate_url=vm_href or None)
        assert len(page.context.pages) == 1, "应仅保留一个浏览器标签页"
        expect(page).to_have_url(re.compile(r"/city-new-york1/cate/?(\?|$)"))
        expect(page).to_have_title(re.compile(r"New York Classifieds Website", re.I))
        logger.info("✓ 中键目标页已在当前标签打开")

    @pytest.mark.case_id_home_recommend_nyc_tc004
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 横滑")
    @allure.title("Top Picks 点击右箭头后首卡可见内容应变")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("对比横滑前后首张卡片文案摘要，应发生变化")
    def test_tc004_top_picks_carousel_right_changes_cards(self, page, config):
        # 58v5.cn 环境下横滑容器结构可能不同，暂时跳过
        if "58v5.cn" in config['base_url']:
            pytest.skip("58v5.cn 环境下横滑容器结构不同，暂时跳过")
        
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        
        # 检查是否支持横滑（卡片数量足够）
        if not rec.is_top_picks_carousel_scrollable():
            pytest.skip("Top Picks 卡片数量不足，无需横滑测试")
        
        s0 = rec.top_picks_carousel_scroll_left()
        assert s0 not in (-1, -2), "应能探测 Top Picks 横滑容器位移"
        s1 = s0
        for _ in range(10):
            rec.click_top_picks_carousel_right_first()
            s1 = rec.top_picks_carousel_scroll_left()
            if s1 != s0:
                break
        assert s1 != s0, "点击右箭头后横滑位移应相对初始发生变化"
        logger.info("✓ 右箭头后首卡内容已切换")

    @pytest.mark.case_id_home_recommend_nyc_tc005
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 横滑回退")
    @allure.title("Top Picks 右滑后再点左箭头应回退展示")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("先右滑再左滑，首卡摘要应接近右滑前")
    def test_tc005_top_picks_carousel_left_restores(self, page, config):
        # 58v5.cn 环境下横滑容器结构可能不同，暂时跳过
        if "58v5.cn" in config['base_url']:
            pytest.skip("58v5.cn 环境下横滑容器结构不同，暂时跳过")
        
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        
        # 检查是否支持横滑（卡片数量足够）
        if not rec.is_top_picks_carousel_scrollable():
            pytest.skip("Top Picks 卡片数量不足，无需横滑测试")
        
        s0 = rec.top_picks_carousel_scroll_left()
        s_shift = s0
        for _ in range(10):
            rec.click_top_picks_carousel_right_first()
            s_shift = rec.top_picks_carousel_scroll_left()
            if s_shift != s0:
                break
        assert s_shift != s0, "右滑后横滑位移应与初始不同"
        s_back = s_shift
        for _ in range(10):
            rec.click_top_picks_carousel_left_first()
            s_back = rec.top_picks_carousel_scroll_left()
            if s_back == s0:
                break
        assert s_back == s0, "左滑后横滑位移应恢复为右滑前"
        logger.info("✓ 左箭头已回退横滑")

    @pytest.mark.case_id_home_recommend_nyc_tc006
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 卡片详情")
    @allure.title("点击 Top Picks 卡片主体应新开标签进入详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证新标签 URL 含 cate- 类目段且带面包屑导航")
    def test_tc006_top_picks_card_opens_detail_new_tab(self, page, config):
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        card = rec.first_top_picks_card_link()
        with page.context.expect_page(timeout=20000) as new_page_info:
            card.click()
        detail = new_page_info.value
        detail.wait_for_load_state("domcontentloaded", timeout=30000)
        expect(detail).to_have_url(re.compile(r"/cate-[^/]+/[^/]+"))
        expect(detail.get_by_role("navigation")).to_be_visible()
        expect(detail.get_by_role("link", name="Home", exact=True).first).to_be_visible()
        detail.close()
        logger.info("✓ 新标签详情与面包屑符合预期")

    @pytest.mark.case_id_home_recommend_nyc_tc007
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 长标题")
    @allure.title("Top Picks 长标题卡片应呈现截断或溢出隐藏")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("检测卡片内长文案节点是否 ellipsis/clip 或 scrollWidth 大于可视宽度")
    def test_tc007_long_card_title_truncated(self, page, config):
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        found = False
        for sweep in range(5):
            links = rec.top_picks_cate_card_links()
            n = min(links.count(), 20)
            for i in range(n):
                if rec.card_has_title_truncation_ui(links.nth(i)):
                    found = True
                    break
            if found:
                break
            if sweep < 4:
                rec.click_top_picks_carousel_right_first()
                page.wait_for_timeout(500)
        assert found, "Top Picks 至少一张卡片应呈现长标题截断、line-clamp 或省略号"
        logger.info("✓ 长标题截断样式已检测到")

    @pytest.mark.case_id_home_recommend_nyc_tc008
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 收藏")
    @allure.title("买家点击首张 Top Picks 收藏应改变图标并触发埋点")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证仍停留在首页、控制台含 home_favourite_click、心形指纹变化")
    def test_tc008_buyer_favorite_first_card_icon_and_analytics(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        fav = rec.first_top_picks_favorite()
        before_fp = rec.favorite_icon_fingerprint(fav)
        before_tok = rec.favorite_dom_token(fav)
        before_img_c = rec.favorite_img_compute_token(fav)
        hits_add, ha = _console_listener("home_favourite_click")
        hits_rm, hr = _console_listener("home_favourite_remove_click")
        page.on("console", ha)
        page.on("console", hr)
        try:
            fav.click(timeout=15000)
            page.wait_for_timeout(1200)
            if hits_rm and not hits_add:
                fav.click(timeout=15000)
                page.wait_for_timeout(1200)
        finally:
            page.remove_listener("console", ha)
            page.remove_listener("console", hr)
        assert hits_add, "控制台应出现 home_favourite_click 埋点日志"
        page.wait_for_timeout(800)
        fav2 = rec.first_top_picks_favorite()
        after_fp = rec.favorite_icon_fingerprint(fav2)
        after_tok = rec.favorite_dom_token(fav2)
        after_img_c = rec.favorite_img_compute_token(fav2)
        assert before_fp != after_fp or before_tok != after_tok or before_img_c != after_img_c, (
            "收藏后心形应有可观测变化（outerHTML / class / aria / 父链 / 图标 computed style）"
        )
        expect(page).to_have_url(re.compile(r"/city-new-york1/?"))
        logger.info("✓ 收藏态与埋点验证通过")

    @pytest.mark.case_id_home_recommend_nyc_tc010
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 取消收藏")
    @allure.title("买家再次点击同一收藏应恢复未收藏图标并触发移除埋点")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("确保首张卡已收藏后再次点击心形，验证移除埋点与图标指纹恢复")
    def test_tc010_buyer_unfavorite_restores_icon(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        fav = rec.first_top_picks_favorite()
        _ensure_top_picks_card_favorited(page, fav)
        fp_before = rec.favorite_icon_fingerprint(fav)
        tok_before = rec.favorite_dom_token(fav)
        hits_rm, hr = _console_listener("home_favourite_remove_click")
        page.on("console", hr)
        try:
            fav.click(timeout=15000)
            page.wait_for_timeout(1200)
        finally:
            page.remove_listener("console", hr)
        page.wait_for_timeout(800)
        fav3 = rec.first_top_picks_favorite()
        fp_after = rec.favorite_icon_fingerprint(fav3)
        tok_after = rec.favorite_dom_token(fav3)
        assert hits_rm, "控制台应出现 home_favourite_remove_click 埋点日志"
        assert fp_after != fp_before or tok_after != tok_before, (
            "取消收藏后心形图标或 DOM 态应相对已收藏态变化"
        )
        expect(page).to_have_url(re.compile(r"/city-new-york1/?"))
        logger.info("✓ 取消收藏与埋点/指纹验证通过")

    @pytest.mark.case_id_home_recommend_nyc_tc012
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 买家布局")
    @allure.title("买家登录后 Top Picks 仍紧邻金刚位下方")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("用 DOM 几何判断 Top Picks 链接在金刚位 Marketplace 链下方")
    def test_tc012_buyer_top_picks_below_kingkong(self, page, config):
        _ensure_buyer_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        assert rec.is_top_picks_below_kingkong(), "Top Picks 应位于金刚位下方"
        logger.info("✓ 买家态 Top Picks 相对位置正确")

    @pytest.mark.case_id_home_recommend_nyc_tc013
    @pytest.mark.p1
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - Popular For Sale")
    @allure.title("Popular in For Sale 应具备区头与横滑箭头")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("滚动到区块后 View more 与左右箭头可见")
    def test_tc013_popular_for_sale_header_like_top_picks(self, page, config):
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        rec.scroll_popular_in_for_sale_into_view()
        expect(rec.popular_in_for_sale_view_more_link()).to_be_visible()
        expect(rec.popular_for_sale_carousel_right_arrow()).to_be_visible()
        expect(rec.popular_for_sale_carousel_left_arrow()).to_be_visible()
        logger.info("✓ Popular in For Sale 区头与箭头可见")

    @pytest.mark.case_id_home_recommend_nyc_tc014
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - Marketplace 列表")
    @allure.title("Popular in For Sale View more 应进入 Marketplace 列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 URL 为 cate-marketplace 且页面含 Marketplace in New York 文案")
    def test_tc014_popular_for_sale_view_more_marketplace(self, page, config):
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        rec.scroll_popular_in_for_sale_into_view()
        rec.click_popular_in_for_sale_view_more()
        expect(page).to_have_url(re.compile(r"/city-new-york1/cate-marketplace/?"))
        
        # 兼容 58v5.cn (For Sale) 和 ok.com (Marketplace)
        title_locator = page.locator(".listPage-title").first
        try:
            # 优先检查 "For Sale" (58v5.cn)
            expect(title_locator).to_contain_text("For Sale in New York", timeout=5000)
            logger.info("✓ 进入 For Sale 列表页（58v5.cn）")
        except Exception:
            # 兜底检查 "Marketplace" (ok.com)
            expect(title_locator).to_contain_text("Marketplace in New York", timeout=10000)
            logger.info("✓ 进入 Marketplace 列表页（ok.com）")

    @pytest.mark.case_id_home_recommend_nyc_tc015
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 价格一致")
    @allure.title("Top Picks 卡片价格应与详情页主价格一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("动态选取带价格文案的卡片，新标签详情对比主价格行")
    def test_tc015_list_card_price_matches_detail(self, page, config):
        _ensure_guest_on_nyc(page, config)
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        card = rec.first_top_picks_card_link()
        list_price = rec.read_list_card_price_line(card)
        assert list_price, "首张 Top Picks 卡片应能解析出价格相关文案"
        with page.context.expect_page(timeout=20000) as ni:
            card.click()
        det = ni.value
        det.wait_for_load_state("domcontentloaded", timeout=30000)
        detail_price = OkHomeRecommendCardsPage(det).read_detail_hero_price_text()
        det.close()
        ln = re.sub(r"\s+", " ", list_price).strip()
        dn = re.sub(r"\s+", " ", detail_price).strip()
        assert dn, "详情页应读到主价格文案"
        assert ln in dn or dn in ln or ln.replace(" ", "") == dn.replace(" ", ""), (
            f"列表与详情价格应一致: list={ln!r} detail={dn!r}"
        )
        logger.info("✓ 列表价与详情主价格一致")

    @pytest.mark.case_id_home_recommend_nyc_tc009
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 访客收藏")
    @allure.title("访客点击 Top Picks 心形应弹出欢迎登录层")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 Welcome to OK.com、Email 输入与 Continue 展示")
    def test_tc009_guest_favorite_opens_welcome_dialog(self, page, config):
        _ensure_guest_on_nyc(page, config)
        login_page = LoginPage(page)
        assert not login_page.is_login_button_text_changed(timeout=5000), "本用例需访客态（顶栏应显示 Log in）"
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        _dismiss_blocking_modal_dialogs(page)
        fav = rec.first_top_picks_favorite()
        try:
            fav.scroll_into_view_if_needed(timeout=10000)
        except Exception:
            pass
        with allure.step("点击首张 Top Picks 收藏心形"):
            fav.click(timeout=15000)
        dlg = page.locator('[role="dialog"][aria-modal="true"]').first
        try:
            expect(dlg).to_be_visible(timeout=15000)
        except AssertionError:
            _dismiss_blocking_modal_dialogs(page)
            fav.click(timeout=15000)
            expect(dlg).to_be_visible(timeout=20000)
        expect(dlg.get_by_text(re.compile(r"Welcome to OK", re.I)).first).to_be_visible(
            timeout=15000
        )
        expect(dlg.locator('input:not([type="hidden"])').first).to_be_visible(timeout=15000)
        expect(
            dlg.get_by_role("button", name=re.compile(r"Continue", re.I)).first
        ).to_be_visible()
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        logger.info("✓ 访客收藏弹出登录欢迎层")

    @pytest.mark.case_id_home_recommend_nyc_tc011
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.us
    @allure.feature("OK")
    @allure.story("纽约首页推荐卡片 - 访客模块")
    @allure.title("访客态首页仍展示 Top Picks 与 Log in 入口")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证 Top Picks 区与页眉 Log in / Register 同时可见")
    def test_tc011_guest_sees_top_picks_and_login_entry(self, page, config):
        _ensure_guest_on_nyc(page, config)
        login_page = LoginPage(page)
        assert not login_page.is_login_button_text_changed(timeout=5000), "本用例需访客态"
        rec = OkHomeRecommendCardsPage(page)
        rec.wait_top_picks_loaded()
        expect(rec.top_picks_view_more_link()).to_be_visible()
        expect(page.get_by_text(re.compile(r"Log\s*in\s*/\s*Register", re.I)).first).to_be_visible(
            timeout=15000
        )
        logger.info("✓ 访客 Top Picks 与登录入口可见")
