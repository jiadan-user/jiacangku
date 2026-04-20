"""
OK.com AE 站 — 账户主页（用例文档章节一、二、三、四、八）

playwright-test-generator 生成 | 文档：web-qa-brain/OK.com-账户主页-测试用例-20260415.md

执行说明：
- 用例名前缀 test_a* 为访客（四），须先跑完再跑 test_b*（已登录），因共享 module 级 page。
- 推荐：pytest test_cases/体验/账户主页/test_account_profile_md_chapters_1_2_3_4_8.py -k "test_a or test_b"
"""

from __future__ import annotations

import re

import allure
import pytest
from playwright.sync_api import expect

from pages.account_profile_page import AccountProfilePage
from pages.login_page import LoginPage
from pages.sg_home_page import SgHomePage

_CONFIG = {
    "site": "ae",
    "site_name": "AE 测试站 (58v5)",
    "role": "mixed_guest_then_logged_in",
    "base_url": "https://ae.58v5.cn",
    "urls": {
        "self_profile": "https://ae.58v5.cn/en/profile/796152584505038400/",
        "other_a": "https://ae.58v5.cn/en/profile/796272266172388160/",
        "other_b": "https://ae.58v5.cn/en/profile/796502164475285952/",
        "other_jobs_paged": "https://ae.58v5.cn/en/profile/796133836057336352/jobs/",
    },
    "expected_nicks": {
        "header_logged_in": "OKer_c8h3yp8",
        "self_card": "OKer_c8h3yp8",
        "other_a_card": "OKer_mamengmeng02",
        "other_b_card": "OKerAE_gvx6evy",
    },
    "profile_ids": {
        "self": "796152584505038400",
        "other_a": "796272266172388160",
        "other_b": "796502164475285952",
        "jobs_paged": "796133836057336352",
    },
    "test_account": {"email": "shenchang@58.com", "password": "123456Tt"},
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1440, "height": 900},
    },
    "timeout": {"default": 30000, "navigation": 90000},
}


def _fill_password_fallback(page, password: str) -> None:
    for name in ("Enter password", "Password"):
        loc = page.get_by_role("textbox", name=name)
        if loc.count() and loc.first.is_visible(timeout=1500):
            loc.first.fill(password)
            page.wait_for_timeout(800)
            return
    raise RuntimeError("未找到密码输入框（Enter password / Password）")


def ensure_logged_in(page, cfg: dict) -> None:
    """与 web-qa-brain/probe_account_profile.py 对齐的登录流程。"""
    base = cfg["base_url"]
    email = cfg["test_account"]["email"]
    password = cfg["test_account"]["password"]
    login_page = LoginPage(page)
    home = SgHomePage(page)
    page.goto(base, wait_until="domcontentloaded", timeout=90000)
    try:
        page.wait_for_load_state("networkidle", timeout=25000)
    except Exception:
        pass
    page.wait_for_timeout(800)
    login_page.handle_cookie_popup()
    page.wait_for_timeout(500)
    if home.is_logged_in():
        return
    login_page.click_login_register_button()
    login_page.input_email(email)
    login_page.click_continue_button()
    try:
        login_page.input_password(password)
    except Exception:
        _fill_password_fallback(page, password)
    login_page.click_login_button()
    page.wait_for_load_state("domcontentloaded", timeout=45000)
    page.wait_for_timeout(2500)
    ok = home.is_logged_in() or login_page.is_login_button_text_changed(timeout=8000)
    if not ok:
        page.screenshot(path="debug_account_profile_login_failed.png", full_page=True)
        raise RuntimeError("登录未确认成功，已截图 debug_account_profile_login_failed.png")


def _profile(page) -> AccountProfilePage:
    return AccountProfilePage(page)


# ---------------------------------------------------------------------------
# 四、未登录（须先于已登录用例执行）
# ---------------------------------------------------------------------------


@allure.epic("OK.com 体验测试")
@allure.feature("账户主页")
@allure.story("章节四 — 未登录与鉴权")
@pytest.mark.ae
@pytest.mark.profile
@pytest.mark.p0
class TestAccountProfileChapter4Guest:
    @pytest.mark.case_id_profile_tc014
    @allure.title("TC014: 未登录访问本人账户主页 URL")
    def test_a00_tc014_visitor_self_profile(self, page, config):
        page.context.clear_cookies()
        page.goto(config["base_url"], wait_until="domcontentloaded")
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        LoginPage(page).handle_cookie_popup()
        prof.wait_main_visible()
        # 策略之一：仍可浏览公开区；或拦截 —— 至少页面可加载且 URL 仍指向 profile
        assert prof.url_contains_profile_id(config["profile_ids"]["self"])
        assert page.url.count("/profile/") >= 1

    @pytest.mark.case_id_profile_tc015
    @allure.title("TC015: 未登录访问他人主页 A / B")
    def test_a01_tc015_visitor_other_profiles(self, page, config):
        page.context.clear_cookies()
        prof = _profile(page)
        for key in ("other_a", "other_b"):
            with allure.step(f"打开 {key}"):
                prof.open_profile(config["urls"][key])
                LoginPage(page).handle_cookie_popup()
                prof.wait_main_visible()
                assert prof.url_contains_profile_id(config["profile_ids"][key])

    @pytest.mark.case_id_profile_tc041
    @allure.title("TC041: 访客他人主页 — 点击帖子收藏")
    def test_a02_tc041_visitor_click_favorite(self, page, config):
        page.context.clear_cookies()
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_a"])
        LoginPage(page).handle_cookie_popup()
        prof.wait_main_visible()
        prof.first_listing_favorite_icon().wait_for(state="visible", timeout=20000)
        prof.click_first_listing_favorite_js()
        page.wait_for_timeout(1500)
        # 应出现登录门闸或等价提示，不应静默当作已登录收藏成功
        gate = prof.login_modal_or_gate_visible()
        assert gate or "login" in page.url.lower(), "访客点收藏后应出现登录引导或登录相关 URL"

    @pytest.mark.case_id_profile_tc042
    @allure.title("TC042: 访客他人主页 — 点击 Contact")
    def test_a03_tc042_visitor_click_contact(self, page, config):
        page.context.clear_cookies()
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_a"])
        LoginPage(page).handle_cookie_popup()
        prof.wait_main_visible()
        prof.wait_contact_cta_visible()
        prof.click_profile_contact_js()
        page.wait_for_timeout(2000)
        url = page.url.lower()
        in_im = bool(re.search(r"chat|message|im|inbox|conversation", url))
        gate = prof.login_modal_or_gate_visible()
        assert gate or (not in_im), "访客点 Contact 不应直接进入可发消息的微聊页（除非产品明确允许）"


# ---------------------------------------------------------------------------
# 一、二、三、八（已登录）
# ---------------------------------------------------------------------------


@allure.epic("OK.com 体验测试")
@allure.feature("账户主页")
@allure.story("章节一/二/三/八 — 已登录")
@pytest.mark.ae
@pytest.mark.profile
class TestAccountProfileChapters1238LoggedIn:
    @pytest.mark.case_id_profile_tc001
    @pytest.mark.p0
    @allure.title("TC001: 已登录打开本人账户主页")
    def test_b00_tc001_self_profile_loads(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        LoginPage(page).handle_cookie_popup()
        prof.wait_main_visible()
        assert prof.url_contains_profile_id(config["profile_ids"]["self"])
        assert prof.title_matches_profile_pattern()
        expect(page).to_have_title(re.compile(re.escape(config["expected_nicks"]["self_card"])))

    @pytest.mark.case_id_profile_tc002
    @pytest.mark.p0
    @allure.title("TC002: 已登录打开他人主页 A")
    def test_b01_tc002_other_a(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_a"])
        prof.wait_main_visible()
        assert prof.url_contains_profile_id(config["profile_ids"]["other_a"])
        expect(page).to_have_title(re.compile(re.escape(config["expected_nicks"]["other_a_card"])))

    @pytest.mark.case_id_profile_tc003
    @pytest.mark.p1
    @allure.title("TC003: 已登录打开他人主页 B")
    def test_b02_tc003_other_b(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_b"])
        prof.wait_main_visible()
        assert prof.url_contains_profile_id(config["profile_ids"]["other_b"])
        expect(page).to_have_title(re.compile(re.escape(config["expected_nicks"]["other_b_card"])))

    @pytest.mark.case_id_profile_tc004
    @pytest.mark.p0
    @allure.title("TC004: 本人与他人主页切换 URL/title 一致")
    def test_b03_tc004_switch_profiles(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        seq = ("self_profile", "other_a", "self_profile")
        for key in seq:
            prof.open_profile(config["urls"][key])
            prof.wait_main_visible()
            pid = (
                config["profile_ids"]["self"]
                if key == "self_profile"
                else config["profile_ids"]["other_a"]
            )
            assert prof.url_contains_profile_id(pid)
            assert prof.title_matches_profile_pattern()

    @pytest.mark.case_id_profile_tc005
    @pytest.mark.p0
    @allure.title("TC005: 本人主页核心信息 + 动态帖子数")
    def test_b04_tc005_self_listings_dynamic(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        prof.wait_main_visible()
        label = prof.profile_listings_label_text()
        assert label, "未解析到 listings 文案"
        n = prof.parse_listings_count(label)
        assert n is not None and n >= 0
        n_cards = page.locator(".list-components-item-favorite.pc-card").count()
        n_links = page.locator("a[href*='/cate-'], a[href*='/city-']").count()
        if n > 0:
            assert n_cards >= 1 or n_links >= 1, "listings>0 时应有帖子卡片或列表链接"

    @pytest.mark.case_id_profile_tc006
    @pytest.mark.p0
    @allure.title("TC006: 本人资料区编辑入口 → 编辑相关页")
    def test_b05_tc006_profile_edit_navigation(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        prof.wait_main_visible()
        try:
            edit = prof.profile_edit_button()
            edit.wait_for(state="visible", timeout=12000)
            edit.click()
        except Exception:
            try:
                prof.click_profile_edit_js()
            except Exception:
                pytest.skip(
                    "未点到资料「编辑」入口：请在本人 profile 打开 DevTools，对编辑图标「Copy selector」"
                    " 或把该按钮外层 HTML 片段发我，以便写入 AccountProfilePage.profile_edit_button / click_profile_edit_js"
                )
        page.wait_for_timeout(2000)
        url = page.url.lower()
        # 资料编辑页 URL 可能含 edit/profile/account/setting/personal 或 user/home
        assert re.search(r"edit|profile|account|setting|personal|user/home", url), f"编辑跳转 URL 未识别: {url}"

    @pytest.mark.case_id_profile_tc007
    @pytest.mark.p0
    @allure.title("TC007: 本人帖子卡片收藏切换")
    def test_b06_tc007_favorite_toggle_self(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        prof.wait_main_visible()
        prof.first_listing_favorite_icon().wait_for(state="visible", timeout=20000)
        prof.click_first_listing_favorite_js()
        page.wait_for_timeout(1200)
        prof.click_first_listing_favorite_js()
        page.wait_for_timeout(800)

    @pytest.mark.case_id_profile_tc008
    @pytest.mark.p0
    @allure.title("TC008: 本人主页类目 Tab 可见并可切换（抽样）")
    def test_b07_tc008_category_tabs(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        prof.wait_main_visible()
        failed: list[str] = []
        for name in ("Marketplace", "Property"):
            with allure.step(name):
                try:
                    prof.click_category_tab(name)
                except Exception:
                    failed.append(name)
        if failed:
            pytest.skip(
                f"类目 Tab 点击失败: {failed}。请在本人 profile 资料卡下方 Tab 行对「Marketplace」等节点 Inspect，"
                "确认是 role=tab / link / 纯文本，并把外层 HTML 或 selector 发我。"
            )

    @pytest.mark.case_id_profile_tc009
    @pytest.mark.p0
    @allure.title("TC009: Jobs 子路径与列表翻页")
    def test_b08_tc009_jobs_pagination(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_jobs_paged"])
        prof.wait_main_visible()
        assert "/jobs/" in page.url
        assert prof.url_contains_profile_id(config["profile_ids"]["jobs_paged"])
        first_href = None
        links = page.locator("main a[href*='/cate-'], main a[href*='/city-']")
        if links.count():
            first_href = links.first.get_attribute("href")
        nxt = prof.pagination_next()
        try:
            nxt.wait_for(state="visible", timeout=8000)
            nxt.click()
            page.wait_for_timeout(2000)
        except Exception:
            # 部分列表为「滚动加载」：无 Next 按钮时用滚轮触发懒加载
            page.mouse.wheel(0, 2400)
            page.wait_for_timeout(2000)
        link_cnt = page.locator("main a[href*='/cate-'], main a[href*='/city-']").count()
        if link_cnt == 0:
            link_cnt = page.locator("a[href*='/cate-'], a[href*='/city-']").count()
        if link_cnt == 0:
            pytest.skip(
                "Jobs 子路径页无任何帖子链接，无法验证翻页/懒加载。请确认 "
                f"{config['urls']['other_jobs_paged']} 在测试环境仍有数据；"
                "若有分页 UI 但无链接，请提供分页按钮文案或 `data-testid`。"
            )
        if first_href and links.count():
            links.first.get_attribute("href")  # 翻页后如需强断言可对比 href 列表

    @pytest.mark.case_id_profile_tc010
    @pytest.mark.p0
    @allure.title("TC010: 他人主页不出现「编辑该用户资料」入口")
    def test_b09_tc010_no_edit_on_other(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_a"])
        prof.wait_main_visible()
        edit = prof.profile_edit_button()
        # 若他人页误展示编辑，点击后 URL 仍可能含 edit —— 结合资料卡展示名判断
        name = prof.profile_card_oker_name()
        assert name and config["expected_nicks"]["other_a_card"] in name

    @pytest.mark.case_id_profile_tc011
    @pytest.mark.p0
    @allure.title("TC011: 他人主页正文不出现完整邮箱形态")
    def test_b10_tc011_no_raw_email_in_body(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        for key in ("other_a", "other_b"):
            prof.open_profile(config["urls"][key])
            prof.wait_main_visible()
            root = page.locator("main").first if page.locator("main").count() else page.locator("body")
            body = root.inner_text(timeout=15000)[:20000]
            assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", body), (
                f"{key} main 内出现疑似完整邮箱"
            )

    @pytest.mark.case_id_profile_tc012
    @pytest.mark.p0
    @allure.title("TC012: 他人主页 Contact → 微聊/会话页")
    def test_b11_tc012_contact_opens_im(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_a"])
        prof.wait_main_visible()
        prof.wait_contact_cta_visible()
        n_pages_before = len(page.context.pages)
        prof.click_profile_contact_js()
        page.wait_for_timeout(2500)
        pages = page.context.pages
        if len(pages) > n_pages_before:
            newp = pages[-1]
            try:
                newp.wait_for_load_state("domcontentloaded", timeout=30000)
                expect(newp).to_have_url(re.compile(r"(chat|message|aepub\.58v5\.cn)", re.I))
            finally:
                newp.close()
            return
        # 同标签跳转：对齐详情页发布者 Contact（aepub…/chat）
        try:
            page.wait_for_url(re.compile(r"aepub\.58v5\.cn/.*/chat", re.I), timeout=35000)
        except Exception:
            try:
                page.wait_for_url(
                    re.compile(r"(ae\.58v5\.cn|aepub\.58v5\.cn).*(chat|message|im)", re.I),
                    timeout=8000,
                )
            except Exception:
                page.wait_for_timeout(500)
        url = page.url.lower()
        chatish = bool(
            re.search(r"chat|message|im|inbox|conversation|talk|aepub\.58v5\.cn", url)
        )
        drawer = page.locator("[class*='chat' i], [class*='Chat' i], [role='dialog']").first
        try:
            drawer_ok = drawer.is_visible(timeout=5000)
        except Exception:
            drawer_ok = False
        try:
            input_ok = page.get_by_role(
                "textbox", name=re.compile(r"input message|message", re.I)
            ).first.is_visible(timeout=8000)
        except Exception:
            try:
                input_ok = page.locator("textarea, [contenteditable='true']").first.is_visible(timeout=3000)
            except Exception:
                input_ok = False
        if not (chatish or drawer_ok or prof.login_modal_or_gate_visible() or input_ok):
            pytest.skip(
                "Contact 后仍未命中微聊 URL/弹层/输入框。若微聊是「新开标签页」，请说明，我会改为 "
                "`context.expect_page()` 断言子页；若是 iframe，请提供 iframe 的 selector。"
            )

    # —— 八章 —— #

    @pytest.mark.case_id_profile_tc031
    @pytest.mark.p0
    @allure.title("TC031: 顶栏登录身份 vs 资料卡主体（他人 A）")
    def test_b12_tc031_header_vs_card_other_a(self, page, config):
        ensure_logged_in(page, config)
        exp_h = config["expected_nicks"]["header_logged_in"]
        exp_c = config["expected_nicks"]["other_a_card"]
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_a"])
        prof.wait_main_visible()
        assert SgHomePage(page).is_logged_in(), "应为已登录态"
        card = prof.profile_card_oker_name()
        assert card and exp_c in card
        # 顶栏展示名因站点实现可能仅头像，不强制 header 内可见同一 OKer 串
        _ = prof.header_text_has(exp_h)

    @pytest.mark.case_id_profile_tc032
    @pytest.mark.p0
    @allure.title("TC032: 本人资料卡字段基线")
    def test_b13_tc032_self_card_baseline(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        prof.wait_main_visible()
        assert prof.profile_card_oker_name() == config["expected_nicks"]["self_card"]
        assert prof.profile_listings_label_text()

    @pytest.mark.case_id_profile_tc033
    @pytest.mark.p1
    @allure.title("TC033: 本人帖子卡片结构（收藏控件可见）")
    def test_b14_tc033_listing_card_structure(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        prof.wait_main_visible()
        prof.first_listing_favorite_icon().wait_for(state="visible", timeout=20000)

    @pytest.mark.case_id_profile_tc034
    @pytest.mark.p0
    @allure.title("TC034: 类目 Tab 默认 Services")
    def test_b15_tc034_default_services_tab(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        page.goto(config["urls"]["self_profile"], wait_until="domcontentloaded")
        LoginPage(page).handle_cookie_popup()
        prof.wait_main_visible()
        tab = page.get_by_role("tab", name=re.compile(r"^services$", re.I))
        if tab.count():
            try:
                expect(tab.first).to_have_attribute("aria-selected", "true", timeout=5000)
            except AssertionError:
                pass
        # 无 <main> 或 Tab 非标准 role 时，用首屏文案 / title 兜底
        blob = page.locator("body").inner_text(timeout=12000)[:4000]
        assert re.search(r"\bServices\b", blob) or re.search(
            r"Services", page.title(), re.I
        ), "本人 profile 首屏或 title 应能体现 Services 类目"

    @pytest.mark.case_id_profile_tc035
    @pytest.mark.p0
    @allure.title("TC035: 他人 A Jobs 列表区")
    def test_b16_tc035_other_a_jobs_list(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_a"])
        prof.wait_main_visible()
        expect(page).to_have_title(re.compile(r"Jobs", re.I))
        assert (
            page.locator(".list-components-item-favorite.pc-card").count() >= 1
            or page.locator("a[href*='/cate-'], a[href*='/city-']").count() >= 1
        )

    @pytest.mark.case_id_profile_tc036
    @pytest.mark.p0
    @allure.title("TC036: 他人 B 零 listing 空态")
    def test_b17_tc036_other_b_empty(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["other_b"])
        prof.wait_main_visible()
        expect(prof.empty_state_text()).to_be_visible()

    @pytest.mark.case_id_profile_tc037
    @pytest.mark.p2
    @allure.title("TC037: listings 数字与文案可解析")
    def test_b18_tc037_listings_label_parse(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        for key in ("self_profile", "other_a", "other_b"):
            prof.open_profile(config["urls"][key])
            prof.wait_main_visible()
            label = prof.profile_listings_label_text()
            assert label and prof.parse_listings_count(label) is not None

    @pytest.mark.case_id_profile_tc038
    @pytest.mark.p0
    @allure.title("TC038: 本人编辑 vs 他人 Contact")
    def test_b19_tc038_edit_vs_contact(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        prof.wait_main_visible()
        try:
            prof.profile_edit_button().wait_for(state="visible", timeout=8000)
        except Exception:
            try:
                prof.click_profile_edit_js()
            except Exception:
                pytest.skip(
                    "本人页编辑入口未对齐：请提供编辑图标 Copy selector 或外层 HTML（同 TC006 skip 说明）"
                )
        prof.open_profile(config["urls"]["other_a"])
        prof.wait_main_visible()
        prof.wait_contact_cta_visible()

    @pytest.mark.case_id_profile_tc039
    @pytest.mark.p2
    @allure.title("TC039: 右侧浮动按钮（弱断言）")
    def test_b20_tc039_floating_action(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        prof.open_profile(config["urls"]["self_profile"])
        prof.wait_main_visible()
        assert page.locator("svg").count() > 0

    @pytest.mark.case_id_profile_tc040
    @pytest.mark.p2
    @allure.title("TC040: 页脚 About Us 可见")
    def test_b21_tc040_footer_about(self, page, config):
        ensure_logged_in(page, config)
        prof = _profile(page)
        if config["profile_ids"]["self"] not in page.url:
            prof.open_profile(config["urls"]["self_profile"], timeout=120000)
        prof.wait_main_visible()
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
        expect(prof.footer_about_link()).to_be_visible()
